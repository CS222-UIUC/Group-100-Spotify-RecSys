
import spotipy
from spotipy.oauth2 import SpotifyOauthError
from lyricsgenius import Genius
import sys
import os

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(parent_dir)

from constants import *

# get spotify authorization and access token with necessary scope
def GetAccessTokenWithAuthorization():
    scope = 'user-top-read'
    try:
        oauth_object = spotipy.SpotifyOAuth(client_id=SPOTIFY_API_CLIENT_ID,
                                    client_secret=SPOTIFY_API_CLIENT_SECRET,
                                    redirect_uri=SPOTIPY_API_REDIRECT_URI,
                                    scope=scope,
                                    )
        token = oauth_object.get_access_token(as_dict=False)
        return token
    except SpotifyOauthError:
        print("Authorization failed")

# get APIs
def GetAPIObjects(token):
    try:
        spotify = spotipy.Spotify(auth=token)
    except spotipy.client.SpotifyException:
        return "bad authtoken"
    genius = Genius(GENIUS_API_CLIENT_ACCESS_TOKEN)
    return spotify, genius

def RecommendationsFromTops():
    token = GetAccessTokenWithAuthorization()
    spotify, genius = GetAPIObjects(token)

    # get user's top tracks and artists
    try:
        top_track_response = spotify.current_user_top_tracks(limit=3)
        top_artist_response = spotify.current_user_top_artists(limit=2)
    except spotipy.client.SpotifyException:
        print("Error with top retrieval")

    # get top artist ids and top song names/ids
    top_artists = []
    top_names = []
    top_ids = []
    for i in range(len(top_artist_response["items"])):
        top_artists.append(top_artist_response["items"][i]["id"])

    for i in range(len(top_track_response["items"])):
        top_names.append(top_track_response["items"][i]["name"])
        top_ids.append(top_track_response["items"][i]["id"])

    # get recommendations
    recs_response = spotify.recommendations(seed_artists=top_artists, seed_genres=None, seed_tracks=top_ids, limit=1, country=None)
    recs = []
    for i in range(len(recs_response['tracks'])):
        recs.append(recs_response['tracks'][i]['name'])
    return recs

def CommentsofRecommendations(recs):
    token = GetAccessTokenWithAuthorization()
    spotify, genius = GetAPIObjects(token)
    if(type(recs) != list):
        raise TypeError
    song = genius.search_song(recs[0])
    print(song)
    if(song is None):
        return "song not found"

    comments_request = genius.song_comments(song.id, per_page=10)
    comments = []

    for i in range(len(comments_request['comments'])):
        comments.append(comments_request['comments'][i]["body"]['plain'])

    return comments

# FailedExperiment, will not test bc will not be used
def RecommendationsFromAnnotations(song):
    token = GetAccessTokenWithAuthorization()
    spotify, genius = GetAPIObjects(token)
    annotations = genius.song_annotations(song_id=song.id)

    # get recommendations by running annotations through lyric search
    recs = []
    for i in range(len(annotations)):
        search_request = genius.search_lyrics(annotations[i][1][0][0], per_page=1)
        if(len(search_request['sections'][0]['hits']) != 0):
            recs.append(search_request['sections'][0]['hits'][0]['result']['title'])
