"""
Process TMDB 5000 Movies Dataset
Creates an enhanced dataset with poster URLs using TMDB movie IDs
"""

import pandas as pd
import json
import re

# TMDB image base URL - posters are accessed via movie ID
TMDB_IMAGE_BASE = "https://image.tmdb.org/t/p/w500"

print("="*60)
print("🎬 Processing TMDB 5000 Movies Dataset")
print("="*60)

# Load the TMDB movies dataset
print("\n📂 Loading tmdb_5000_movies.csv...")
movies_df = pd.read_csv('tmdb_5000_movies.csv')
print(f"   Found {len(movies_df)} movies")

# Load credits for cast/crew info (optional enhancement)
print("\n📂 Loading tmdb_5000_credits.csv...")
try:
    credits_df = pd.read_csv('tmdb_5000_credits.csv')
    print(f"   Found {len(credits_df)} credit entries")
    has_credits = True
except:
    print("   Credits file not found, skipping...")
    has_credits = False

# Parse JSON fields
def parse_json_field(json_str, key='name', limit=5):
    """Parse JSON string and extract values"""
    try:
        if pd.isna(json_str):
            return []
        data = json.loads(json_str.replace("'", '"'))
        return [item[key] for item in data[:limit] if key in item]
    except:
        return []

def parse_genres(json_str):
    """Parse genres JSON"""
    return parse_json_field(json_str, 'name', limit=10)

def get_director(crew_json):
    """Extract director from crew JSON"""
    try:
        if pd.isna(crew_json):
            return None
        crew = json.loads(crew_json.replace("'", '"'))
        for person in crew:
            if person.get('job') == 'Director':
                return person.get('name')
    except:
        pass
    return None

def get_cast(cast_json, limit=5):
    """Extract top cast members"""
    return parse_json_field(cast_json, 'name', limit=limit)

print("\n🔄 Processing movies...")

# Create enhanced dataframe
enhanced_data = []

for idx, row in movies_df.iterrows():
    movie_id = row['id']
    title = row['title']
    
    # Parse genres
    genres = parse_genres(row['genres'])
    genres_str = '|'.join(genres) if genres else ''
    
    # Extract year from release date
    year = None
    if pd.notna(row.get('release_date')):
        match = re.search(r'(\d{4})', str(row['release_date']))
        if match:
            year = int(match.group(1))
    
    # Get credits info if available
    director = None
    cast = []
    if has_credits:
        credit_row = credits_df[credits_df['movie_id'] == movie_id]
        if not credit_row.empty:
            director = get_director(credit_row.iloc[0].get('crew'))
            cast = get_cast(credit_row.iloc[0].get('cast'), limit=5)
    
    # Build enhanced movie record
    movie_data = {
        'movieId': movie_id,
        'title': f"{title} ({year})" if year else title,
        'clean_title': title,
        'year': year,
        'genres': genres_str,
        'rating': round(float(row.get('vote_average', 0)), 1),
        'vote_count': int(row.get('vote_count', 0)),
        'popularity': float(row.get('popularity', 0)),
        'overview': row.get('overview', 'No overview available.'),
        'runtime': row.get('runtime'),
        'budget': row.get('budget', 0),
        'revenue': row.get('revenue', 0),
        'tagline': row.get('tagline', ''),
        'director': director,
        'cast': '|'.join(cast) if cast else '',
        'keywords': '|'.join(parse_json_field(row.get('keywords'), 'name', 10)),
        # TMDB poster URL - uses movie ID
        'poster_url': f"https://image.tmdb.org/t/p/w500/{movie_id}" if movie_id else None
    }
    
    enhanced_data.append(movie_data)
    
    if (idx + 1) % 500 == 0:
        print(f"   Processed {idx + 1}/{len(movies_df)} movies...")

# Create DataFrame
enhanced_df = pd.DataFrame(enhanced_data)

# Sort by popularity
enhanced_df = enhanced_df.sort_values('popularity', ascending=False)

# Save to CSV
output_file = 'tmdb_movies_processed.csv'
enhanced_df.to_csv(output_file, index=False)

print(f"\n✅ Done! Processed {len(enhanced_df)} movies")
print(f"📁 Saved to: {output_file}")

# Show sample
print("\n📊 Sample data:")
print(enhanced_df[['clean_title', 'year', 'rating', 'genres']].head(10))

print("\n" + "="*60)
print("🎉 Dataset ready! The app will now use this rich dataset.")
print("="*60)
