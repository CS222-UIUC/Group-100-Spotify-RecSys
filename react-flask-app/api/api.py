import time
from flask import Flask, jsonify, request, redirect
import requests
# import spotify_requests.requestHelpers as spotify_request
# import genius_requests.requestHelpers as genius_request
import constants
import time
from flask import Flask, jsonify, request, redirect
import requests
import constants

app = Flask(__name__)


@app.route("/api/time", methods=["GET"])
def get_current_time():
    return {"time": time.time()}


@app.route("/api/send-message", methods=["POST"])
def send_message():
    data = request.get_json()
    message = data.get("name", "")
    return jsonify({"responseMessage": f"Hello {message}"})


@app.route("/api/spotify-login", methods=["GET"])
def spotify_login():
    params = {
        "client_id": constants.SPOTIFY_API_CLIENT_ID,
        "response_type": "code",
        "redirect_uri": constants.SPOTIPY_API_REDIRECT_URI,
        "scope":  "user-read-private user-read-email"
    }
    SPOTIFY_AUTH_URL = "https://accounts.spotify.com/authorize"
    url = f"{SPOTIFY_AUTH_URL}?{requests.compat.urlencode(params)}"
    return redirect(url)


@app.route("/api/spotify-callback", methods=["GET"])
def spotify_callback():
    code = request.args.get("code")
    if not code:
        return jsonify({"error": "Authorization code not found"}), 400

    payload = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": constants.SPOTIPY_API_REDIRECT_URI,
        "client_id": constants.SPOTIFY_API_CLIENT_ID,
        "client_secret": constants.SPOTIFY_API_CLIENT_SECRET,
    }
    response = requests.post("https://accounts.spotify.com/api/token", data=payload)
    token_info = response.json()
    return jsonify(token_info)
"""
app = Flask(__name__)

@app.route("/api/time", methods=["GET"])
def get_current_time():
    return {"time": time.time()}


# this is a test function to test backend fuctionality
@app.route("/api/send-message", methods=["POST"])
def send_message():
    data = request.get_json()
    message = data.get("name", "")
    return jsonify({"responseMessage": f"Hello {message}"})


@app.route("/api/login", methods = ['POST'])
def login():
    params = {
        'client_id' : constants.SPOTIFY_API_CLIENT_ID,
        'redirect_uri' : constants.SPOTIPY_API_REDIRECT_URI,
        'scope' : 'user-read-email user-read-private user-top-read',
        'response_type' : 'code'
    }


"""


"""
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
    """