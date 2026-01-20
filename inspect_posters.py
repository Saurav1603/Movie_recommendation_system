import pandas as pd
p='tmdb_movies_processed.csv'
try:
    df=pd.read_csv(p)
    total=len(df)
    missing_null=df['poster_url'].isna().sum()
    missing_empty=(df['poster_url'].fillna('')=='').sum()
    missing = df[df['poster_url'].isna() | (df['poster_url'].fillna('')=='')]
    print('total', total)
    print('missing_null', missing_null)
    print('missing_empty', missing_empty)
    print('\nSample missing rows:')
    print(missing[['movieId','title','year','poster_url']].head(20).to_string(index=False))
except Exception as e:
    print('ERROR', e)
