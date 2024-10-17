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

#scope = "user-library-read"

def get_auth_token(client_id, client_secret):
    request_ret = requests.post("https://accounts.spotify.com/api/token", {
        'grant_type': 'client_credentials',
        'Content-Type': 'application/x-www-form-urlencoded',
        'client_id': client_id,
        'client_secret': client_secret,
    })
    return request_ret.json().get('access_token')


def get_artist_data(auth_token, artist_id):
    headers = {
            "Authorization": f"Bearer {auth_token}"
    }    
    artist_info_response = requests.get(f"https://api.spotify.com/v1/artists/{artist_id}", headers=headers)
    return artist_info_response.json(), artist_info_response.status_code

def get_album_data(auth_token, album_id):
    headers = {
            "Authorization": f"Bearer {auth_token}"
    }  
    album_info_response = requests.get(f"https://api.spotify.com/v1/albums/{album_id}", headers = headers)
    return album_info_response.json(), album_info_response.status_code

def get_recommended_genres(auth_token):
    headers = {
            "Authorization": f"Bearer {auth_token}"
    }  
    genres = requests.get(f"https://api.spotify.com/v1/recommendations/available-genre-seeds", headers = headers)
    return genres.json(), genres.status_code

def search(auth_token, query):
     headers = {
            "Authorization": f"Bearer {auth_token}"
    }
     params = {'q': query}
     search_query = requests.get(f"https://api.spotify.com/v1/search", headers = headers, params=params)
     return search_query.json(), search_query.status_code

#if __name__ == '__main__':
    # basic configuration to generate token


'''
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
    '''
    