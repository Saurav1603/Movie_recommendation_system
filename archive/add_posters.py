"""
Script to add REAL poster URLs to TMDB movies using TMDB API
This will update your dataset with actual movie poster images.
"""
import pandas as pd
import requests
import time
import os

# ============================================================
# TMDB API Configuration
# Get your FREE API key from: https://www.themoviedb.org/settings/api
# ============================================================
API_KEY = "YOUR_API_KEY_HERE"  # <-- PASTE YOUR API KEY HERE
# ============================================================

BASE_URL = "https://api.themoviedb.org/3"
IMAGE_BASE_URL = "https://image.tmdb.org/t/p/w500"

def get_poster_url(movie_id, api_key):
    """Fetch poster URL for a movie using TMDB API"""
    try:
        url = f"{BASE_URL}/movie/{movie_id}?api_key={api_key}"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            poster_path = data.get('poster_path')
            if poster_path:
                return f"{IMAGE_BASE_URL}{poster_path}"
        return None
    except Exception as e:
        return None

def validate_poster_url(url):
    """Check if a poster URL already exists and is valid"""
    if not url or pd.isna(url):
        return False
    url_str = str(url)
    if not url_str.startswith('https://image.tmdb.org/t/p/w500/'):
        return False
    # Check if it's just a number (our placeholder) or has a real path
    path = url_str.replace('https://image.tmdb.org/t/p/w500/', '')
    if path.isdigit():
        return False  # This was our placeholder
    return True

def main():
    # Check if API key is set
    if API_KEY == "YOUR_API_KEY_HERE":
        print("=" * 70)
        print("   TMDB API KEY REQUIRED")
        print("=" * 70)
        print("""
To add real movie posters, you need a FREE TMDB API key.

Steps to get your API key:
1. Go to: https://www.themoviedb.org/signup
2. Create a free account and verify your email
3. Go to: https://www.themoviedb.org/settings/api
4. Click 'Create' under 'Request an API Key'
5. Choose 'Developer' and accept the terms
6. Fill in the form:
   - Application Name: Movie Recommender
   - Application URL: http://localhost:5000
   - Application Summary: Personal movie recommendation app
7. Copy your 'API Key (v3 auth)' 
8. Open this file (add_posters.py) and paste it on line 15

Then run this script again!
        """)
        print("=" * 70)
        return
    
    # Find the best input file
    input_files = ['tmdb_movies_processed.csv', 'movies_enhanced.csv', 'movies.csv']
    input_file = None
    for f in input_files:
        if os.path.exists(f):
            input_file = f
            break
    
    if not input_file:
        print("Error: No movie dataset found!")
        return
    
    output_file = 'tmdb_movies_with_posters.csv'
    
    print(f"Loading {input_file}...")
    df = pd.read_csv(input_file)
    print(f"Found {len(df)} movies")
    
    # Create movieId column if needed (for API calls)
    if 'movieId' not in df.columns and 'id' in df.columns:
        df['movieId'] = df['id']
    
    # Check existing posters
    if 'poster_url' not in df.columns:
        df['poster_url'] = None
    
    # Find movies that need posters
    needs_poster = ~df['poster_url'].apply(validate_poster_url)
    movies_to_fetch = df[needs_poster].copy()
    
    valid_count = (~needs_poster).sum()
    print(f"Already have {valid_count} valid poster URLs")
    print(f"Need to fetch {len(movies_to_fetch)} posters")
    
    if len(movies_to_fetch) == 0:
        print("All movies already have posters!")
        return
    
    # Fetch posters
    total = len(movies_to_fetch)
    fetched = 0
    failed = 0
    
    print(f"\n{'=' * 50}")
    print(f"Fetching {total} posters from TMDB API...")
    print("Rate limited to 40 requests per 10 seconds")
    print(f"Estimated time: {(total / 40) * 10 / 60:.1f} minutes")
    print(f"{'=' * 50}\n")
    
    for idx, (index, row) in enumerate(movies_to_fetch.iterrows()):
        movie_id = row.get('movieId') or row.get('id')
        
        if pd.isna(movie_id):
            failed += 1
            continue
        
        poster_url = get_poster_url(int(movie_id), API_KEY)
        
        if poster_url:
            df.at[index, 'poster_url'] = poster_url
            fetched += 1
        else:
            failed += 1
        
        # Progress update
        if (idx + 1) % 50 == 0 or idx == total - 1:
            pct = ((idx + 1) / total) * 100
            print(f"Progress: {idx + 1}/{total} ({pct:.1f}%) - ✓ {fetched} | ✗ {failed}")
        
        # Rate limiting (TMDB allows 40 requests per 10 seconds)
        if (idx + 1) % 40 == 0:
            print("  [Rate limit pause - 10 seconds]")
            time.sleep(10)
    
    # Save the result
    df.to_csv(output_file, index=False)
    
    print(f"\n{'=' * 50}")
    print(f"DONE!")
    print(f"{'=' * 50}")
    print(f"Fetched: {fetched} posters")
    print(f"Failed: {failed}")
    print(f"Saved to: {output_file}")
    
    # Show sample
    print(f"\nSample movies with posters:")
    sample = df[df['poster_url'].apply(validate_poster_url)].head(5)
    for _, row in sample.iterrows():
        print(f"  🎬 {row['title']}")
        print(f"     {row['poster_url']}")
    
    print(f"\n✨ Now restart your Flask app to see the posters!")

if __name__ == "__main__":
    main()
