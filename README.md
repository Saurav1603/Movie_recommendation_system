 # CineMatch — Movie Recommender Web App
 
 A compact, local-first Flask web application that provides content-based movie recommendations using a processed TMDB dataset and simple TF-IDF on genres. The UI includes a searchable movie selector, poster images (fetched from OMDb as a fallback), filters, and a responsive, mobile-first design.
 
 ## What this repo contains
 - `app.py` — Flask application and recommendation engine
 - `tmdb_movies_processed.csv` — processed movie dataset used by the app (kept intentionally small)
 - `templates/` — Jinja2 HTML templates (main UI)
 - `static/` — CSS, icons and client-side assets
 - `requirements.txt` — Python dependencies
 - `archive/` — helper scripts and raw TMDB files (moved to archive to keep repo clean)
 
 > Note: A local `.venv/` is present for development but is ignored by `.gitignore`.
 
 ## Quick start (Windows PowerShell)
 1. Create and activate a virtual environment (if you don't have one):
 
 ```powershell
 python -m venv .venv
 .\.venv\Scripts\Activate.ps1
 ```
 
 2. Install dependencies:
 
 ```powershell
 pip install -r requirements.txt
 ```
 
 3. Run the app:
 
 ```powershell
 C:/Users/<you>/OneDrive/Desktop/miniproject/movie_recommender_web/.venv/Scripts/python.exe app.py
 ```
 
 Open http://127.0.0.1:5000 in your browser.
 
 ## Notes about posters and the OMDb API
 - The app attempts to use `poster_url` values from the dataset first. If a poster is missing or invalid it will try to fetch a poster from the OMDb API.
 - An OMDb API key may be required for full poster coverage. By default this project used a test key during development — do not publish private API keys in public repositories. Instead, set a runtime environment variable or update the app configuration before deploying.
 
 Change the key in `app.py` or use an environment variable (recommended).
 
 ## Cleaning up and preparing for GitHub
 - Large raw datasets and the virtual environment are excluded by `.gitignore`. If you need to add or update the dataset, keep a copy locally and run the dataset processing scripts found in `archive/`.
 
 ## Deploying
 Recommended simple deploy options for Flask apps:
 
 - Render (free tier available) — add a new Web Service, connect your GitHub repo and set the start command to:
 
	 ```
	 .venv/Scripts/python.exe app.py
	 ```
 
 - Railway or Fly.io also work well for small Flask apps.
 
 When deploying, add any API keys as environment variables in the service dashboard rather than hard-coding them in source.
 
 ## Troubleshooting
 - If you see missing posters: run the helper script `fix_posters.py` (in repo history / archive) to attempt fetching replacements from OMDb, or re-run the poster-filling process locally.
 - If the app fails to start due to missing packages, re-run `pip install -r requirements.txt` inside the active virtualenv.
 
 ## Contributing
 - Small fixes, UI improvements, and dataset updates are welcome. Create a branch, commit, and open a pull request. If you update the dataset, add instructions to the README describing the processing steps.
 
 ## License
 This project is provided under the MIT License — see the `LICENSE` file if present.
 
 ---
 If you want, I can (1) finish removing helper files from the repo and push the cleaned repository to GitHub, or (2) prepare a Render deployment configuration and push it for you. Which would you prefer?


