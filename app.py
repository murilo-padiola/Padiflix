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
API_KEY = "ab9814a8f1d3307aac19e7acc2d5a7b0"

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
        print(f"Erro ao obter duração do arquivo {file_path}: {str(e)}")
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
    current_files = [os.path.splitext(f)[0] for f in os.listdir(movie_folder) if f.endswith(('.mp4', '.mkv', '.avi'))]
    with open(movie_list_path, 'w', encoding='utf-8') as file:
        file.write("\n".join(current_files))

@app.route('/')
def index():
    movie_folder = os.path.join(base_dir, 'Filmes')
    update_movie_list(movie_folder)  # Atualiza a lista de filmes

    ratings = load_ratings()
    release_dates = load_release_dates()
    durations = load_durations()
    search_query = request.args.get('search', '').lower()
    files = []
    total_duration = 0  
    num_movies = 0  
    has_new_durations = False
    has_new_release_dates = False  

    for filename in os.listdir(movie_folder):
        if filename.endswith(('.mp4', '.mkv', '.avi')):
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

    total_size_bytes = get_folder_size(movie_folder)
    total_size_gb = total_size_bytes / (1024 ** 3)

    if has_new_durations:
        save_durations(durations)
    if has_new_release_dates:
        with open(os.path.join(base_dir, 'data.txt'), 'w', encoding='utf-8') as file:
            for movie_name, release_date in release_dates.items():
                file.write(f"{movie_name} = {release_date}\n")

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
        subprocess.Popen(['start', '', filename], shell=True)
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
        if filename.endswith(('.mp4', '.mkv', '.avi')):
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
    return render_template('random.html', movie=selected_movie)

if __name__ == '__main__':
    app.run(debug=True)