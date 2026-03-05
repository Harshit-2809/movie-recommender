
import streamlit as st
import pickle
import pandas as pd
import requests
from dotenv import load_dotenv
import os

load_dotenv()

api_key = os.getenv("API_KEY")


def fetch_poster(movie_id):
    try:
        response = requests.get(
            'https://api.themoviedb.org/3/movie/{}?api_key={}&language=en-US'.format(movie_id, api_key),
            timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            return "https://image.tmdb.org/t/p/w500/" + data['poster_path']
        else:
            return None
    except Exception as e:
        return None


def recommend(movie):
    movie_index = movies[movies['title'] == movie].index[0]
    distances = similarity[movie_index]
    movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:11]

    recommended_movies = []
    recommended_movies_posters = []
    
    for i in movies_list:
        movie_id = movies.iloc[i[0]].movie_id
        recommended_movies.append(movies.iloc[i[0]].title)
        poster = fetch_poster(movie_id)
        recommended_movies_posters.append(poster)

    return recommended_movies, recommended_movies_posters


movies_dict = pickle.load(open('artifacts/movie_dict.pkl', 'rb'))
movies = pd.DataFrame(movies_dict)
similarity = pickle.load(open('artifacts/similarity.pkl', 'rb'))

movies_list = movies['title'].values
st.title('Movie Recommender System')

options = st.selectbox('Select a movie you like', movies_list)

if st.button('Recommend'):
    with st.spinner('Fetching recommendations...'):
        names, posters = recommend(options)
    
    # Display recommendations in two rows of 5
    st.subheader("Recommended Movies")
    
    # First row (movies 0-4)
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.text(names[0])
        if posters[0]:
            st.image(posters[0])
        else:
            st.warning("Poster unavailable")
    with col2:
        st.text(names[1])
        if posters[1]:
            st.image(posters[1])
        else:
            st.warning("Poster unavailable")
    with col3:
        st.text(names[2])
        if posters[2]:
            st.image(posters[2])
        else:
            st.warning("Poster unavailable")
    with col4:
        st.text(names[3])
        if posters[3]:
            st.image(posters[3])
        else:
            st.warning("Poster unavailable")
    with col5:
        st.text(names[4])
        if posters[4]:
            st.image(posters[4])
        else:
            st.warning("Poster unavailable")
    
    # Second row (movies 5-9)
    st.write("")  # Add spacing
    col6, col7, col8, col9, col10 = st.columns(5)
    with col6:
        st.text(names[5])
        if posters[5]:
            st.image(posters[5])
        else:
            st.warning("Poster unavailable")
    with col7:
        st.text(names[6])
        if posters[6]:
            st.image(posters[6])
        else:
            st.warning("Poster unavailable")
    with col8:
        st.text(names[7])
        if posters[7]:
            st.image(posters[7])
        else:
            st.warning("Poster unavailable")
    with col9:
        st.text(names[8])
        if posters[8]:
            st.image(posters[8])
        else:
            st.warning("Poster unavailable")
    with col10:
        st.text(names[9])
        if posters[9]:
            st.image(posters[9])
        else:
            st.warning("Poster unavailable")

