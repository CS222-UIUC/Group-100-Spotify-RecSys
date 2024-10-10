import requests
import base64
import datetime
from urllib.parse import urlencode
from flask import Flask, jsonify, request, redirect
import sys
import os
from lyricsgenius import Genius

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(parent_dir)

from constants import *

if __name__ == '__main__':
    #configuration
    #headers = {
    #"Authorization": f"Bearer {GENIUS_API_CLIENT_ACCESS_TOKEN}"
    #}

    #helpful functions are probably searching and adding songs? maybe done throguh spotify
    #getting lyrics definitely helpful
    #can get youtube url?
    #CAN SEARCH FOR SONG BY LYRICS
    #can get songs by genre-but will do via spotify probs
    #can get lyrics for all songs of a search
    #can get images too

    #Url about package: https://lyricsgenius.readthedocs.io/en/master/usage.html
    genius = Genius(GENIUS_API_CLIENT_ACCESS_TOKEN)

    #search for song by lyrics// alternate method to do same thing too
    request = genius.search_lyrics('Jeremy can we talk a minute?')
    for hit in request['sections'][0]['hits']:
        print(hit['result']['title'])   
    
    #can get all lyrics via url or song ID
    # Using Song URL
    url = "https://genius.com/Andy-shauf-begin-again-lyrics"
    genius.lyrics(song_url=url)

    id = 2885745
    genius.lyrics(id)

    #search for artist's songs
    artist = genius.search_artist("Andy Shauf", max_songs=3, sort="title")
    print(artist.songs)

    #search for song by artist
    song = genius.search_song("To You", artist.name)
    #searches artist's songs for the song before doing the above method
    song = artist.song("To You")
    print(song.lyrics)

    #add song to artist
    artist.add_song(song)

    #save songs to JSON file
    artist.save_lyrics()

    #search for album and save
    album = genius.search_album("The Party", "Andy Shauf")
    album.save_lyrics()

    # Turn off status messages
    genius.verbose = False

    # Remove section headers (e.g. [Chorus]) from lyrics when searching
    genius.remove_section_headers = True

    # Include hits thought to be non-songs (e.g. track lists)
    genius.skip_non_songs = False

    # Exclude songs with these words in their title
    genius.excluded_terms = ["(Remix)", "(Live)"]



    #search function
    '''artist_name = "Lana Del Rey"
    params = {'q': artist_name}
    get_artist_info_response = requests.get('https://api.genius.com/search', headers=headers, params=params)

    print(get_artist_info_response.json())

    #songs
    song_id = 378195
    #text_format optional
    get_song_info_response = requests.get('https://api.genius.com/songs/',headers=headers,params=song_id )
    '''