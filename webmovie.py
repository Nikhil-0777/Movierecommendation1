import streamlit as st
import pickle
import requests
from difflib import get_close_matches

# Load trained model
with open('D:/movierecommend/movie_recommendation_model.pkl', 'rb') as model_file:
    model_data = pickle.load(model_file)

vectorizer = model_data['vectorizer']
similarity_matrix = model_data['similarity_matrix']
movies_data = model_data['movies_data']

# TMDb API Key (Replace 'YOUR_API_KEY' with your actual API key)
API_KEY = "a366864a44b736317794dc0baef71951"  # <-- Replace this with your actual TMDb API key
TMDB_IMAGE_URL = "https://image.tmdb.org/t/p/w500"

# Function to fetch movie poster
def fetch_movie_poster(movie_title):
    search_url = f"https://api.themoviedb.org/3/search/movie?api_key={API_KEY}&query={movie_title}"
    response = requests.get(search_url).json()
    
    if response["results"]:
        poster_path = response["results"][0].get("poster_path")
        if poster_path:
            return TMDB_IMAGE_URL + poster_path
    return None

# Function to recommend movies
def recommend_movie(movie_name):
    list_of_all_titles = movies_data['title'].tolist()
    
    # Find closest match
    close_match = get_close_matches(movie_name, list_of_all_titles, n=1)
    
    if not close_match:
        return "Movie not found in dataset.", []
    
    movie_index = movies_data[movies_data.title == close_match[0]].index[0]
    
    similarity_scores = list(enumerate(similarity_matrix[movie_index]))
    sorted_movies = sorted(similarity_scores, key=lambda x: x[1], reverse=True)[1:6]  # Top 5 movies
    
    recommended_movies = [movies_data.iloc[i[0]].title for i in sorted_movies]
    
    # Fetch posters
    recommended_movies_with_posters = [(title, fetch_movie_poster(title)) for title in recommended_movies]
    
    return recommended_movies_with_posters

# Streamlit Web App
st.title("🎬 Movie Recommendation System ")

# Input box for movie name
movie_name = st.text_input("Enter a movie name:")

# Show recommendations when the user enters a movie
if st.button("Get Recommendations"):
    if movie_name:
        recommendations = recommend_movie(movie_name)
        
        if isinstance(recommendations, tuple) and isinstance(recommendations[1], list):
            st.error(recommendations[0])
        else:
            st.success("Here are the recommended movies:")
            
            cols = st.columns(5)  # Display 5 movies in a row
            
            for i, (movie, poster) in enumerate(recommendations):
                with cols[i]:
                    if poster:
                        st.image(poster, width=150)
                    st.write(f"**{movie}**")
    else:
        st.warning("Please enter a movie name.")
