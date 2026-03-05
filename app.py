import streamlit as st
import pickle
import pandas as pd
import requests
from dotenv import load_dotenv
import os

load_dotenv()

api_key = os.getenv("API_KEY")


def fetch_movie_details(movie_id):
    """Fetch detailed movie information from TMDB"""
    try:
        response = requests.get(
            'https://api.themoviedb.org/3/movie/{}?api_key={}&language=en-US'.format(movie_id, api_key),
            timeout=10
        )
        if response.status_code == 200:
            return response.json()
        return None
    except Exception:
        return None


def fetch_poster(movie_id):
    """Fetch movie poster URL"""
    try:
        response = requests.get(
            'https://api.themoviedb.org/3/movie/{}?api_key={}&language=en-US'.format(movie_id, api_key),
            timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            return "https://image.tmdb.org/t/p/w500/" + data['poster_path']
        return None
    except Exception:
        return None


def recommend(movie):
    """Get movie recommendations"""
    movie_index = movies[movies['title'] == movie].index[0]
    distances = similarity[movie_index]
    movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:11]

    recommended_movies = []
    recommended_movies_posters = []
    recommended_movie_ids = []
    recommended_overviews = []
    recommended_ratings = []
    
    for i in movies_list:
        movie_id = movies.iloc[i[0]].movie_id
        recommended_movies.append(movies.iloc[i[0]].title)
        recommended_movie_ids.append(movie_id)
        
        # Fetch poster
        poster = fetch_poster(movie_id)
        recommended_movies_posters.append(poster)
        
        # Fetch movie details
        details = fetch_movie_details(movie_id)
        if details:
            recommended_overviews.append(details.get('overview', 'No overview available')[:150] + '...')
            recommended_ratings.append(details.get('vote_average', 'N/A'))
        else:
            recommended_overviews.append('No overview available')
            recommended_ratings.append('N/A')

    return recommended_movies, recommended_movies_posters, recommended_movie_ids, recommended_overviews, recommended_ratings


# Page configuration
st.set_page_config(
    page_title="Movie Recommender",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    /* Main background */
    .stApp {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
        min-height: 100vh;
    }
    
    /* Title styling */
    .main-title {
        font-size: 3rem !important;
        font-weight: 800 !important;
        background: linear-gradient(90deg, #ff6b6b, #feca57, #48dbfb, #ff9ff3);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        text-align: center;
        padding: 1rem 0;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    /* Subheader styling */
    .recommend-title {
        color: #feca57 !important;
        font-size: 1.8rem !important;
        font-weight: 600 !important;
        text-align: center;
        padding: 1rem 0;
        border-bottom: 2px solid #48dbfb;
        margin-bottom: 1.5rem;
    }
    
    /* Select box styling */
    .stSelectbox label {
        color: #48dbfb !important;
        font-weight: 600 !important;
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 25px !important;
        padding: 0.75rem 2rem !important;
        font-weight: 600 !important;
        font-size: 1.1rem !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4) !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6) !important;
    }
    
    /* Card styling */
    .movie-card {
        background: rgba(255, 255, 255, 0.1);
        border-radius: 15px;
        padding: 10px;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        transition: all 0.3s ease;
    }
    
    .movie-card:hover {
        background: rgba(255, 255, 255, 0.15);
        transform: scale(1.02);
    }
    
    /* Movie title styling */
    .movie-title {
        color: #ffffff !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
        text-align: center;
        margin-top: 0.5rem;
        line-height: 1.3;
        min-height: 2.5rem;
    }
    
    /* Rating badge */
    .rating-badge {
        display: inline-block;
        background: linear-gradient(135deg, #feca57 0%, #ff9f43 100%);
        color: #1a1a2e;
        padding: 2px 8px;
        border-radius: 10px;
        font-weight: 700;
        font-size: 0.8rem;
        margin-top: 5px;
    }
    
    /* Overview text */
    .movie-overview {
        color: rgba(255, 255, 255, 0.7) !important;
        font-size: 0.75rem !important;
        line-height: 1.4;
        margin-top: 5px;
        text-align: center;
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: rgba(0, 0, 0, 0.3) !important;
    }
    
    /* Info message */
    .stInfo {
        background: rgba(72, 219, 251, 0.2) !important;
        border: 1px solid #48dbfb !important;
    }
    
    /* Spinner */
    .stSpinner > div > div {
        border-top-color: #48dbfb !important;
    }
</style>
""", unsafe_allow_html=True)

# Load data
movies_dict = pickle.load(open('artifacts/movie_dict.pkl', 'rb'))
movies = pd.DataFrame(movies_dict)
similarity = pickle.load(open('artifacts/similarity.pkl', 'rb'))

# Main title
st.markdown('<h1 class="main-title">🎬 Movie Recommender System</h1>', unsafe_allow_html=True)

# Create two columns for layout
col1, col2 = st.columns([2, 1])

with col1:
    # Movie selection with autocomplete
    movies_list = sorted(movies['title'].values)
    selected_movie = st.selectbox(
        '🎭 Select a movie you like:',
        movies_list,
        index=None,
        placeholder="Search for a movie..."
    )

with col2:
    st.markdown("<br>", unsafe_allow_html=True)
    show_details = st.checkbox("Show movie details", value=True)

# Recommendation section
if selected_movie:
    st.markdown('<h2 class="recommend-title">✨ Recommended Movies</h2>', unsafe_allow_html=True)
    
    with st.spinner('Finding similar movies... 🔍'):
        names, posters, movie_ids, overviews, ratings = recommend(selected_movie)
    
    # Display recommendations in a responsive grid
    if show_details:
        # Show with details (2 rows of 5)
        cols = st.columns(5)
        
        for idx, (col, name, poster, mid, overview, rating) in enumerate(zip(cols, names, posters, movie_ids, overviews, ratings)):
            with col:
                st.markdown('<div class="movie-card">', unsafe_allow_html=True)
                if poster:
                    st.image(poster, use_container_width=True)
                else:
                    st.markdown("🎬")
                st.markdown(f'<p class="movie-title">{name}</p>', unsafe_allow_html=True)
                st.markdown(f'<span class="rating-badge">⭐ {rating}</span>', unsafe_allow_html=True)
                st.markdown(f'<p class="movie-overview">{overview}</p>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
        
        # Second row
        st.write("")
        cols2 = st.columns(5)
        for idx, (col, name, poster, mid, overview, rating) in enumerate(zip(cols2, names[5:], posters[5:], movie_ids[5:], overviews[5:], ratings[5:])):
            with col:
                st.markdown('<div class="movie-card">', unsafe_allow_html=True)
                if poster:
                    st.image(poster, use_container_width=True)
                else:
                    st.markdown("🎬")
                st.markdown(f'<p class="movie-title">{name}</p>', unsafe_allow_html=True)
                st.markdown(f'<span class="rating-badge">⭐ {rating}</span>', unsafe_allow_html=True)
                st.markdown(f'<p class="movie-overview">{overview}</p>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
    else:
        # Simple display without details (2 rows of 5)
        cols = st.columns(5)
        
        for idx, (col, name, poster) in enumerate(zip(cols, names[:5], posters[:5])):
            with col:
                st.markdown('<div class="movie-card">', unsafe_allow_html=True)
                if poster:
                    st.image(poster, use_container_width=True)
                else:
                    st.markdown("🎬")
                st.markdown(f'<p class="movie-title">{name}</p>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
        
        st.write("")
        cols2 = st.columns(5)
        for idx, (col, name, poster) in enumerate(zip(cols2, names[5:], posters[5:])):
            with col:
                st.markdown('<div class="movie-card">', unsafe_allow_html=True)
                if poster:
                    st.image(poster, use_container_width=True)
                else:
                    st.markdown("🎬")
                st.markdown(f'<p class="movie-title">{name}</p>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

# Sidebar with info
with st.sidebar:
    st.markdown("### ℹ️ About")
    st.info("""
    **Movie Recommender System**
    
    This system uses content-based filtering to recommend similar movies based on:
    
    • Genres
    • Keywords
    • Cast
    • Director
    • Overview
    
    Select a movie and get 10 personalized recommendations!
    """)
    
    st.markdown("### 🎯 How to Use")
    st.markdown("""
    1. Select a movie from the dropdown
    2. Toggle 'Show movie details' for more info
    3. Click 'Recommend' to get suggestions
    4. Browse the recommended movies
    """)
    
    if selected_movie:
        st.markdown("### 📊 Selected Movie")
        st.success(f"**{selected_movie}**")
        
        # Get selected movie ID and details
        selected_id = movies[movies['title'] == selected_movie]['movie_id'].values[0]
        details = fetch_movie_details(selected_id)
        
        if details:
            st.markdown(f"**Rating:** ⭐ {details.get('vote_average', 'N/A')}/10")
            st.markdown(f"**Release Date:** {details.get('release_date', 'N/A')}")
            genres = [g['name'] for g in details.get('genres', [])]
            st.markdown(f"**Genres:** {', '.join(genres[:3]) if genres else 'N/A'}")

