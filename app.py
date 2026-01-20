from flask import Flask, render_template, request, jsonify
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re
import os
import hashlib
import requests
from functools import lru_cache

# Initialize Flask app
app = Flask(__name__)

# ============================================================================
# OMDb API Configuration (for movie posters)
# ============================================================================

OMDB_API_KEY = "3294bca1"
OMDB_API_URL = "http://www.omdbapi.com/"

# ============================================================================
# Movie Recommendation Engine
# ============================================================================

class MovieRecommender:
    def __init__(self, csv_path='tmdb_movies_processed.csv'):
        self.df = None
        self.tfidf_matrix = None
        self.tfidf_vectorizer = None
        self.is_loaded = False
        self.error_message = None
        self.poster_cache = {}
        self.load_data(csv_path)
    
    def load_data(self, csv_path):
        """Load and preprocess movie data"""
        try:
            # Try files in order of preference (TMDB processed first)
            files_to_try = [
                'tmdb_movies_processed.csv',  # Best - has real movie data
                csv_path,
                'movies_with_posters.csv', 
                'movies_enhanced.csv', 
                'movies.csv'
            ]
            
            loaded = False
            for file_path in files_to_try:
                if os.path.exists(file_path):
                    self.df = pd.read_csv(file_path)
                    print(f"📂 Loading from: {file_path}")
                    loaded = True
                    break
            
            if not loaded:
                raise FileNotFoundError("No movie dataset found")
            
            # Validate required columns
            required_cols = {'movieId', 'title', 'genres'}
            if not required_cols.issubset(self.df.columns):
                raise ValueError(f"CSV must contain columns: {required_cols}")
            
            # Clean the data
            self.df = self.df.dropna(subset=['title', 'genres'])
            self.df = self.df.drop_duplicates(subset=['title'])
            self.df = self.df.reset_index(drop=True)
            
            # Ensure all required columns exist
            self._ensure_columns()
            
            # Process genres for TF-IDF
            self.df['genres_processed'] = self.df['genres'].str.replace('|', ' ', regex=False)
            self.df['genres_processed'] = self.df['genres_processed'].str.replace('(no genres listed)', '', regex=False)
            
            # Create genre list for display
            self.df['genre_list'] = self.df['genres'].apply(
                lambda x: [g.strip() for g in str(x).split('|') if g and g != '(no genres listed)']
            )
            
            # Build TF-IDF matrix on genres
            self.tfidf_vectorizer = TfidfVectorizer(stop_words='english', ngram_range=(1, 2))
            self.tfidf_matrix = self.tfidf_vectorizer.fit_transform(self.df['genres_processed'])
            
            self.is_loaded = True
            print(f"✓ Loaded {len(self.df)} movies successfully")
            
        except FileNotFoundError as e:
            self.error_message = str(e)
            print(self.error_message)
        except Exception as e:
            self.error_message = f"Error loading data: {str(e)}"
            print(self.error_message)
    
    def _enhance_basic_dataset(self):
        """Add missing columns to basic dataset"""
        import random
        random.seed(42)
        
        if 'year' not in self.df.columns:
            self.df['year'] = self.df['title'].apply(self._extract_year)
        if 'clean_title' not in self.df.columns:
            self.df['clean_title'] = self.df['title'].apply(self._clean_title)
        if 'rating' not in self.df.columns:
            self.df['rating'] = [round(random.uniform(5.0, 9.0), 1) for _ in range(len(self.df))]
        if 'vote_count' not in self.df.columns:
            self.df['vote_count'] = [random.randint(100, 50000) for _ in range(len(self.df))]
        if 'popularity' not in self.df.columns:
            self.df['popularity'] = self.df['vote_count'] / self.df['vote_count'].max() * 100
        if 'overview' not in self.df.columns:
            self.df['overview'] = self.df.apply(self._generate_overview, axis=1)
    
    def _ensure_columns(self):
        """Ensure all display columns exist"""
        if 'year' not in self.df.columns:
            self.df['year'] = self.df['title'].apply(self._extract_year)
        if 'clean_title' not in self.df.columns:
            self.df['clean_title'] = self.df['title'].apply(self._clean_title)
        if 'rating' not in self.df.columns:
            self.df['rating'] = 7.0
        if 'vote_count' not in self.df.columns:
            self.df['vote_count'] = 1000
        if 'popularity' not in self.df.columns:
            self.df['popularity'] = 50.0
        if 'overview' not in self.df.columns:
            self.df['overview'] = 'A great movie to watch!'
    
    def _extract_year(self, title):
        """Extract year from movie title like 'Movie Name (1995)'"""
        match = re.search(r'\((\d{4})\)', str(title))
        return int(match.group(1)) if match else None
    
    def _clean_title(self, title):
        """Remove year from title for cleaner display"""
        return re.sub(r'\s*\(\d{4}\)\s*$', '', str(title)).strip()
    
    def _generate_overview(self, row):
        """Generate a placeholder overview"""
        return f"A captivating film: {row.get('clean_title', row['title'])}."
    
    @lru_cache(maxsize=1000)
    def _fetch_omdb_poster(self, title, year):
        """Fetch poster from OMDb API (with caching)"""
        if not OMDB_API_KEY:
            return None
        
        try:
            params = {
                "apikey": OMDB_API_KEY,
                "t": title,
                "type": "movie"
            }
            if year:
                params["y"] = int(year)
            
            response = requests.get(OMDB_API_URL, params=params, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("Response") == "True":
                    poster = data.get("Poster")
                    if poster and poster != "N/A":
                        return poster
        except Exception:
            pass
        
        return None
    
    def _get_poster_url(self, movie_id, title, row=None):
        """Get poster URL - checks dataset first, then OMDb API, then placeholder"""
        
        # 1. Check if poster_url exists in the dataset
        if row is not None and 'poster_url' in row.index:
            poster_url = row.get('poster_url')
            if pd.notna(poster_url) and poster_url and str(poster_url).startswith('http'):
                # Validate it's a real URL, not our placeholder
                url_str = str(poster_url)
                if 'image.tmdb.org' in url_str:
                    path = url_str.split('/')[-1]
                    if not path.isdigit():  # Real TMDB path
                        return poster_url
                elif 'placeholder' not in url_str.lower():
                    return poster_url
        
        # 2. Try to fetch from OMDb API (if API key is set)
        if OMDB_API_KEY:
            clean = self._clean_title(title)
            year = self._extract_year(title)
            omdb_poster = self._fetch_omdb_poster(clean, year)
            if omdb_poster:
                return omdb_poster
        
        # 3. Fallback to placeholder with movie title
        colors = ['667eea', 'f093fb', '4facfe', '43e97b', 'fa709a', 'fee140', 
                  'a18cd1', '30cfd0', 'f5576c', '4481eb']
        color_index = int(movie_id) % len(colors)
        bg_color = colors[color_index]
        
        clean = self._clean_title(title)[:25]
        # URL encode the title for placeholder
        encoded_title = clean.replace(' ', '+').replace('&', '%26')
        
        return f"https://via.placeholder.com/300x450/{bg_color}/ffffff?text={encoded_title}"
    
    def _movie_to_dict(self, row, include_poster=True, rank=None, similarity=None):
        """Convert a DataFrame row to a movie dictionary"""
        movie_id = int(row['movieId'])
        title = row['title']
        
        movie = {
            'id': movie_id,
            'title': title,
            'clean_title': row.get('clean_title', self._clean_title(title)),
            'year': row.get('year', self._extract_year(title)),
            'genres': row.get('genre_list', []),
            'rating': float(row.get('rating', 7.0)),
            'vote_count': int(row.get('vote_count', 1000)),
            'overview': row.get('overview', 'A great movie to watch!'),
        }
        
        if include_poster:
            movie['poster_url'] = self._get_poster_url(movie_id, title, row)
        
        if rank is not None:
            movie['rank'] = rank
        
        if similarity is not None:
            movie['similarity_score'] = round(float(similarity) * 100, 1)
        
        return movie
    
    def search_movies(self, query, limit=10):
        """Search for movies by title (for autocomplete)"""
        if not self.is_loaded:
            return []
        
        query_lower = query.lower().strip()
        if len(query_lower) < 2:
            return []
        
        # Find movies that contain the query
        mask = self.df['clean_title'].str.lower().str.contains(query_lower, regex=False, na=False)
        matches = self.df[mask].head(limit)
        
        return [self._movie_to_dict(row, include_poster=False) for _, row in matches.iterrows()]
    
    def get_movie_by_id(self, movie_id):
        """Get movie details by ID"""
        if not self.is_loaded:
            return None
        
        movie = self.df[self.df['movieId'] == movie_id]
        if movie.empty:
            return None
        
        return self._movie_to_dict(movie.iloc[0])
    
    def find_movie(self, query):
        """Find the best matching movie for a query"""
        if not self.is_loaded:
            return None
        
        query_lower = query.lower().strip()
        
        # Try exact match first
        exact_match = self.df[self.df['title'].str.lower() == query_lower]
        if not exact_match.empty:
            return exact_match.index[0]
        
        # Try clean title match
        clean_match = self.df[self.df['clean_title'].str.lower() == query_lower]
        if not clean_match.empty:
            return clean_match.index[0]
        
        # Try contains match
        contains_match = self.df[self.df['clean_title'].str.lower().str.contains(query_lower, regex=False, na=False)]
        if not contains_match.empty:
            return contains_match.index[0]
        
        return None
    
    def get_recommendations(self, movie_id=None, movie_title=None, n_recommendations=20):
        """Get movie recommendations based on movie ID or title"""
        if not self.is_loaded:
            return {'error': self.error_message or 'Data not loaded', 'recommendations': []}
        
        # Find the movie index
        if movie_id is not None:
            movie_rows = self.df[self.df['movieId'] == movie_id]
            if movie_rows.empty:
                return {'error': 'Movie not found', 'recommendations': []}
            idx = movie_rows.index[0]
        elif movie_title:
            idx = self.find_movie(movie_title)
            if idx is None:
                return {'error': f'Could not find movie: "{movie_title}"', 'recommendations': []}
        else:
            return {'error': 'Please provide a movie ID or title', 'recommendations': []}
        
        # Get the selected movie
        selected_row = self.df.iloc[idx]
        selected_movie = self._movie_to_dict(selected_row)
        
        # Calculate similarity scores
        movie_vector = self.tfidf_matrix[idx]
        similarity_scores = cosine_similarity(movie_vector, self.tfidf_matrix).flatten()
        
        # Get indices of most similar movies (excluding the input movie)
        similar_indices = similarity_scores.argsort()[::-1]
        similar_indices = [i for i in similar_indices if i != idx][:n_recommendations]
        
        # Build recommendation list
        recommendations = []
        for rank, sim_idx in enumerate(similar_indices, 1):
            row = self.df.iloc[sim_idx]
            score = similarity_scores[sim_idx]
            recommendations.append(self._movie_to_dict(row, rank=rank, similarity=score))
        
        return {
            'selected_movie': selected_movie,
            'recommendations': recommendations,
            'error': None
        }
    
    def get_popular_movies(self, limit=20):
        """Get popular movies for the homepage"""
        if not self.is_loaded:
            return []
        
        # Get movies sorted by popularity/vote_count
        if 'popularity' in self.df.columns:
            sorted_df = self.df.nlargest(limit * 2, 'popularity')
        else:
            sorted_df = self.df.head(limit * 2)
        
        # Sample to add variety
        if len(sorted_df) > limit:
            sorted_df = sorted_df.sample(n=limit, random_state=42)
        
        return [self._movie_to_dict(row) for _, row in sorted_df.iterrows()]
    
    def get_top_rated_movies(self, limit=12):
        """Get top rated movies"""
        if not self.is_loaded:
            return []
        
        if 'rating' in self.df.columns:
            sorted_df = self.df.nlargest(limit, 'rating')
            return [self._movie_to_dict(row) for _, row in sorted_df.iterrows()]
        
        return self.get_popular_movies(limit)
    
    def get_all_genres(self):
        """Get list of all unique genres"""
        if not self.is_loaded:
            return []
        
        all_genres = set()
        for genres in self.df['genre_list']:
            if isinstance(genres, list):
                all_genres.update(genres)
        
        return sorted(list(all_genres))
    
    def get_movies_by_genre(self, genre, limit=20):
        """Get movies filtered by genre"""
        if not self.is_loaded:
            return []
        
        mask = self.df['genre_list'].apply(lambda x: genre in x if isinstance(x, list) else False)
        filtered = self.df[mask]
        
        # Sort by rating and take top movies
        if 'rating' in filtered.columns:
            filtered = filtered.nlargest(limit, 'rating')
        else:
            filtered = filtered.head(limit)
        
        return [self._movie_to_dict(row) for _, row in filtered.iterrows()]
    
    def get_filtered_movies(self, year_from=None, year_to=None, min_rating=0, 
                           runtime=None, sort_by='popularity', genre=None, limit=40):
        """Get movies with advanced filters"""
        if not self.is_loaded:
            return []
        
        filtered = self.df.copy()
        
        # Year filter
        if year_from:
            filtered = filtered[filtered['year'] >= year_from]
        if year_to:
            filtered = filtered[filtered['year'] <= year_to]
        
        # Rating filter
        if min_rating and min_rating > 0:
            filtered = filtered[filtered['rating'] >= min_rating]
        
        # Runtime filter
        if runtime and 'runtime' in filtered.columns:
            if runtime == 'short':
                filtered = filtered[filtered['runtime'] < 90]
            elif runtime == 'medium':
                filtered = filtered[(filtered['runtime'] >= 90) & (filtered['runtime'] <= 120)]
            elif runtime == 'long':
                filtered = filtered[(filtered['runtime'] > 120) & (filtered['runtime'] <= 180)]
            elif runtime == 'epic':
                filtered = filtered[filtered['runtime'] > 180]
        
        # Genre filter
        if genre:
            filtered = filtered[filtered['genre_list'].apply(
                lambda x: genre in x if isinstance(x, list) else False
            )]
        
        # Sorting
        if sort_by == 'rating' and 'rating' in filtered.columns:
            filtered = filtered.sort_values('rating', ascending=False)
        elif sort_by == 'year_desc' and 'year' in filtered.columns:
            filtered = filtered.sort_values('year', ascending=False)
        elif sort_by == 'year_asc' and 'year' in filtered.columns:
            filtered = filtered.sort_values('year', ascending=True)
        elif sort_by == 'title':
            filtered = filtered.sort_values('clean_title', ascending=True)
        elif 'popularity' in filtered.columns:
            filtered = filtered.sort_values('popularity', ascending=False)
        
        # Limit results
        filtered = filtered.head(limit)
        
        return [self._movie_to_dict(row) for _, row in filtered.iterrows()]


# Initialize the recommender
recommender = MovieRecommender()


# ============================================================================
# Flask Routes
# ============================================================================

@app.route('/')
def index():
    """Main page"""
    popular_movies = recommender.get_popular_movies()
    top_rated = recommender.get_top_rated_movies(6)
    genres = recommender.get_all_genres()
    
    # Empty filters for initial page load
    filters = {
        'year_from': None,
        'year_to': None,
        'min_rating': 0,
        'runtime': '',
        'sort_by': 'popularity',
        'genre': ''
    }
    
    return render_template('index.html', 
                         popular_movies=popular_movies,
                         top_rated=top_rated,
                         genres=genres,
                         filters=filters,
                         is_loaded=recommender.is_loaded)


@app.route('/recommend', methods=['POST'])
def recommend():
    """Get recommendations for a movie"""
    movie_id = request.form.get('movie_id')
    movie_title = request.form.get('movie_title', '').strip()
    
    if movie_id:
        result = recommender.get_recommendations(movie_id=int(movie_id))
    elif movie_title:
        result = recommender.get_recommendations(movie_title=movie_title)
    else:
        result = {'error': 'Please enter a movie title', 'recommendations': []}
    
    popular_movies = recommender.get_popular_movies()
    genres = recommender.get_all_genres()
    
    # Empty filters
    filters = {
        'year_from': None,
        'year_to': None,
        'min_rating': 0,
        'runtime': '',
        'sort_by': 'popularity',
        'genre': ''
    }
    
    return render_template('index.html',
                         result=result,
                         popular_movies=popular_movies,
                         genres=genres,
                         filters=filters,
                         search_query=movie_title,
                         is_loaded=recommender.is_loaded)


@app.route('/browse')
def browse():
    """Browse movies with advanced filters"""
    # Get filter parameters
    year_from = request.args.get('year_from', type=int)
    year_to = request.args.get('year_to', type=int)
    min_rating = request.args.get('min_rating', type=float, default=0)
    runtime = request.args.get('runtime', '')
    sort_by = request.args.get('sort_by', 'popularity')
    genre = request.args.get('genre', '')
    
    # Store filters for template
    filters = {
        'year_from': year_from,
        'year_to': year_to,
        'min_rating': min_rating,
        'runtime': runtime,
        'sort_by': sort_by,
        'genre': genre
    }
    
    # Get filtered movies
    filtered_movies = recommender.get_filtered_movies(
        year_from=year_from,
        year_to=year_to,
        min_rating=min_rating,
        runtime=runtime,
        sort_by=sort_by,
        genre=genre,
        limit=40
    )
    
    popular_movies = recommender.get_popular_movies()
    genres = recommender.get_all_genres()
    
    return render_template('index.html',
                         popular_movies=popular_movies,
                         genres=genres,
                         filtered_movies=filtered_movies,
                         filters=filters,
                         selected_genre=genre,
                         is_loaded=recommender.is_loaded)


@app.route('/api/search')
def api_search():
    """API endpoint for movie search (autocomplete)"""
    query = request.args.get('q', '')
    movies = recommender.search_movies(query, limit=8)
    return jsonify(movies)


@app.route('/api/recommend/<int:movie_id>')
def api_recommend(movie_id):
    """API endpoint to get recommendations"""
    result = recommender.get_recommendations(movie_id=movie_id)
    return jsonify(result)


@app.route('/api/genres/<genre>')
def api_genre_movies(genre):
    """API endpoint to get movies by genre"""
    movies = recommender.get_movies_by_genre(genre)
    return jsonify(movies)


@app.route('/api/movie/<int:movie_id>')
def api_movie_details(movie_id):
    """API endpoint to get movie details"""
    movie = recommender.get_movie_by_id(movie_id)
    if movie:
        return jsonify(movie)
    return jsonify({'error': 'Movie not found'}), 404


# ============================================================================
# Run the Application
# ============================================================================

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)
