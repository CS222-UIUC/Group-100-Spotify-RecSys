import requests
import base64
import datetime
from urllib.parse import urlencode
from flask import Flask, jsonify, request, redirect
import sys
import os

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(parent_dir)

from constants import *





if __name__ == '__main__':
    
    headers = {
            "Authorization": f"Bearer {GENIUS_API_CLIENT_ACCESS_TOKEN}"
    }
    artist_name = "Lana Del Rey"
    params = {'q': artist_name}
    get_artist_info_response = requests.get('https://api.genius.com/search', headers=headers, params=params)
    print(get_artist_info_response.json())