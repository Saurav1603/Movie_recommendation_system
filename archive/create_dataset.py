"""
Script to create an enhanced movie dataset with poster URLs and additional features.
This uses the existing movies.csv and adds TMDB-style poster placeholders.
"""

import pandas as pd
import json
import random

# Read the existing movies.csv
df = pd.read_csv('movies.csv')

print(f"Original dataset has {len(df)} movies")

# Clean up and enhance the data
df = df.dropna(subset=['title', 'genres'])
df = df.drop_duplicates(subset=['title'])

# Create additional features
# Extract year from title
def extract_year(title):
    import re
    match = re.search(r'\((\d{4})\)', str(title))
    return int(match.group(1)) if match else None

def clean_title(title):
    import re
    return re.sub(r'\s*\(\d{4}\)\s*$', '', str(title)).strip()

df['year'] = df['title'].apply(extract_year)
df['clean_title'] = df['title'].apply(clean_title)

# Generate mock ratings (for demo purposes)
# In a real app, you'd get these from TMDB API
random.seed(42)
df['rating'] = [round(random.uniform(5.0, 9.0), 1) for _ in range(len(df))]
df['vote_count'] = [random.randint(100, 50000) for _ in range(len(df))]

# Create popularity score based on vote count
df['popularity'] = df['vote_count'] / df['vote_count'].max() * 100

# Generate overview/description (placeholder)
genre_descriptions = {
    'Action': 'An action-packed adventure',
    'Adventure': 'An exciting journey',
    'Animation': 'A beautifully animated story',
    'Children': 'A family-friendly tale',
    'Comedy': 'A hilarious comedy',
    'Crime': 'A gripping crime story',
    'Documentary': 'An insightful documentary',
    'Drama': 'A compelling drama',
    'Fantasy': 'A magical fantasy',
    'Film-Noir': 'A classic noir tale',
    'Horror': 'A terrifying horror story',
    'Musical': 'A musical experience',
    'Mystery': 'A mysterious thriller',
    'Romance': 'A romantic story',
    'Sci-Fi': 'A science fiction adventure',
    'Thriller': 'A suspenseful thriller',
    'War': 'A war epic',
    'Western': 'A western adventure',
    'IMAX': 'An IMAX experience',
}

def generate_overview(row):
    genres = row['genres'].split('|') if pd.notna(row['genres']) else []
    if genres:
        first_genre = genres[0]
        desc = genre_descriptions.get(first_genre, 'An entertaining film')
        return f"{desc} featuring {row['clean_title']}."
    return f"A captivating film: {row['clean_title']}."

df['overview'] = df.apply(generate_overview, axis=1)

# For poster images, we'll use placeholder URLs
# The actual posters will be generated using a placeholder service
# or you can integrate with TMDB API later
df['poster_path'] = None  # Will be handled in the app using movie ID

# Select and reorder columns
enhanced_df = df[[
    'movieId', 'title', 'clean_title', 'year', 'genres', 
    'rating', 'vote_count', 'popularity', 'overview', 'poster_path'
]].copy()

# Sort by popularity
enhanced_df = enhanced_df.sort_values('popularity', ascending=False)

# Save the enhanced dataset
enhanced_df.to_csv('movies_enhanced.csv', index=False)

print(f"\nEnhanced dataset created with {len(enhanced_df)} movies")
print(f"Columns: {enhanced_df.columns.tolist()}")
print(f"\nSample data:")
print(enhanced_df.head())
print(f"\nSaved to movies_enhanced.csv")
