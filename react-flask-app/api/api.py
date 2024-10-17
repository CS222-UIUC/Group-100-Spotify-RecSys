import time
from flask import Flask, jsonify, request
import requests
app = Flask(__name__)
import spotify_requests.requestHelpers as spotify_request
import genius_requests .requestHelpers as genius_request
import constants 
@app.route('/api/time', methods=['GET'])
def get_current_time():
    return {'time': time.time()}

# this is a test function to test backend fuctionality 
@app.route('/api/send-message', methods=['POST'])
def send_message():
    data = request.get_json()  
    message = data.get('name', '')  
    return jsonify({'responseMessage': f"Hello {message}"})


@app.route('/api/spotify_auth', methods=['POST'])
def get_spotify_auth_token():
    return jsonify({'token' : spotify_request.get_auth_token(constants.SPOTIFY_API_CLIENT_ID, constants.SPOTIFY_API_CLIENT_SECRET)})


@app.route('/api/spotify_artist', methods = ['GET'])
def get_spotify_artist(auth_token, artist_id):
    return jsonify({'artist' : spotify_request.get_artist_data(auth_token, artist_id)})

@app.route('api/spotify_album', methods = ['GET'])
def get_spotify_album(auth_token, album_id):
    return jsonify({'album' : spotify_request.get_album_data(auth_token, album_id)})

@app.route('api/spotify_search', methods = ['GET'])
def get_spotify_query(auth_token, q):
    return jsonify({'query' : spotify_request.search(auth_token, q)})

@app.route('api/get_recommended_genres', methods = ['GET'])
def get_spotify_genre_recc(auth_token):
    return jsonify({'genres' : spotify_request.get_recommended_genres(auth_token)})