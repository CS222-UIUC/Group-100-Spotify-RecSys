import requests
import base64
import datetime
from urllib.parse import urlencode
from flask import Flask, url_for, jsonify, request, redirect
import spotipy 
from spotipy.oauth2 import SpotifyClientCredentials,SpotifyOAuth
from lyricsgenius import Genius
import sys
import os
import json

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(parent_dir)

from constants import *

if __name__ == '__main__':

    #Url about package: https://lyricsgenius.readthedocs.io/en/master/usage.html
    
    scope = 'user-top-read'

    oauth_object = spotipy.SpotifyOAuth(client_id= SPOTIFY_API_CLIENT_ID,
                                        client_secret= SPOTIFY_API_CLIENT_SECRET,
                                        redirect_uri=SPOTIPY_API_REDIRECT_URI,
                                        scope = scope,
                                       )
    token = oauth_object.get_access_token(as_dict=False)

    spotify = spotipy.Spotify(auth=token)
    genius = Genius(GENIUS_API_CLIENT_ACCESS_TOKEN)

    top_track_response = spotify.current_user_top_tracks(limit=3)
    top_artist_response = spotify.current_user_top_artists(limit=2)

    top_artists= []

    top_names = []
    top_ids = []

    for i in range(len(top_artist_response["items"])):
        top_artists.append(top_artist_response["items"][i]["id"])

    for i in range(len(top_track_response["items"])):
        top_names.append(top_track_response["items"][i]["name"])
        top_ids.append(top_track_response["items"][i]["id"])

    recs_response = spotify.recommendations(seed_artists=top_artists, seed_genres=None, seed_tracks=top_ids, limit=1, country=None)
    recs = []
    for i in range(len(recs_response['tracks'])):
        recs.append(recs_response['tracks'][i]['name'])
    
    print(top_names)
    print(recs)

    #search for artist's songs
    #artist = genius.search_artist("Vance Joy", max_songs=3, sort="title")
    #print(artist.songs)
    
    song = genius.search_song(recs[0])

    comments_request = genius.song_comments(song.id, per_page=10)

    comments = []

    for i in range(len(comments_request['comments'])):
        comments.append(comments_request['comments'][i]["body"]['plain'])

    print(comments)
    #print(json.dumps(comments_request['comments'], sort_keys=False, indent=4))

    #referent_request = genius.referents(song_id=song.id,
    #                       per_page=1)
    

    #annotations = [y for x in request['referents']
    #        for y in x['annotations']]
    
    #fragments = []
    #ann_text = []

    anns = genius.song_annotations(song_id=song.id)
    #print(anns[0][0])
    #print(anns[0][1][0][0])

    for i in range(len(anns)):
        search_request  = genius.search_lyrics(anns[i][1][0][0],per_page=1)
        #if(len(search_request['sections'][0]['hits']) != 0):
            #print(search_request['sections'][0]['hits'][0]['result']['title'])
    '''
    for i in range(len(request['referents'])):
        #print(annotations[i]['body']['plain'])
        fragments.append(request['referents'][i]['fragment'])
    
    for i in range(len(annotations)):
        #print(annotations[i]['body']['plain'])
        ann_text.append(annotations[i]['body']['plain'])

    '''

    








#search for song by lyrics// alternate method to do same thing too
    '''
    request = genius.search_lyrics('Jeremy can we talk a minute?')
    for hit in request['sections'][0]['hits']:
        print(hit['result']['title'])   
    
    #can get all lyrics via url or song ID
    # Using Song URL
    url = "https://genius.com/Andy-shauf-begin-again-lyrics"
    genius.lyrics(song_url=url)

    id = 2885745
    genius.lyrics(id)
'''
'''
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
    artist_name = "Lana Del Rey"
    params = {'q': artist_name}
    get_artist_info_response = requests.get('https://api.genius.com/search', headers=headers, params=params)

    print(get_artist_info_response.json())

    #songs
    song_id = 378195
    #text_format optional
    get_song_info_response = requests.get('https://api.genius.com/songs/',headers=headers,params=song_id )
    '''