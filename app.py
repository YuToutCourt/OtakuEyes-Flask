from flask import Flask, render_template, request

from anilist_api import get_ids_by_name, retrive_anime, top_anime_by_trends, top_anime_by_popularity, top_anime_this_season 
from anime import create_anime_object

from neko_sama_scraping import find_anime_in_neko_sama, get_video_url_of, get_nb_episodes

app = Flask(__name__)

@app.route('/')
def redirect():
    return render_template('index.html')

@app.route('/home')
def index():
    return render_template('index.html')

@app.route('/browse', methods=['POST'])
def browse():
    name = request.form['search']
    anime_data = get_ids_by_name(name)

    animes = [create_anime_object(anime) for anime in anime_data['data']['Page']['media'] 
                if anime['format'] not in ["MANGA", "NOVEL", "ONE_SHOT", "MUSIC", "LIGHT_NOVEL", "VISUAL_NOVEL", "SPECIAL"] and \
                    anime['status'] not in ["NOT_YET_RELEASED", "CANCELLED"] and anime['isAdult'] == False]

    return render_template('browse.html', animes=animes)

@app.route('/anime/<id>/<ep>')
def anime(id, ep):
    anime_data = retrive_anime(id)

    anime = create_anime_object(anime_data['data']['Media'])

    anime_data_neko = find_anime_in_neko_sama(anime.title['english'] if anime.title['english'] is not None else anime.title['romaji'])
    if anime_data_neko is None:
        return render_template('anime.html', id=id, ep=-1, anime=anime)

    url_video = get_video_url_of(anime_data_neko, ep)
    if url_video is None:
        return render_template('anime.html', id=id, ep=-1, anime=anime)

    nb_episodes = get_nb_episodes(anime_data_neko, id)

    return render_template('anime.html', id=id, ep=int(ep), anime=anime, url_video=url_video, nb_episodes=nb_episodes)


@app.route('/top_anime')
def top_anime():
    trending_now = [create_anime_object(anime) for anime in top_anime_by_trends()]
    most_popular = [create_anime_object(anime) for anime in top_anime_by_popularity()]
    this_season = [create_anime_object(anime) for anime in top_anime_this_season()]

    return render_template('top_anime.html', trending_now=trending_now, most_popular=most_popular, this_season=this_season)

if __name__ == '__main__':
    app.run(debug=True)