import requests
import base64
import datetime
from urllib.parse import urlencode
from flask import Flask, jsonify, request, redirect
import spotipy 
from spotipy.oauth2 import SpotifyClientCredentials,SpotifyOAuth
import sys
import os

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(parent_dir)

from constants import *

#app = Flask(__name__)
#scope = "user-library-read"

if __name__ == '__main__':
    # basic configuration to generate token
    request_ret = requests.post("https://accounts.spotify.com/api/token", {
        'grant_type': 'client_credentials',
        'Content-Type': 'application/x-www-form-urlencoded',
        'client_id': SPOTIFY_API_CLIENT_ID,
        'client_secret': SPOTIFY_API_CLIENT_SECRET,
    })
    access_token = request_ret.json().get('access_token')
    #print(access_token)

    #example of accessing artists' metadata
    headers = {
            "Authorization": f"Bearer {access_token}"
    }
    artist_id = '00FQb4jTyendYWaN8pK0wa?si=SjOVmXpdSuSguFAyncPu-w'
    get_artist_info_response = requests.get(f"https://api.spotify.com/v1/artists/{artist_id}", headers=headers)
    print(get_artist_info_response.json())
    