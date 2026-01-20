import pandas as pd
import requests
import time
import os
import re
from datetime import datetime

OMDB_API_KEY = "3294bca1"
OMDB_API_URL = "http://www.omdbapi.com/"
CSV = 'tmdb_movies_processed.csv'
BACKUP = f"tmdb_movies_processed_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

print('Loading', CSV)
df = pd.read_csv(CSV)
print('Rows:', len(df))

# backup
if not os.path.exists(BACKUP):
    df.to_csv(BACKUP, index=False)
    print('Backup saved to', BACKUP)

# helper to check URL validity
import socket
import urllib.parse

def is_url_valid(url):
    if not isinstance(url, str) or not url.strip():
        return False
    url = url.strip()
    # quick heuristic: if ends with numeric id (bad), treat as invalid
    path = urllib.parse.urlparse(url).path
    last = path.rstrip('/').split('/')[-1]
    if last.isdigit():
        return False
    # try HEAD
    try:
        r = requests.head(url, timeout=5, allow_redirects=True)
        if r.status_code == 200:
            return True
        # some servers don't respond to HEAD; try GET small
        r2 = requests.get(url, timeout=5, stream=True)
        if r2.status_code == 200:
            return True
        return False
    except Exception:
        return False


def fetch_omdb_poster(title, year=None):
    params = {'apikey': OMDB_API_KEY, 't': title, 'type': 'movie'}
    if pd.notna(year):
        try:
            params['y'] = int(year)
        except Exception:
            pass
    try:
        r = requests.get(OMDB_API_URL, params=params, timeout=8)
        if r.status_code == 200:
            data = r.json()
            if data.get('Response') == 'True':
                poster = data.get('Poster')
                if poster and poster != 'N/A':
                    return poster
    except Exception:
        return None
    return None

fixed = 0
checked = 0
failed = 0

candidates = []
for i, row in df.iterrows():
    url = row.get('poster_url', '')
    if not is_url_valid(url):
        candidates.append(i)

print('Candidates to fix:', len(candidates))

# limit requests if you want
# candidates = candidates[:500]

for idx in candidates:
    checked += 1
    row = df.iloc[idx]
    title = row.get('title')
    year = row.get('year', None)
    clean_title = re.sub(r"\s*\(\d{4}\)\s*$", '', str(title)).strip()
    poster = fetch_omdb_poster(clean_title, year)
    if poster:
        df.at[idx, 'poster_url'] = poster
        fixed += 1
        print(f"Fixed [{idx}] {clean_title} -> {poster}")
    else:
        failed += 1
        print(f"Not found OMDb poster for [{idx}] {clean_title}")
    # polite sleep
    time.sleep(0.15)

print('Done. Checked:', checked, 'Fixed:', fixed, 'Failed:', failed)

if fixed > 0:
    out = 'tmdb_movies_processed_updated.csv'
    df.to_csv(out, index=False)
    print('Updated CSV saved to', out)
else:
    print('No updates made.')
