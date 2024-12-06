import time
from flask import Flask, jsonify, request, redirect
import requests

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
    return SpotifyOAuth(
        client_id=SPOTIFY_API_CLIENT_ID,
        client_secret=SPOTIFY_API_CLIENT_SECRET,
        redirect_uri=SPOTIPY_API_REDIRECT_URI,
        scope="user-top-read"
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

@app.route("/api/spotify-login", methods=["GET"])
def spotify_login():
    # spotify authorization and redirect url
    oauth = get_spotify_oauth()
    auth_url = oauth.get_authorize_url()
    return redirect(auth_url)

@app.route("/api/spotify-callback", methods=["GET"])
def spotify_callback():
    # process to generate auth token from code generated from redirect spotify access
    oauth = get_spotify_oauth()
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
    access_token = get_valid_token()

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
def get_top_5_recommendations():
    access_token = get_valid_token()

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

        recs_response = spotify.recommendations(seed_artists=top_artists, seed_genres=None, seed_tracks=top_ids, limit=5, country=None)
        recs = []
        for i in range(len(recs_response['tracks'])):
            song = {}
            song['title'] = recs_response['tracks'][i]['name']
            artists = []
            for j in range(len(recs_response['tracks'][i]['artists'])):
                artists.append(recs_response['tracks'][i]['artists'][j]['name'])
            song['artists'] = artists
            recs.append(song)
        return jsonify({'recommended_songs' : recs, 'token' : access_token}), 200

        #genius = Genius(GENIUS_API_CLIENT_ACCESS_TOKEN)
        
    except spotipy.SpotifyException:
        return jsonify({'error': 'Failed to fetch top tracks'}), 400

@app.route('/api/genius-facts', methods = ['POST'])
def get_top_5_genius_facts():
    access_token = get_valid_token()

    if not access_token:
        return jsonify({'error': 'No valid token available. Need token for personalized recommendation'}), 400
    
    genius = Genius(GENIUS_API_CLIENT_ACCESS_TOKEN)
    
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
        return jsonify({'genius_facts' : overall_comments, 'token' : access_token}), 200
    except spotipy.SpotifyException:
        return jsonify({'error': 'Failed to fetch top tracks'}), 400


