
import spotipy
from spotipy.oauth2 import SpotifyOauthError
from lyricsgenius import Genius
import sys
import os
import json

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(parent_dir)

from constants import *


# get spotify authorization and access token with necessary scope
def GetAccessTokenWithAuthorization():
    #scope ='user-top-read'
    try:
        oauth_object = spotipy.SpotifyOAuth(client_id=SPOTIFY_API_CLIENT_ID,
                                    client_secret=SPOTIFY_API_CLIENT_SECRET,
                                    redirect_uri=SPOTIPY_API_REDIRECT_URI,
                                    #scope=scope,
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
    recs_response = spotify.recommendations(seed_artists=top_artists, seed_genres=None, seed_tracks=top_ids, limit=5, country=None)
    recs = []
    rec_artists = []
    for i in range(len(recs_response['tracks'])):
        recs.append(recs_response['tracks'][i]['name'])
        rec_artists.append(recs_response['tracks'][i]['artists'][0]['name'])
    return recs, rec_artists

def RecommendationsFromParams(genres, danceability, popularity, tempo):
    token = GetAccessTokenWithAuthorization()
    spotify, genius = GetAPIObjects(token)

    if(danceability > 1 or danceability < 0):
        print("invalid danceability")
        return "invalid danceability", ""
    
    if(popularity > 100 or popularity < 0):
        print("invalid popularity")
        return "invalid popularity", ""
    
    if(tempo > 200 or tempo < 60):
        print("invalid tempo")
        return "invalid tempo", ""
    
    #figure out genre check!!!!
    #all_genres = spotify.recommendation_genre_seeds()

    #may want sliders or textbox for user to choose most parameters and then checkboxes for genres
    #get recommendations based on: genre, danceabilitiy(0-1), popularity(0-100), tempo(60-200BPM)
    
    recs_response = spotify.recommendations(seed_genres=genres, target_danceability=danceability, target_popularity=popularity, target_tempo=tempo,limit=5, country=None)
    recs = []
    rec_artists = []

    for i in range(len(recs_response['tracks'])):
        recs.append(recs_response['tracks'][i]['name'])
        rec_artists.append(recs_response['tracks'][i]['artists'][0]['name'])
    return recs, rec_artists

def CommentsofRecommendations(recs, rec_artists):
    token = GetAccessTokenWithAuthorization()
    spotify, genius = GetAPIObjects(token)
    if(type(recs) != list):
        raise TypeError
    comments = []
    for i in range(len(recs)):
        comments.append([])
        song = genius.search_song(recs[i], rec_artists[i])
        if(song is None):
            return "song not found"
        comments_request = genius.song_comments(song.id, per_page=10)
        for i in range(len(comments_request['comments'])):
            comments[i].append(comments_request['comments'][i]["body"]['plain'])
    return comments

#takes in recommendations and gives facts about them
def InfoOfRecommendations(recs, rec_artists):
    token = GetAccessTokenWithAuthorization()
    spotify, genius = GetAPIObjects(token)
    if(type(recs) != list or type(rec_artists) != list):
        raise TypeError
    for i in range(len(recs)):
        song = genius.search_song(recs[i], rec_artists[i])
        if(song is None):
            print ("song not found")
        song_data = genius.song(song.id)
        title = song_data['song']['full_title']
        artist = song_data['song']['artist_names']
        desc = song_data['song']['description_annotation']['annotations'][0]['body']['plain']
        if(desc == ""):
            desc = "No additional information available."
        print("___________________________________________________________________")
        print(title)
        print("Artist: " + artist)
        print("About:")
        print(desc)
        print("___________________________________________________________________")

        
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



if __name__ == "__main__":
   #I also made sure the song is connected to genius by both song name and author for security
   #recommendations from attributes- can put in up to 5 genres
    
    genres = ['french','pop','r-n-b']
    danceability = .9
    popularity = 30
    tempo = 130

    recs, rec_artists = RecommendationsFromParams(genres, danceability, popularity, tempo)

    InfoOfRecommendations(recs, rec_artists)

