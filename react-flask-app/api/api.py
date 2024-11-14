import time
from flask import Flask, jsonify, request, redirect
import requests
# import spotify_requests.requestHelpers as spotify_request
# import genius_requests.requestHelpers as genius_request
import constants
import time
from flask import Flask, jsonify, request, redirect, session
import requests
from constants import *

import spotipy
from spotipy.oauth2 import SpotifyOAuth, SpotifyOauthError

app = Flask(__name__)
app.secret_key = APP_SESSION_SECRET_KEY

def get_spotify_oauth():
    return SpotifyOAuth(
        client_id=SPOTIFY_API_CLIENT_ID,
        client_secret=SPOTIFY_API_CLIENT_SECRET,
        redirect_uri=SPOTIPY_API_REDIRECT_URI,
        scope="user-top-read"
    )


def get_valid_token():
    token_info = session.get("token_info", None)

    if not token_info or not token_info['access_token']:
        return None
    
    if token_info['expires_at'] - int(time.time()) < 60: 
        spotify_oauth = get_spotify_oauth()
        token_info = spotify_oauth.refresh_access_token(token_info['refresh_token'])
        session["token_info"] = token_info

    return token_info['access_token']

'''
@app.route("/api/time", methods=["GET"])
def get_current_time():
    return {"time": time.time()}


@app.route("/api/send-message", methods=["POST"])
def send_message():
    data = request.get_json()
    message = data.get("name", "")
    return jsonify({"responseMessage": f"Hello {message}"})

'''
@app.route("/api/spotify-login", methods=["GET"])
def spotify_login():
    oauth = get_spotify_oauth()
    auth_url = oauth.get_authorize_url()
    return redirect(auth_url)

@app.route("/api/spotify-callback", methods=["GET"])
def spotify_callback():
    oauth = get_spotify_oauth()
    code = request.args.get("code")
    
    if not code:
        return jsonify({"error": "Authorization code not found"}), 400

    try:
        token_info = oauth.get_access_token(code)
        session["token_info"] = token_info
        return jsonify(token_info)
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
        top_tracks = [track['name'] for track in top_tracks_response['items']]
        return jsonify({'top_tracks': top_tracks, 'token' : access_token})
    except spotipy.SpotifyException:
        return jsonify({'error': 'Failed to fetch top tracks'}), 400



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
            recs.append(recs_response['tracks'][i]['name'])
        return jsonify({'recommended_songs' : recs, 'token' : access_token})
    
    except spotipy.SpotifyException:
        return jsonify({'error': 'Failed to fetch top tracks'}), 400