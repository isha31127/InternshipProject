import streamlit as st
import pickle
import pandas as pd
from fuzzywuzzy import process
from sklearn.neighbors import NearestNeighbors
from tmdbv3api import TMDb, Movie
import requests

# Function to fetch movie poster using TMDB API
def fetch_poster(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=c7ec19ffdd3279641fb606d19ceb9bb1&language=en-US"
    data = requests.get(url).json()
    poster_path = data.get('poster_path')
    if poster_path:
        return f"https://image.tmdb.org/t/p/w500{poster_path}"
    return None

# Load the pickled objects
with open('movie_recommendation_model.pkl', 'rb') as file:
    movies_data, vectorizer, feature_vectors, similarity = pickle.load(file)

# Initialize TMDB API
tmdb = TMDb()
tmdb.api_key = '6acbc555a6993960dfc5c78e087e0c10'
tmdb.language = 'en'
tmdb_movie = Movie()

# Get the list of movie titles
movies_list = movies_data['title'].values

# Define function to get movie recommendations
def get_recommendations(movie_name):
    list_of_all_titles = movies_data['title'].tolist()
    find_close_match = process.extractOne(movie_name, list_of_all_titles)
    if not find_close_match:
        return ["No close match found"], []

    close_match = find_close_match[0]
    index_of_the_movie = movies_data[movies_data.title == close_match].index[0]
    similarity_score = list(enumerate(similarity[index_of_the_movie]))
    sorted_similar_movies = sorted(similarity_score, key=lambda x: x[1], reverse=True)

    recommended_movies = []
    poster_urls = []
    i = 0  # Start i at 0 to ensure 5 recommendations excluding the input movie
    for movie in sorted_similar_movies:
        index = movie[0]
        title_from_index = movies_data.iloc[index]['title']
        if title_from_index.lower() != movie_name.lower() and i < 5:
            recommended_movies.append(title_from_index)
            poster_url = get_movie_poster_url(title_from_index)
            if poster_url:
                poster_urls.append(poster_url)
            i += 1
    return recommended_movies, poster_urls


# Define function to get movie poster URLs from TMDB
def get_movie_poster_url(movie_title):
    search_result = tmdb_movie.search(movie_title)
    if search_result:
        poster_path = search_result[0].poster_path
        return f"https://image.tmdb.org/t/p/w500{poster_path}"
    return None

# Streamlit UI
st.header("Movie Recommender System")
import streamlit.components.v1 as components
imageCarouselComponent = components.declare_component("image-carousel-component", path="frontend/public")
imageUrls = [
    fetch_poster(19995),
    fetch_poster(24428),
    fetch_poster(1726),
    fetch_poster(10195),
    fetch_poster(557),
    fetch_poster(767),
    fetch_poster(209112),
    fetch_poster(207),
    fetch_poster(10193),
    fetch_poster(168259),
    fetch_poster(534),
    fetch_poster(1930),
    fetch_poster(299534)
   
    ]

imageCarouselComponent(imageUrls=imageUrls, height=200)
# Selectbox for movie selection
selected_movie = st.selectbox("Select movie from dropdown", movies_list)

# Display recommendations
if st.button("Show Recommendations"):
    recommendations, poster_urls = get_recommendations(selected_movie)
    st.write("Recommendations for:", selected_movie)
    
    # Display recommendations and posters horizontally
    if recommendations:
        cols = st.columns(len(recommendations))
        for col, title, poster_url in zip(cols, recommendations, poster_urls):
            with col:
                st.text(title)
                if poster_url:
                    st.image(poster_url, use_column_width=True)
