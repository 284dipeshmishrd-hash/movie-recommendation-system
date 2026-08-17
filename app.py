import os
import pickle
import requests
import streamlit as st


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="Movie Recommendation System",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# =========================================================
# TMDB API KEY
# =========================================================

try:
    TMDB_API_KEY = st.secrets.get("TMDB_API_KEY", "")
except Exception:
    TMDB_API_KEY = ""


# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown(
    """
    <style>

    /* Main Background */
    .stApp {
        background: linear-gradient(
            135deg,
            #0f0c29,
            #302b63,
            #24243e
        );
    }

    /* Main Container */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1200px;
    }

    /* Main Title */
    .main-title {
        text-align: center;
        font-size: 52px;
        font-weight: 800;
        color: white;
        margin-bottom: 5px;
    }

    /* Subtitle */
    .subtitle {
        text-align: center;
        font-size: 20px;
        color: #d1d1d1;
        margin-bottom: 35px;
    }

    /* Select Box Label */
    label[data-testid="stWidgetLabel"] p {
        color: white !important;
        font-size: 18px;
        font-weight: bold;
    }

    /* Select Box */
    div[data-baseweb="select"] > div {
        border-radius: 10px;
    }

    /* Button */
    .stButton > button {
        width: 100%;
        background: linear-gradient(
            90deg,
            #ff416c,
            #ff4b2b
        );
        color: white;
        border: none;
        border-radius: 12px;
        padding: 12px;
        font-size: 18px;
        font-weight: bold;
        transition: 0.3s;
    }

    .stButton > button:hover {
        transform: scale(1.03);
        background: linear-gradient(
            90deg,
            #ff4b2b,
            #ff416c
        );
    }

    /* Recommendation Title */
    .recommendation-title {
        text-align: center;
        color: white;
        font-size: 32px;
        font-weight: bold;
        margin-top: 35px;
        margin-bottom: 25px;
    }

    /* Movie Card */
    .movie-card {
        background: rgba(255, 255, 255, 0.10);
        padding: 15px;
        border-radius: 18px;
        text-align: center;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.15);
        transition: 0.3s;
        min-height: 100%;
    }

    .movie-card:hover {
        transform: translateY(-8px);
        border: 1px solid #ff4b4b;
    }

    /* Movie Name */
    .movie-name {
        color: white !important;
        font-size: 20px;
        font-weight: bold;
        text-align: center;
        min-height: 60px;
        margin-top: 15px;
    }

    /* Footer */
    .footer {
        text-align: center;
        color: #90EE90;
        margin-top: 40px;
        font-size: 16px;
        font-weight: bold;
        background: transparent;
        padding: 0;
    }

    /* API Warning */
    .api-warning {
        background: rgba(255, 193, 7, 0.15);
        border: 1px solid rgba(255, 193, 7, 0.5);
        border-radius: 10px;
        padding: 12px;
        color: #fff3cd;
        text-align: center;
        margin-bottom: 20px;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# =========================================================
# LOAD MODEL
# =========================================================

@st.cache_resource
def load_models():

    movies_path = "model/movie_list.pkl"
    similarity_path = "model/similarity.pkl"

    if not os.path.exists(movies_path):
        raise FileNotFoundError(
            f"Missing file: {movies_path}"
        )

    if not os.path.exists(similarity_path):
        raise FileNotFoundError(
            f"Missing file: {similarity_path}"
        )

    with open(movies_path, "rb") as file:
        movies = pickle.load(file)

    with open(similarity_path, "rb") as file:
        similarity = pickle.load(file)

    return movies, similarity


# =========================================================
# FETCH MOVIE POSTER
# =========================================================

def fetch_poster(movie_id):

    # If API key is not configured
    if not TMDB_API_KEY:
        return None

    try:

        url = (
            "https://api.themoviedb.org/3/movie/"
            f"{movie_id}"
        )

        response = requests.get(
            url,
            params={
                "api_key": TMDB_API_KEY,
                "language": "en-US"
            },
            timeout=10
        )

        response.raise_for_status()

        data = response.json()

        poster_path = data.get("poster_path")

        if poster_path:

            return (
                "https://image.tmdb.org/t/p/w500"
                + poster_path
            )

    except requests.exceptions.RequestException:
        return None

    except Exception:
        return None

    return None


# =========================================================
# RECOMMEND MOVIES
# =========================================================

def recommend(movie, movies, similarity):

    # Find selected movie
    movie_indices = movies[
        movies["title"] == movie
    ].index

    if len(movie_indices) == 0:
        return []

    index = movie_indices[0]

    # Calculate similarity
    distances = sorted(
        list(enumerate(similarity[index])),
        reverse=True,
        key=lambda x: x[1]
    )

    recommended_movies = []

    # Get top 5 recommendations
    for item in distances[1:6]:

        movie_index = item[0]

        movie_id = movies.iloc[
            movie_index
        ]["movie_id"]

        movie_name = movies.iloc[
            movie_index
        ]["title"]

        poster = fetch_poster(movie_id)

        recommended_movies.append(
            {
                "name": movie_name,
                "poster": poster
            }
        )

    return recommended_movies


# =========================================================
# MAIN TITLE
# =========================================================

st.markdown(
    """
    <div class="main-title">
        🎬 Movie Recommendation System
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <div class="subtitle">
        Discover movies you will love ❤️
    </div>
    """,
    unsafe_allow_html=True
)


# =========================================================
# LOAD APPLICATION
# =========================================================

try:

    # Load movies and similarity model
    movies, similarity = load_models()

    # =====================================================
    # API KEY MESSAGE
    # =====================================================

    if not TMDB_API_KEY:

        st.markdown(
            """
            <div class="api-warning">
                ⚠️ TMDB API key is not configured.
                Movie recommendations will work,
                but posters may not appear.
            </div>
            """,
            unsafe_allow_html=True
        )

    # =====================================================
    # MOVIE SELECT BOX
    # =====================================================

    selected_movie = st.selectbox(
        "🔍 Search or Select Your Favorite Movie",
        movies["title"].values,
        index=None,
        placeholder="Choose a movie..."
    )

    st.write("")

    # =====================================================
    # RECOMMENDATION BUTTON
    # =====================================================

    if st.button(
        "✨ Get Movie Recommendations"
    ):

        # Check movie selection
        if selected_movie is None:

            st.warning(
                "⚠️ Please select a movie first!"
            )

        else:

            # =================================================
            # LOADING
            # =================================================

            with st.spinner(
                "🎬 Finding the best movies for you..."
            ):

                recommendations = recommend(
                    selected_movie,
                    movies,
                    similarity
                )

            # =================================================
            # DISPLAY RECOMMENDATIONS
            # =================================================

            if recommendations:

                st.markdown(
                    """
                    <div class="recommendation-title">
                        🔥 Recommended For You
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                # Create 5 columns
                cols = st.columns(5)

                # Display each recommendation
                for col, movie in zip(
                    cols,
                    recommendations
                ):

                    with col:

                        # Movie card
                        st.markdown(
                            '<div class="movie-card">',
                            unsafe_allow_html=True
                        )

                        # -------------------------------------
                        # Poster
                        # -------------------------------------

                        if movie["poster"]:

                            st.image(
                                movie["poster"],
                                use_container_width=True
                            )

                        else:

                            # Simple placeholder
                            st.markdown(
                                """
                                <div style="
                                    height: 300px;
                                    display: flex;
                                    align-items: center;
                                    justify-content: center;
                                    background: rgba(
                                        255,255,255,0.08
                                    );
                                    border-radius: 12px;
                                    color: white;
                                    font-size: 18px;
                                ">
                                    🎬<br>
                                    Poster Not Available
                                </div>
                                """,
                                unsafe_allow_html=True
                            )

                        # -------------------------------------
                        # Movie Name
                        # -------------------------------------

                        movie_name = movie["name"]

                        st.markdown(
                            f"""
                            <div class="movie-name">
                                {movie_name}
                            </div>
                            """,
                            unsafe_allow_html=True
                        )

                        # Close card
                        st.markdown(
                            "</div>",
                            unsafe_allow_html=True
                        )

            else:

                st.warning(
                    "⚠️ No recommendations found."
                )


# =========================================================
# FILE ERROR
# =========================================================

except FileNotFoundError as e:

    st.error(
        "❌ Model files not found!"
    )

    st.info(
        """
        Please make sure your GitHub repository
        contains these files:

        model/movie_list.pkl

        model/similarity.pkl
        """
    )

    st.code(str(e))


# =========================================================
# GENERAL ERROR
# =========================================================

except Exception as e:

    st.error(
        "❌ Something went wrong while running the app."
    )

    st.code(str(e))


# =========================================================
# FOOTER
# =========================================================

st.markdown(
    """
    <div class="footer">
        🎬 Movie Recommendation System
        &nbsp; | &nbsp;
        Developed with ❤️ by Dipesh Kr Mishra
    </div>
    """,
    unsafe_allow_html=True
)
