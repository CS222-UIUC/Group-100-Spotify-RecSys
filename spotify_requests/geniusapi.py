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

#if __name__ == '__main__':
    
    #get spotify authorization and access token with necessary scope
def GetAPIObjects():
    scope = 'user-top-read'
    oauth_object = spotipy.SpotifyOAuth(client_id= SPOTIFY_API_CLIENT_ID,
                                    client_secret= SPOTIFY_API_CLIENT_SECRET,
                                    redirect_uri=SPOTIPY_API_REDIRECT_URI,
                                    scope = scope,
                                )
    token = oauth_object.get_access_token(as_dict=False)
    spotify = spotipy.Spotify(auth=token)
    genius = Genius(GENIUS_API_CLIENT_ACCESS_TOKEN)
    return spotify, genius

def RecommendationsFromTops():
    spotify,genius = GetAPIObjects()

    #get user's top tracks and artists
    top_track_response = spotify.current_user_top_tracks(limit=3)
    top_artist_response = spotify.current_user_top_artists(limit=2)

    #get top artist ids and top song names/ids
    top_artists= []
    top_names = []
    top_ids = []
    for i in range(len(top_artist_response["items"])):
        top_artists.append(top_artist_response["items"][i]["id"])

    for i in range(len(top_track_response["items"])):
        top_names.append(top_track_response["items"][i]["name"])
        top_ids.append(top_track_response["items"][i]["id"])

    #get recommendations
    recs_response = spotify.recommendations(seed_artists=top_artists, seed_genres=None, seed_tracks=top_ids, limit=1, country=None)
    recs = []
    for i in range(len(recs_response['tracks'])):
        recs.append(recs_response['tracks'][i]['name'])
    return recs

def CommentsofRecommendations(recs):
    spotify,genius = GetAPIObjects()
    song = genius.search_song(recs[0])

    comments_request = genius.song_comments(song.id, per_page=10)
    comments = []

    for i in range(len(comments_request['comments'])):
        comments.append(comments_request['comments'][i]["body"]['plain'])

    return comments

#FailedExperiment, will not test bc will not be used
def RecommendationsFromAnnotations(song):
    spotify,genius = GetAPIObjects()
    annotations = genius.song_annotations(song_id=song.id)

    #get recommendations by running annotations through lyric search
    recs = []
    for i in range(len(annotations)):
        search_request  = genius.search_lyrics(annotations[i][1][0][0],per_page=1)
        if(len(search_request['sections'][0]['hits']) != 0):
            recs.append(search_request['sections'][0]['hits'][0]['result']['title'])