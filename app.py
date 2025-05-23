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

def fetch_poster(movie_id):
    response = requests.get(f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=a95299e81ac22292d76c6b3e83e2c5b0&language=en-US")
    data = response.json()
    poster_path = data.get('poster_path', '')
    if poster_path:
        return "https://image.tmdb.org/t/p/w500/" + poster_path
    return "https://via.placeholder.com/500"

def recommend(movie):
    movie_index = movies[movies['title'] == movie].index[0]
    distances = similarity[movie_index]
    movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]

    recommended_movies = []
    recommended_movies_posters = []
    for i in movies_list:
        movie_id = movies.iloc[i[0]].movie_id
        recommended_movies.append(movies.iloc[i[0]]['title'])
        recommended_movies_posters.append(fetch_poster(movie_id))

    return recommended_movies, recommended_movies_posters

@app.route('/', methods=['GET', 'POST'])
def index():
    recommended = []
    posters = []
    selected_movie = None

    if request.method == 'POST':
        selected_movie = request.form['movie']
        recommended, posters = recommend(selected_movie)

    zipped = zip(recommended, posters)
    return render_template('index.html', movies=movies['title'].values, zipped=zipped, selected_movie=selected_movie)

if __name__ == '__main__':
    app.run(debug=True)
