# Movie Recommendation System

A content-based movie recommendation web application built with Python and Streamlit.

## Project structure

```text
movie_recommendation_system/
├── app.py
├── requirements.txt
├── README.md
├── notebook86c26b4f17.ipynb
├── tmdb_5000_movies.csv
├── tmdb_5000_credits.csv
└── model/
    ├── movie_list.pkl
    └── similarity.pkl
```

## Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Generate model files

Open and run all cells in `notebook86c26b4f17.ipynb`. The notebook creates:

- `movie_list.pkl`
- `similarity.pkl`

Move both files into the `model/` folder.

## TMDB API key

For local development:

**Windows PowerShell**
```powershell
$env:TMDB_API_KEY="YOUR_TMDB_API_KEY"
streamlit run app.py
```

For Streamlit Community Cloud, add this to **Secrets**:

```toml
TMDB_API_KEY = "YOUR_TMDB_API_KEY"
```

Do not hard-code or publicly commit your API key.

## Deploy

Push this folder to GitHub, then deploy the repository on Streamlit Community Cloud. Set `app.py` as the entry point and add the `TMDB_API_KEY` secret.
