import pandas as pd
import requests
import random

p='tmdb_movies_processed.csv'
df=pd.read_csv(p)
# sample 300 movies
sample=df.sample(n=min(300,len(df)), random_state=42)
failed=[]
for _,row in sample.iterrows():
    url=str(row.get('poster_url',''))
    if not url or url.strip()=='' or url.lower().endswith('n/a'):
        failed.append((row['movieId'], row['title'], url, 'empty'))
        continue
    try:
        r=requests.head(url, timeout=5, allow_redirects=True)
        if r.status_code!=200:
            # try GET
            r2=requests.get(url, timeout=5)
            if r2.status_code!=200:
                failed.append((row['movieId'], row['title'], url, r.status_code))
    except Exception as e:
        failed.append((row['movieId'], row['title'], url, str(e)))

print('checked', len(sample))
print('failed count', len(failed))
for f in failed[:50]:
    print(f)
