import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import lyricsgenius


SPOTIFY_CLIENT_ID = 'your_spotify_client_id'
SPOTIFY_CLIENT_SECRET = 'your_spotify_client_secret'
GENIUS_ACCESS_TOKEN = 'your_genius_access_token'



def initialize_spotify_client():
    client_credentials_manager = SpotifyClientCredentials(
        client_id=SPOTIFY_CLIENT_ID,
        client_secret=SPOTIFY_CLIENT_SECRET
    )
    return spotipy.Spotify(client_credentials_manager=client_credentials_manager)



def initialize_genius_client():
    return lyricsgenius.Genius(GENIUS_ACCESS_TOKEN)



def get_spotify_track_info(spotify_client, song_name, artist_name=None):
    query = f'track:{song_name}'
    if artist_name:
        query += f' artist:{artist_name}'
    results = spotify_client.search(q=query, type='track', limit=1)
    if results['tracks']['items']:
        track = results['tracks']['items'][0]
        track_info = {
            'name': track['name'],
            'artist': track['artists'][0]['name'],
            'album': track['album']['name'],
            'release_date': track['album']['release_date']
        }
        return track_info
    else:
        print(f"Could not find '{song_name}' by {artist_name} on Spotify.")
        return None



def get_genius_lyrics(genius_client, song_name, artist_name):
    song = genius_client.search_song(title=song_name, artist=artist_name)
    if song:
        return song.lyrics
    else:
        print(f"Could not find lyrics for '{song_name}' by {artist_name} on Genius.")
        return None



def search_spotify_by_genre_popularity_year(spotify_client, genre=None, popularity=None, year=None, limit=10):
    query = ""
    if genre:
        query += f' genre:"{genre}"'
    if popularity:
        query += f' popularity:{popularity}'
    if year:
        query += f' year:{year}'
    
    results = spotify_client.search(q=query.strip(), type='track', limit=limit)
    tracks = results['tracks']['items']
    return [
        {'name': track['name'], 'artist': track['artists'][0]['name'], 'album': track['album']['name']}
        for track in tracks
    ]



def get_artist_top_tracks(spotify_client, artist_name, limit=5):
    results = spotify_client.search(q=f'artist:{artist_name}', type='artist', limit=1)
    if results['artists']['items']:
        artist_id = results['artists']['items'][0]['id']
        top_tracks = spotify_client.artist_top_tracks(artist_id)['tracks'][:limit]
        return [
            {'name': track['name'], 'album': track['album']['name'], 'popularity': track['popularity']}
            for track in top_tracks
        ]
    else:
        print(f"Could not find artist '{artist_name}' on Spotify.")
        return None



def get_songs_with_similar_lyrics(genius_client, lyrics_query, max_results=5):
    search_results = genius_client.search_lyrics(lyrics_query)
    if search_results['sections']:
        hits = search_results['sections'][0]['hits'][:max_results]
        return [{'title': hit['result']['title'], 'artist': hit['result']['primary_artist']['name']} for hit in hits]
    else:
        print("No songs found with similar lyrics.")
        return None



def main():
    
    spotify_client = initialize_spotify_client()
    genius_client = initialize_genius_client()

    
    song_name = "Shape of You"
    artist_name = "Ed Sheeran"

    
    print("=== Spotify Track Info ===")
    track_info = get_spotify_track_info(spotify_client, song_name, artist_name)
    if track_info:
        print(f"Found on Spotify: {track_info['name']} by {track_info['artist']}")

    
    print("\n=== Lyrics from Genius ===")
    lyrics = get_genius_lyrics(genius_client, track_info['name'], track_info['artist']) if track_info else None
    if lyrics:
        print(f"Lyrics for '{track_info['name']}' by {track_info['artist']}:\n")
        print(lyrics[:1000] + "...")  

    
    print("\n=== Songs by Genre and Popularity ===")
    genre_songs = search_spotify_by_genre_popularity_year(spotify_client, genre="pop", popularity=70, year=2017)
    for song in genre_songs:
        print(f"{song['name']} by {song['artist']} (Album: {song['album']})")

    
    print("\n=== Top Tracks for an Artist ===")
    top_tracks = get_artist_top_tracks(spotify_client, artist_name)
    if top_tracks:
        for i, track in enumerate(top_tracks):
            print(f"{i + 1}. {track['name']} (Album: {track['album']}, Popularity: {track['popularity']})")

    
    print("\n=== Songs with Similar Lyrics ===")
    similar_songs = get_songs_with_similar_lyrics(genius_client, lyrics_query="The club isn't the best place to find a lover")
    if similar_songs:
        for song in similar_songs:
            print(f"'{song['title']}' by {song['artist']}")


if __name__ == "__main__":
    main()
