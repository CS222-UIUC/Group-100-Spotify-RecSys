import time
from flask import Flask, jsonify, request, redirect
import requests
from unittest.mock import Mock, patch
from lyricsgenius import Genius
import constants
import time
from flask import Flask, jsonify, request, redirect, session
import requests
from constants import *

import spotipy
from spotipy.oauth2 import SpotifyOAuth, SpotifyOauthError, SpotifyClientCredentials

app = Flask(__name__)
app.secret_key = APP_SESSION_SECRET_KEY

def get_spotify_oauth():
    # get spotify authorization with necessary scope
    scope = 'playlist-modify-public user-read-email user-read-private user-top-read playlist-read-private user-library-modify user-library-read playlist-modify-private'
    return SpotifyOAuth(
        client_id=SPOTIFY_API_CLIENT_ID,
        client_secret=SPOTIFY_API_CLIENT_SECRET,
        redirect_uri=SPOTIPY_API_REDIRECT_URI,
        scope=scope
    )


def get_valid_token():
    # get access token wrt. valid refresh
    token_info = session.get("token_info", None)

    if not token_info or not token_info['access_token']:
        return None
    
    if token_info['expires_at'] - int(time.time()) < 60: 
        spotify_oauth = get_spotify_oauth()
        token_info = spotify_oauth.refresh_access_token(token_info['refresh_token'])
        session["token_info"] = token_info

    return token_info['access_token']


def get_mocked_personalized_recommendation():
    # basing it on my personal songs, utilized https://www.chosic.com/playlist-generator/
    # in format of json_obj[track][i][artist][j][name]
    tracks = [("Alright", "Victoria Monet"),
    ("NVMD", "Denise Julia"),
    ("Right My Wrongs", "Bryson Tiller"),
    ("Shameless", "Avenoir"),
    ("Awkward", "Sza")]

    res = {}
    res['tracks'] = []

    for track in tracks:
        res['tracks'].append({'name' : track[0], 'artists' : [{'name' : track[1]}]})

    return res


def get_mocked_general_recommendations():
    # https://tunebat.com/Advanced for recommendations
    # based on danceability 0.62, bpm 125, dance pop
    dance_pop_tracks = [("Say My Name", "Destiny's Child"), 
                        ("So What", "P!nk"), 
                        ("Last Friday Night (T.G.I.F)", "Katy Perry"),
                        ("Who You Are", "Jessie J"), 
                        ("You Don't Know My Name", "Alicia Keys")]
    
    dance_res = {}
    dance_res['tracks'] = []

    for track in dance_pop_tracks:
        dance_res['tracks'].append({'name' : track[0], 'artists' : [{'name' : track[1]}]})

    # based on danceability 0.7, bpm 146, rock

    rock_tracks = [("Bohemian Rhapsody", "Queen"), 
                   ("Wanted Dead or Alive", "Bon Jovi"), 
                   ("Amazing", "Aerosmith"), 
                   ("I Get Around (Mono)", "The Beach Boys"), 
                   ("Waterloo", "ABBA")]
    rock_res = {}
    rock_res['tracks'] = []

    for track in rock_tracks:
        rock_res['tracks'].append({'name' : track[0], 'artists' : [{'name' : track[1]}]})

    return dance_res, rock_res

    


@app.route("/api/spotify-login", methods=["GET"])
def spotify_login():
    # spotify authorization and redirect url
    oauth = get_spotify_oauth()
    auth_url = oauth.get_authorize_url()
    return redirect(auth_url)

@app.route("/api/spotify-callback", methods=["GET"])
def spotify_callback():
    # process to generate auth token from code generated from redirect spotify access
    try:
        oauth = get_spotify_oauth()
    except SpotifyOauthError:
        return jsonify({"error": "Authorization failed"}), 400

    code = request.args.get("code")
    
    if not code:
        return jsonify({"error": "Authorization code not found"}), 400

    try:
        token_info = oauth.get_access_token(code)
        session["token_info"] = token_info
        return jsonify(token_info), 200
    except SpotifyOauthError:
        return jsonify({"error": "Authorization failed"}), 400


@app.route("/api/display-songs", methods=['POST'])
def get_top_5_songs():

    try:
        access_token = get_valid_token()
    except:
        return jsonify({'error': "Bad authorization token"}), 400
    
    if not access_token:
        return jsonify({'error': 'No valid token available'}), 400

    spotify = spotipy.Spotify(auth=access_token)

    try:
        top_tracks_response = spotify.current_user_top_tracks(limit=5)
        top_tracks = []

        for i, track in enumerate(top_tracks_response['items']):  
            song = {}
            song['title'] = track['name']
            artists = []

            for j in range(len(track['artists'])):
                artists.append(track['artists'][j]['name'])
            song['artists'] = artists
            top_tracks.append(song)

        #top_tracks = [track['name'] for track in top_tracks_response['items']]
        return jsonify({'top_tracks': top_tracks, 'token' : access_token}), 200
    
    except spotipy.SpotifyException:
        return jsonify({'error': 'Failed to fetch top tracks'}), 400



@app.route("/api/recc", methods=['POST'])
def get_recommendations_from_params():
    # different spotify credentials -- this does not connect to user's spotify
    spotipy_unauth = SpotifyClientCredentials(client_id=SPOTIFY_API_CLIENT_ID, client_secret=SPOTIFY_API_CLIENT_SECRET)
    spotify = spotipy.Spotify(client_credentials_manager=spotipy_unauth)

    try: # not including popularity at the moment
        data = request.json
        genres = data.get('genres', [])
        danceability = data.get('danceability', None)
        tempo = data.get('tempo', None)
        params = {'seed_genres': genres}
        
        if danceability is not None:
            if not (0 <= danceability <= 1): # danceabiity is flota betwen [0,1]
                return jsonify({'error': 'Invalid danceability, valid range between 0 and 1'}), 400
            params['target_danceability'] = danceability

        if tempo is not None:
            if not (60 <= tempo <= 200): # tempo between 60-200
                return jsonify({'error': 'Invalid tempo value, valid range between 60 and 200 BPM'}), 400
            params['target_tempo'] = tempo

        if not genres:
            del params['seed_genres']
            #return jsonify({'error': 'At least one genre must be provided.'}), 400

        #recs_response = spotify.recommendations(limit=5, **params)
        dance_res, rock_res = get_mocked_general_recommendations()
        if 'rock' in genres:
            mocked_res = rock_res
        else:
            mocked_res = dance_res 
        with patch.object(spotify, 'recommendations', return_value = mocked_res):
            recs_response = spotify.recommendations(limit=5, **params)
            recs = []
            for i in range(len(recs_response['tracks'])):
                song = {}
                song['title'] = recs_response['tracks'][i]['name']
                artists = []

                for j in range(len(recs_response['tracks'][i]['artists'])):
                    artists.append(recs_response['tracks'][i]['artists'][j]['name'])
                song['artists'] = artists
                recs.append(song)

            return jsonify({'recommended_songs': recs}), 200
    except spotipy.SpotifyException as e:
        print('error', e)
        return jsonify({'error': f'Failed to fetch recommendations'}), 400


 

@app.route("/api/personal-recc", methods = ['POST'])
#@patch('spotipy.client.Spotify.recommendations')
def get_top_5_recommendations():
    try:
        access_token = get_valid_token()
    except:
        return jsonify({'error': "Bad authorization token"}), 400

    if not access_token:
        return jsonify({'error': 'No valid token available'}), 400

    spotify = spotipy.Spotify(auth=access_token)
    try:
        top_track_response = spotify.current_user_top_tracks(limit=3)
        top_artist_response = spotify.current_user_top_artists(limit=2)
        top_artists = []
        top_names = []
        top_ids = []
        for i in range(len(top_artist_response["items"])):
            top_artists.append(top_artist_response["items"][i]["id"])

        for i in range(len(top_track_response["items"])):
            top_names.append(top_track_response["items"][i]["name"])
            top_ids.append(top_track_response["items"][i]["id"])
        # mocked here after spotify recommendation deprecation
        with patch.object(spotify, 'recommendations', return_value = get_mocked_personalized_recommendation()):
            recs_response = spotify.recommendations(seed_artists=top_artists, seed_genres=None, seed_tracks=top_ids, limit=5, country=None)
            #recs_response = get_mocked_personalized_recommendation()
            recs = []
            for i in range(len(recs_response['tracks'])):
                song = {}
                song['title'] = recs_response['tracks'][i]['name']
                artists = []
                for j in range(len(recs_response['tracks'][i]['artists'])):
                    artists.append(recs_response['tracks'][i]['artists'][j]['name'])
                song['artists'] = artists
                recs.append(song)
            print(recs)
            return jsonify({'recommended_songs' : recs, 'token' : access_token}), 200
        
    except spotipy.SpotifyException:
        return jsonify({'error': 'Failed to fetch top tracks'}), 400

@app.route('/api/genius-facts', methods = ['POST'])
def get_top_5_genius_facts():

    genius = Genius(GENIUS_API_CLIENT_ACCESS_TOKEN, timeout=25, retries=3)
    
    try:
        data = request.json
        recs = data.get('songs', [])
        overall_comments = {}
        
        for spotify_song in recs:
            title = spotify_song['title']
            artists = spotify_song['artists']
            song = genius.search_song(title, artists[0])

            if song is None:
                continue

            song_data = genius.song(song.id, text_format='plain')
            overall_comments[title] = (song_data['song']['description']['plain'])

        return jsonify({'genius_facts' : overall_comments}), 200
    
    except spotipy.SpotifyException:
        return jsonify({'error': 'Failed to fetch top tracks'}), 400


@app.route('/api/save-recommended', methods = ['POST'])
def add_recs_to_new_playlist():
    try:
        access_token = get_valid_token()
    except:
        return jsonify({'error': "Bad authorization token"}), 400
    
    if not access_token:
        return jsonify({'error': 'No valid token available. Need token for personalized recommendation'}), 400
    
    spotify = spotipy.Spotify(auth=access_token)
    try:
        data = request.json
        recs = data.get('songs', [])
        playlist_title = data.get('title', [])

        description = "Spotify Recommendation Generated Songs :)"
        user_info = spotify.current_user()['id']

        playlists_response = spotify.current_user_playlists()
        found_curr_playlist = False
        playlist_id = ""

        for playlist in playlists_response['items']:
            if playlist and playlist['name'] == playlist_title:
                found_curr_playlist = True
                playlist_id = playlist['id']

        if not found_curr_playlist:
            spotify.user_playlist_create(user_info, playlist_title, public=False, collaborative=False, description=description)

            for playlist in spotify.current_user_playlists()['items']:
                if playlist and playlist['name'] == playlist_title:
                    found_curr_playlist = True
                    playlist_id = playlist['id']
        
        tracks = [("Alright", "Victoria Monet"),
        ("NVMD", "Denise Julia"),
        ("Right My Wrongs", "Bryson Tiller"),
        ("Shameless", "Avenoir"),
        ("Awkward", "Sza")]

        track_ids = []
        for spotify_song in recs:
            title = spotify_song['title']
            artist = spotify_song['artists'][0]
            query = f"track:{title} artist:{artist}"
            results = spotify.search(q=query, type="track", limit=1)

            if results['tracks']['items']:
                #print(results['tracks']['items'][0])
                #track_ids['items'].append(results['tracks']['items'][0])
                track_ids.append(results['tracks']['items'][0]['id'])
        if track_ids:
            spotify.user_playlist_add_tracks(user_info, playlist_id, track_ids)
        return jsonify({'success_upload' : 'Uploaded playlists to Spotify'}), 200

    except spotipy.SpotifyException:
        return jsonify({'error': 'Failed to upload recommendations'}), 400