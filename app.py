import os
import subprocess
import random
import locale
import ffmpeg
import requests
from flask import Flask, render_template, request

app = Flask(__name__)
locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
base_dir = os.path.dirname(os.path.abspath(__file__))

def download_movie_cover(movie_name):
    url = f"https://api.themoviedb.org/3/search/movie?api_key={API_KEY}&query={movie_name}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if data['results']:
            poster_path = data['results'][0].get('poster_path')
            if poster_path:
                img_url = f"https://image.tmdb.org/t/p/w500{poster_path}"
                covers_dir = os.path.join(base_dir, 'static', 'covers')
                os.makedirs(covers_dir, exist_ok=True)
                img_path = os.path.join(covers_dir, f"{movie_name}.jpg")
                img_data = requests.get(img_url).content
                with open(img_path, 'wb') as f:
                    f.write(img_data)
                return img_path
    return None

def load_api_keys(file_path):
    keys = {}
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if '=' in line:
                    key, value = line.split('=', 1)
                    keys[key.strip()] = value.strip().strip("'").strip('"')
    except FileNotFoundError:
        raise FileNotFoundError(f"Arquivo de chaves não encontrado: {file_path}")
    return keys

keys_file = os.path.join(base_dir, 'keys.txt')
api_keys = load_api_keys(keys_file)
API_KEY = api_keys.get("tmdbkey", "")
OMDB_API_KEY = api_keys.get("omdbkey", "")

def get_metacritic_score(movie_name):
    url = f"http://www.omdbapi.com/?t={movie_name}&apikey={OMDB_API_KEY}"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        if 'Metascore' in data and data['Metascore'].isdigit():
            return int(data['Metascore'])
    return 'N/A'

def save_ratings(ratings):
    with open(os.path.join(base_dir, 'notas.txt'), 'w', encoding='utf-8') as file:
        for movie_name, rating in ratings.items():
            file.write(f"{movie_name} = {rating}\n")

def get_movie_release_year(movie_name):
    url = f"https://api.themoviedb.org/3/search/movie?api_key={API_KEY}&query={movie_name}"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        if data['results']:
            release_date = data['results'][0].get('release_date', 'N/A')
            if release_date != 'N/A':
                return release_date.split('-')[0]
    return 'N/A'

def load_ratings():
    ratings = {}
    try:
        with open(os.path.join(base_dir, 'notas.txt'), 'r', encoding='utf-8') as file:
            for line in file:
                movie_name, rating = line.strip().split(' = ')
                ratings[movie_name] = rating
    except FileNotFoundError:
        pass
    return ratings

def load_release_dates():
    release_dates = {}
    try:
        with open(os.path.join(base_dir, 'data.txt'), 'r', encoding='utf-8') as file:
            for line in file:
                parts = line.strip().split(' = ')
                if len(parts) == 2:  
                    movie_name, release_date = parts
                    if movie_name not in release_dates:  
                        release_dates[movie_name] = release_date
    except FileNotFoundError:
        pass
    return release_dates

def load_durations():
    durations = {}
    try:
        with open(os.path.join(base_dir, 'durations.txt'), 'r', encoding='utf-8') as file:
            for line in file:
                movie_name, duration = line.strip().split(' = ')
                durations[movie_name] = float(duration)
    except FileNotFoundError:
        pass  
    return durations

def save_durations(durations):
    with open(os.path.join(base_dir, 'durations.txt'), 'w', encoding='utf-8') as file:
        for movie_name, duration in durations.items():
            file.write(f"{movie_name} = {duration}\n")

def get_video_duration(file_path):
    try:
        probe = ffmpeg.probe(file_path)
        duration = float(probe['format']['duration'])
        return duration
    except ffmpeg.Error as e:
        app.logger.error(f"Erro ao obter duração do arquivo {file_path}: {str(e)}")
        return 0

def get_folder_size(folder_path):
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(folder_path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            total_size += os.path.getsize(fp)
    return total_size

def update_movie_list(movie_folder):
    movie_list_path = os.path.join(base_dir, 'lista.txt')
    current_files = [os.path.splitext(f)[0] for f in os.listdir(movie_folder) if f.endswith(('.mp4', '.mkv', '.avi', '.mov', '.flv', '.html'))]
    with open(movie_list_path, 'w', encoding='utf-8') as file:
        file.write("\n".join(current_files))

@app.route('/')
def index():
    movie_folder = os.path.join(base_dir, 'Filmes')
    update_movie_list(movie_folder)
    ratings = load_ratings()
    release_dates = load_release_dates()
    durations = load_durations()
    search_query = request.args.get('search', '').lower()
    files = []
    total_duration = 0  
    num_movies = 0  
    has_new_durations = False
    has_new_release_dates = False  
    has_new_ratings = False

    for filename in os.listdir(movie_folder):
        if filename.endswith(('.mp4', '.mkv', '.avi', '.mov', '.flv', '.html')):
            file_path = os.path.join(movie_folder, filename)
            file_name = os.path.splitext(filename)[0]
            cover_art = f'/static/covers/{file_name}.jpg'
            rating = ratings.get(file_name, 'N/A')
            if file_name not in release_dates:
                release_date = get_movie_release_year(file_name)
                release_dates[file_name] = release_date
                has_new_release_dates = True
            else:
                release_date = release_dates[file_name]
            if file_name not in durations:
                duration = get_video_duration(file_path)
                durations[file_name] = duration
                has_new_durations = True
            else:
                duration = durations[file_name]
            normalized_name = file_name.lower()
            if search_query in normalized_name:
                files.append({
                    'name': file_name, 
                    'path': file_path, 
                    'cover_art': cover_art, 
                    'rating': rating, 
                    'release_date': release_date, 
                    'duration': duration,
                })
            total_duration += duration  
            num_movies += 1  
            if file_name not in ratings:
                metascore = get_metacritic_score(file_name)
                ratings[file_name] = metascore
                has_new_ratings = True

    if has_new_ratings:
        save_ratings(ratings)
    if has_new_durations:
        save_durations(durations)
    if has_new_release_dates:
        with open(os.path.join(base_dir, 'data.txt'), 'w', encoding='utf-8') as file:
            for movie_name, release_date in release_dates.items():
                file.write(f"{movie_name} = {release_date}\n")

    total_size_bytes = get_folder_size(movie_folder)
    total_size_gb = total_size_bytes / (1024 ** 3)

    sort_by = request.args.get('sort_by', 'name')
    order = request.args.get('order', 'asc')
    if sort_by == 'name':
        files.sort(key=lambda x: locale.strxfrm(x['name']), reverse=(order == 'desc'))
    elif sort_by == 'rating':
        files.sort(key=lambda x: int(x['rating']) if x['rating'] != 'N/A' else 0, reverse=(order == 'desc'))
    elif sort_by == 'release_date':
        files.sort(key=lambda x: x['release_date'] if x['release_date'] != 'N/A' else '0000-00-00', reverse=(order == 'desc'))
    elif sort_by == 'duration':
        files.sort(key=lambda x: x['duration'], reverse=(order == 'desc'))

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return render_template('movie_list.html', files=files)
    
    return render_template('index.html', 
                           files=files, 
                           sort_by=sort_by, 
                           order=order, 
                           total_duration=total_duration, 
                           num_movies=num_movies, 
                           total_size_gb=total_size_gb)

@app.route('/play/<path:filename>')
def play(filename):
    try:
        sanitized_filename = os.path.abspath(filename)
        subprocess.run(['start', '', sanitized_filename], shell=True)
        return '', 204  
    except Exception as e:
        return str(e), 500

@app.route('/random')
def random_movie():
    movie_folder = os.path.join(base_dir, 'Filmes')
    ratings = load_ratings()
    release_dates = load_release_dates()
    durations = load_durations()
    files = []
    for filename in os.listdir(movie_folder):
        if filename.endswith(('.mp4', '.mkv', '.avi', '.mov', '.flv', '.html')):
            file_path = os.path.join(movie_folder, filename)
            file_name = os.path.splitext(filename)[0]
            cover_art = f'/static/covers/{file_name}.jpg'
            rating = ratings.get(file_name, 'N/A')
            release_date = release_dates.get(file_name, 'N/A')
            duration = durations.get(file_name, 'N/A')  
            files.append({
                'name': file_name, 
                'path': file_path, 
                'cover_art': cover_art, 
                'rating': rating, 
                'release_date': release_date,
                'duration': duration
            })
    selected_movie = random.choice(files)
    with open(os.path.join(base_dir, 'lista.txt'), 'r', encoding='utf-8') as f:
        movie_list = [line.strip() for line in f.readlines() if line.strip()]
    
    return render_template('random.html', 
                         movie=selected_movie,
                         movie_list=movie_list,
                         num_movies=len(movie_list))

if __name__ == '__main__':
    app.run(debug=True)
