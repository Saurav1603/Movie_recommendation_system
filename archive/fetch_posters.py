"""
Fetch Movie Posters from TMDB API
This script fetches poster URLs for movies and updates the dataset.

To use this script:
1. Get a free API key from https://www.themoviedb.org/settings/api
2. Replace 'YOUR_API_KEY_HERE' with your actual API key
3. Run this script

The TMDB API is free and provides high-quality movie posters.
"""

import pandas as pd
import requests
import time
import os

# ============================================
# CONFIGURATION
# ============================================

# Get your free API key from: https://www.themoviedb.org/settings/api
# 
# INSTRUCTIONS:
# 1. Go to https://www.themoviedb.org/signup and create account
# 2. Go to https://www.themoviedb.org/settings/api
# 3. Click "Create" and choose "Developer"
# 4. Fill the form and get your API key
# 5. Paste your API key below (replace the empty string)
#
TMDB_API_KEY = ""  # <-- Paste your API key here between the quotes

# Example: TMDB_API_KEY = "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6"

# TMDB API endpoints
TMDB_SEARCH_URL = "https://api.themoviedb.org/3/search/movie"
TMDB_IMAGE_BASE_URL = "https://image.tmdb.org/t/p/w500"  # w500 = 500px width

# File paths
INPUT_FILE = "movies_enhanced.csv"
OUTPUT_FILE = "movies_with_posters.csv"

# Rate limiting (TMDB allows 40 requests per 10 seconds)
REQUESTS_PER_BATCH = 35
BATCH_DELAY = 10  # seconds

# ============================================
# FUNCTIONS
# ============================================

def search_movie_poster(title, year=None, api_key=TMDB_API_KEY):
    """Search TMDB for a movie and get its poster URL"""
    
    params = {
        "api_key": api_key,
        "query": title,
        "include_adult": False
    }
    
    if year:
        params["year"] = int(year)
    
    try:
        response = requests.get(TMDB_SEARCH_URL, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            if data["results"]:
                # Get the first (most relevant) result
                movie = data["results"][0]
                poster_path = movie.get("poster_path")
                
                if poster_path:
                    return f"{TMDB_IMAGE_BASE_URL}{poster_path}"
        
        return None
        
    except Exception as e:
        print(f"Error fetching poster for '{title}': {e}")
        return None


def fetch_posters_for_dataset(input_file, output_file, limit=None):
    """Fetch posters for all movies in the dataset"""
    
    if TMDB_API_KEY == "YOUR_API_KEY_HERE":
        print("\n" + "="*60)
        print("⚠️  API KEY REQUIRED")
        print("="*60)
        print("\nTo fetch real movie posters, you need a TMDB API key.")
        print("\n📝 Steps to get your free API key:")
        print("   1. Go to https://www.themoviedb.org/signup")
        print("   2. Create a free account")
        print("   3. Go to Settings → API")
        print("   4. Request an API key (choose 'Developer' option)")
        print("   5. Copy your API key")
        print("   6. Replace 'YOUR_API_KEY_HERE' in this file")
        print("   7. Run this script again")
        print("\n" + "="*60)
        return
    
    print(f"\n📂 Loading dataset from {input_file}...")
    df = pd.read_csv(input_file)
    
    total_movies = len(df)
    if limit:
        df = df.head(limit)
        print(f"   Processing first {limit} movies (out of {total_movies})")
    else:
        print(f"   Found {total_movies} movies")
    
    # Add poster_url column if not exists
    if 'poster_url' not in df.columns:
        df['poster_url'] = None
    
    # Track progress
    found = 0
    not_found = 0
    
    print(f"\n🎬 Fetching posters from TMDB...")
    print(f"   Rate limit: {REQUESTS_PER_BATCH} requests per {BATCH_DELAY} seconds\n")
    
    for idx, row in df.iterrows():
        # Skip if already has poster
        if pd.notna(row.get('poster_url')) and row['poster_url']:
            found += 1
            continue
        
        title = row['clean_title'] if 'clean_title' in row else row['title']
        year = row.get('year')
        
        # Fetch poster
        poster_url = search_movie_poster(title, year)
        
        if poster_url:
            df.at[idx, 'poster_url'] = poster_url
            found += 1
            print(f"   ✓ [{idx+1}/{len(df)}] {title} ({year})")
        else:
            not_found += 1
            print(f"   ✗ [{idx+1}/{len(df)}] {title} ({year}) - not found")
        
        # Rate limiting
        if (idx + 1) % REQUESTS_PER_BATCH == 0:
            print(f"\n   ⏳ Waiting {BATCH_DELAY}s (rate limit)...\n")
            time.sleep(BATCH_DELAY)
    
    # Save results
    print(f"\n💾 Saving to {output_file}...")
    df.to_csv(output_file, index=False)
    
    print(f"\n✅ Done!")
    print(f"   Posters found: {found}")
    print(f"   Not found: {not_found}")
    print(f"   Success rate: {found/(found+not_found)*100:.1f}%")
    print(f"\n📁 Output saved to: {output_file}")


# ============================================
# MAIN
# ============================================

if __name__ == "__main__":
    print("\n" + "="*60)
    print("🎬 TMDB Movie Poster Fetcher")
    print("="*60)
    
    # Fetch posters (set limit for testing, remove for full dataset)
    # For testing, start with limit=100
    # For full dataset, set limit=None (will take several hours)
    
    fetch_posters_for_dataset(
        input_file=INPUT_FILE,
        output_file=OUTPUT_FILE,
        limit=500  # Start with 500 movies for testing, set to None for all
    )
