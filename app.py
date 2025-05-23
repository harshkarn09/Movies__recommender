from flask import Flask, render_template, request
import pickle
import pandas as pd
import requests
import gzip

app = Flask(__name__)

# Load data
movies_dict = pickle.load(open('movies_dict.pkl', 'rb'))
movies = pd.DataFrame(movies_dict)

with gzip.open('similarity.pkl.gz', 'rb') as f:
    similarity = pickle.load(f)

# Fetch poster using TMDB API
def fetch_poster(movie_id):
    try:
        url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=a95299e81ac22292d76c6b3e83e2c5b0&language=en-US"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        poster_path = data.get('poster_path')
        if poster_path:
            return "https://image.tmdb.org/t/p/w500/" + poster_path
    except Exception as e:
        print(f"Error fetching poster for movie_id={movie_id}: {e}")
    return "https://via.placeholder.com/500?text=No+Image"

# Recommend function
def recommend(movie):
    if movie not in movies['title'].values:
        return [], []

    movie_index = movies[movies['title'] == movie].index[0]
    distances = similarity[movie_index]
    movie_indices = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]

    recommended_movies = []
    recommended_movies_posters = []
    for i in movie_indices:
        movie_id = movies.iloc[i[0]]['movie_id']
        recommended_movies.append(movies.iloc[i[0]]['title'])
        recommended_movies_posters.append(fetch_poster(movie_id))

    return recommended_movies, recommended_movies_posters

@app.route('/', methods=['GET', 'POST'])
def index():
    selected_movie = None
    recommended = []
    posters = []

    if request.method == 'POST':
        selected_movie = request.form.get('movie')
        if selected_movie:
            recommended, posters = recommend(selected_movie)

    zipped = list(zip(recommended, posters))

    return render_template(
        'index.html',
        movies=movies['title'].values,
        zipped=zipped,
        selected_movie=selected_movie
    )

if __name__ == '__main__':
    app.run(debug=True)
