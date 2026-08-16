import os
import pickle
import requests
import streamlit as st

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Movie Recommendation System",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ---------------- CUSTOM CSS ----------------
st.markdown("""
<style>

/* Main Background */
.stApp {
    background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
}

/* Main Container */
.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
    max-width: 1200px;
}

/* ---------------- MAIN TITLE ---------------- */

.main-title {
    text-align: center;
    font-size: 52px;
    font-weight: 800;
    color: white;
    margin-bottom: 5px;
}

/* ---------------- SUBTITLE ---------------- */

.subtitle {
    text-align: center;
    font-size: 20px;
    color: #d1d1d1;
    margin-bottom: 35px;
}

/* ---------------- SELECT BOX LABEL ---------------- */

label[data-testid="stWidgetLabel"] p {
    color: white !important;
    font-size: 18px;
    font-weight: bold;
}

/* ---------------- SELECT BOX ---------------- */

div[data-baseweb="select"] > div {
    border-radius: 10px;
}

/* ---------------- BUTTON ---------------- */

.stButton > button {
    width: 100%;
    background: linear-gradient(90deg, #ff416c, #ff4b2b);
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
    background: linear-gradient(90deg, #ff4b2b, #ff416c);
}

/* ---------------- RECOMMENDATION TITLE ---------------- */

.recommendation-title {
    text-align: center;
    color: white;
    font-size: 32px;
    font-weight: bold;
    margin-top: 35px;
    margin-bottom: 25px;
}

/* ---------------- MOVIE CARD ---------------- */

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

/* ---------------- MOVIE NAME ---------------- */

.movie-name {
    color: white !important;
    font-size: 20px;
    font-weight: bold;
    text-align: center;
    min-height: 60px;
    margin-top: 15px;
}

/* ---------------- FOOTER ---------------- */

.footer {
    text-align: center;
    color: #90EE90; /* Light Green */
    margin-top: 40px;
    font-size: 16px;
    font-weight: bold;
    background: transparent;
    padding: 0;
}
</style>
""", unsafe_allow_html=True)


# ---------------- API KEY ----------------

try:
    TMDB_API_KEY = st.secrets["TMDB_API_KEY"]

except Exception:
    TMDB_API_KEY = os.getenv("TMDB_API_KEY", "")


# ---------------- LOAD MODEL ----------------

@st.cache_resource
def load_models():

    movies = pickle.load(
        open("model/movie_list.pkl", "rb")
    )

    similarity = pickle.load(
        open("model/similarity.pkl", "rb")
    )

    return movies, similarity


# ---------------- FETCH MOVIE POSTER ----------------

def fetch_poster(movie_id):

    if not TMDB_API_KEY:
        return None

    try:

        url = f"https://api.themoviedb.org/3/movie/{movie_id}"

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

    except Exception:

        return None

    return None


# ---------------- RECOMMEND MOVIES ----------------

def recommend(movie, movies, similarity):

    index = movies[
        movies["title"] == movie
    ].index[0]

    distances = sorted(
        list(enumerate(similarity[index])),
        reverse=True,
        key=lambda x: x[1]
    )

    recommended_movies = []

    for i in distances[1:6]:

        movie_id = movies.iloc[i[0]].movie_id

        movie_name = movies.iloc[i[0]].title

        poster = fetch_poster(movie_id)

        recommended_movies.append({
            "name": movie_name,
            "poster": poster
        })

    return recommended_movies


# ---------------- MAIN APP ----------------

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


# ---------------- LOAD APP ----------------

try:

    movies, similarity = load_models()


    # Movie Selection

    selected_movie = st.selectbox(

        "🔍 Search or Select Your Favorite Movie",

        movies["title"].values,

        index=None,

        placeholder="Choose a movie..."
    )


    st.write("")


    # Recommendation Button

    if st.button(
        "✨ Get Movie Recommendations"
    ):


        if selected_movie is None:

            st.warning(
                "⚠️ Please select a movie first!"
            )


        else:


            # Loading Animation

            with st.spinner(
                "🎬 Finding the best movies for you..."
            ):

                recommendations = recommend(

                    selected_movie,

                    movies,

                    similarity

                )


            # Recommendation Heading

            st.markdown(

                """
                <div class="recommendation-title">
                    🔥 Recommended For You
                </div>
                """,

                unsafe_allow_html=True

            )


            # Create 5 Columns

            cols = st.columns(5)


            # Display Movies

            for col, movie in zip(
                cols,
                recommendations
            ):

                with col:


                    # Movie Card Start

                    st.markdown(

                        '<div class="movie-card">',

                        unsafe_allow_html=True

                    )


                    # Movie Poster

                    if movie["poster"]:

                        st.image(

                            movie["poster"],

                            use_container_width=True

                        )

                    else:

                        st.image(

                            "https://via.placeholder.com/500x750.png?text=No+Poster",

                            use_container_width=True

                        )


                    # Movie Name

                    st.markdown(

                        f'<div class="movie-name">{movie["name"]}</div>',

                        unsafe_allow_html=True

                    )


                    # Movie Card End

                    st.markdown(

                        '</div>',

                        unsafe_allow_html=True

                    )


# ---------------- ERROR HANDLING ----------------

except FileNotFoundError:

    st.error(
        "❌ Model files not found!"
    )

    st.info(
        """
        Please make sure:

        model/movie_list.pkl

        and

        model/similarity.pkl

        are available.
        """
    )


# ---------------- FOOTER ----------------

st.markdown(
    """
    <div class="footer">
        🎬 Movie Recommendation System &nbsp; Developed with ❤️ by Dipesh Kr Mishra
    </div>
    """,
    unsafe_allow_html=True
)