import time
from flask import Flask, jsonify, request, redirect
import requests
from unittest.mock import Mock, patch
from lyricsgenius import Genius
import constants
import time
from flask import Flask, jsonify, request, redirect, session
import requests
from constants import *

import spotipy
from spotipy.oauth2 import SpotifyOAuth, SpotifyOauthError, SpotifyClientCredentials

app = Flask(__name__)
app.secret_key = APP_SESSION_SECRET_KEY

def get_spotify_oauth():
    # get spotify authorization with necessary scope
    scope = 'playlist-modify-public user-read-email user-read-private user-top-read playlist-read-private user-library-modify user-library-read playlist-modify-private'
    return SpotifyOAuth(
        client_id=SPOTIFY_API_CLIENT_ID,
        client_secret=SPOTIFY_API_CLIENT_SECRET,
        redirect_uri=SPOTIPY_API_REDIRECT_URI,
        scope=scope
    )


def get_valid_token():
    # get access token wrt. valid refresh
    token_info = session.get("token_info", None)

    if not token_info or not token_info['access_token']:
        return None
    
    if token_info['expires_at'] - int(time.time()) < 60: 
        spotify_oauth = get_spotify_oauth()
        token_info = spotify_oauth.refresh_access_token(token_info['refresh_token'])
        session["token_info"] = token_info

    return token_info['access_token']


def get_mocked_personalized_recommendation():
    # basing it on my personal songs, utilized https://www.chosic.com/playlist-generator/
    # in format of json_obj[track][i][artist][j][name]
    tracks = [("Alright", "Victoria Monet"),
    ("NVMD", "Denise Julia"),
    ("Right My Wrongs", "Bryson Tiller"),
    ("Shameless", "Avenoir"),
    ("Awkward", "Sza")]

    res = {}
    res['tracks'] = []

    for track in tracks:
        res['tracks'].append({'name' : track[0], 'artists' : [{'name' : track[1]}]})

    return res


def get_mocked_general_recommendations():
    # https://tunebat.com/Advanced for recommendations
    # based on danceability 0.62, bpm 125, dance pop
    dance_pop_tracks = [("Say My Name", "Destiny's Child"), 
                        ("So What", "P!nk"), 
                        ("Last Friday Night (T.G.I.F)", "Katy Perry"),
                        ("Who You Are", "Jessie J"), 
                        ("You Don't Know My Name", "Alicia Keys")]
    
    dance_res = {}
    dance_res['tracks'] = []

    for track in dance_pop_tracks:
        dance_res['tracks'].append({'name' : track[0], 'artists' : [{'name' : track[1]}]})

    # based on danceability 0.7, bpm 146, rock

    rock_tracks = [("Bohemian Rhapsody", "Queen"), 
                   ("Wanted Dead or Alive", "Bon Jovi"), 
                   ("Amazing", "Aerosmith"), 
                   ("I Get Around (Mono)", "The Beach Boys"), 
                   ("Waterloo", "ABBA")]
    rock_res = {}
    rock_res['tracks'] = []

    for track in rock_tracks:
        rock_res['tracks'].append({'name' : track[0], 'artists' : [{'name' : track[1]}]})

    return dance_res, rock_res

    


@app.route("/api/spotify-login", methods=["GET"])
def spotify_login():
    # spotify authorization and redirect url
    oauth = get_spotify_oauth()
    auth_url = oauth.get_authorize_url()
    return redirect(auth_url)

@app.route("/api/spotify-callback", methods=["GET"])
def spotify_callback():
    # process to generate auth token from code generated from redirect spotify access
    try:
        oauth = get_spotify_oauth()
    except SpotifyOauthError:
        return jsonify({"error": "Authorization failed"}), 400

    code = request.args.get("code")
    
    if not code:
        return jsonify({"error": "Authorization code not found"}), 400

    try:
        token_info = oauth.get_access_token(code)
        session["token_info"] = token_info
        return jsonify(token_info), 200
    except SpotifyOauthError:
        return jsonify({"error": "Authorization failed"}), 400


@app.route("/api/display-songs", methods=['POST'])
def get_top_5_songs():

    try:
        access_token = get_valid_token()
    except:
        return jsonify({'error': "Bad authorization token"}), 400
    
    if not access_token:
        return jsonify({'error': 'No valid token available'}), 400

    spotify = spotipy.Spotify(auth=access_token)

    try:
        top_tracks_response = spotify.current_user_top_tracks(limit=5)
        top_tracks = []

        for i, track in enumerate(top_tracks_response['items']):  
            song = {}
            song['title'] = track['name']
            artists = []

            for j in range(len(track['artists'])):
                artists.append(track['artists'][j]['name'])
            song['artists'] = artists
            top_tracks.append(song)

        #top_tracks = [track['name'] for track in top_tracks_response['items']]
        return jsonify({'top_tracks': top_tracks, 'token' : access_token}), 200
    
    except spotipy.SpotifyException:
        return jsonify({'error': 'Failed to fetch top tracks'}), 400



@app.route("/api/recc", methods=['POST'])
def get_recommendations_from_params():
    # different spotify credentials -- this does not connect to user's spotify
    spotipy_unauth = SpotifyClientCredentials(client_id=SPOTIFY_API_CLIENT_ID, client_secret=SPOTIFY_API_CLIENT_SECRET)
    spotify = spotipy.Spotify(client_credentials_manager=spotipy_unauth)

    try: # not including popularity at the moment
        data = request.json
        genres = data.get('genres', [])
        danceability = data.get('danceability', None)
        tempo = data.get('tempo', None)
        params = {'seed_genres': genres}
        
        if danceability is not None:
            if not (0 <= danceability <= 1): # danceabiity is flota betwen [0,1]
                return jsonify({'error': 'Invalid danceability, valid range between 0 and 1'}), 400
            params['target_danceability'] = danceability

        if tempo is not None:
            if not (60 <= tempo <= 200): # tempo between 60-200
                return jsonify({'error': 'Invalid tempo value, valid range between 60 and 200 BPM'}), 400
            params['target_tempo'] = tempo

        if not genres:
            del params['seed_genres']
            #return jsonify({'error': 'At least one genre must be provided.'}), 400

        #recs_response = spotify.recommendations(limit=5, **params)
        dance_res, rock_res = get_mocked_general_recommendations()
        if 'rock' in genres:
            mocked_res = rock_res
        elif 'dance' in genres:
            mocked_res = dance_res 
        with patch.object(spotify, 'recommendations', return_value = mocked_res):
            recs_response = spotify.recommendations(limit=5, **params)
            recs = []
            for i in range(len(recs_response['tracks'])):
                song = {}
                song['title'] = recs_response['tracks'][i]['name']
                artists = []

                for j in range(len(recs_response['tracks'][i]['artists'])):
                    artists.append(recs_response['tracks'][i]['artists'][j]['name'])
                song['artists'] = artists
                recs.append(song)

            return jsonify({'recommended_songs': recs}), 200
    except spotipy.SpotifyException as e:
        print('error', e)
        return jsonify({'error': f'Failed to fetch recommendations'}), 400


 

@app.route("/api/personal-recc", methods = ['POST'])
#@patch('spotipy.client.Spotify.recommendations')
def get_top_5_recommendations():
    try:
        access_token = get_valid_token()
    except:
        return jsonify({'error': "Bad authorization token"}), 400

    if not access_token:
        return jsonify({'error': 'No valid token available'}), 400

    spotify = spotipy.Spotify(auth=access_token)
    try:
        top_track_response = spotify.current_user_top_tracks(limit=3)
        top_artist_response = spotify.current_user_top_artists(limit=2)
        top_artists = []
        top_names = []
        top_ids = []
        for i in range(len(top_artist_response["items"])):
            top_artists.append(top_artist_response["items"][i]["id"])

        for i in range(len(top_track_response["items"])):
            top_names.append(top_track_response["items"][i]["name"])
            top_ids.append(top_track_response["items"][i]["id"])
        # mocked here after spotify recommendation deprecation
        with patch.object(spotify, 'recommendations', return_value = get_mocked_personalized_recommendation()):
            recs_response = spotify.recommendations(seed_artists=top_artists, seed_genres=None, seed_tracks=top_ids, limit=5, country=None)
            #recs_response = get_mocked_personalized_recommendation()
            recs = []
            for i in range(len(recs_response['tracks'])):
                song = {}
                song['title'] = recs_response['tracks'][i]['name']
                artists = []
                for j in range(len(recs_response['tracks'][i]['artists'])):
                    artists.append(recs_response['tracks'][i]['artists'][j]['name'])
                song['artists'] = artists
                recs.append(song)
            print(recs)
            return jsonify({'recommended_songs' : recs, 'token' : access_token}), 200
        
    except spotipy.SpotifyException:
        return jsonify({'error': 'Failed to fetch top tracks'}), 400

@app.route('/api/genius-facts', methods = ['POST'])
def get_top_5_genius_facts():

    genius = Genius(GENIUS_API_CLIENT_ACCESS_TOKEN, timeout=25, retries=3)
    
    try:
        data = request.json
        recs = data.get('songs', [])
        overall_comments = {}

        for spotify_song in recs:
            title = spotify_song['title']
            artists = spotify_song['artists']

            if title == "Say My Name":
                time.sleep(1) # simulating time it takes for Genius request
                overall_comments["Say My Name"] = "Destiny's Child released 'Say My Name' in 1999 as the third single from their second album Writings on the Wall. \
                    This album was their breakthrough success, and this song specifically represented a crucial moment in this band's future. This song was recorded by the four original members of the band: Beyoncé Knowles, Kelly Rowland, LeToya Luckett, and LaTavia Roberson. However when the video dropped, LeToya and LaTavia were conspicuously absent and replaced with two new girls: Michelle Williams (who remained in Destiny's Child until their final album in 2004) and Farrah Franklin (who lasted five months). LeToya and LaTavia told MTV News that they didn't know they had been dropped from the band until they saw the music video, though Beyoncé and Kelly denied this. \
                    Williams met the band while touring with R&B singer Monica, and was pursuing an interest in criminal justice when she got called in to shoot the “Say My Name” video. She told Huffington Post that the “Say My Name” video shoot happened at a pivotal point in her life. \
                    Before I joined Destiny's Child, I was supposed to see an autopsy. My uncle called the county coroner and arranged for me to shadow her. But I couldn't make it because on the day of, I was shooting the 'Say My Name' video… So it was like, what do you want to do with life: 'Say My Name' or autopsy \
                    This song was Destiny's Child's first collaboration with the esteemed R&B producer Darkchild a.k.a. Rodney Jerkins. He produced this song and wrote it alongside his brother Fred Jerkins III and his frequent collaborator LaShawn Daniels. Beyoncé remembered not liking his first attempt at the track. She told the Guardian: \
                    I don't think he liked it either. There was just too much stuff going on it. It just sounded like this jungle…I don't even know to this day how we wrote that song over that track. My dad came in to the studio and said, 'Rodney's done a new mix of that song that you hate—you have to listen to it.'..He had turned it into an amazing, timeless R&B record. It was one of the best songs we ever had, one of the best he's ever produced. \
                    Fred Jerkins told Billboard that the girls liked the first version, just not as much as they liked the second version. The song was a major boost for Darkchild's career; he ended up working with more Destiny’s Child frequently throughout their career, as well as produced songs for Michael Jackson, Toni Braxton, and Whitney Houston. \
                    Kelly Rowland told Pop Justice that this song is her favorite Destiny's Child track. \
                    It was so much fun to record and we crossed over with that song into a whole new world and it was amazing for us. Our audience got bigger."
                
                overall_comments["So What"] = "“So What” is a pop-rock song, written during a separation between P!nk and her husband Carey Hart. \n \
                Funnily enough, Hart features in the video for this song, because by the time P!nk's “Funhouse” album was nearing release, P!nk and Carey were back together, but P!nk decided to keep this track in as she felt it was important due to its emotional subject matter. \n \
                P!nk and Carey continued to be on and off with each other until they took part in marriage counselling and have now been together solidly since February 2010, and had their first child together, Willow, in June 2011, who went on to appear in the music video for P!nk's 2013 single “True Love”."
                
                overall_comments["Last Friday Night (T.G.I.F)"] = "“Last Friday Night (T.G.I.F.)” is an ode to partying heavily. In the music video, Perry (portraying her alter ego, Kathy Beth Terry) celebrates a party at her house on a Friday night. As much as Kathy regrets everything that she did on that Friday night, she wants nothing more than to do it all again next week. The acronym “T.G.I.F” stands for “Thank God/Goodness It's Friday,” hence the second part of the title. \n \
                    The song became Katy Perry's fifth consecutive number-one Hot 100 single from the album. With “Last Friday Night (T.G.I.F.),” Perry broke a record becoming the first woman in the 53-year history of Billboard to have five of her singles from the same album reach number one on the Billboard Hot 100."
                
                overall_comments["Who You Are"] = "This song is all about Jessie reassuring people that it's okay to be sad sometimes, and it's okay to cry about it, as long as you promise to stay true to who you are and not become somebody else. \n \
                    Jessie said she wrote this whilst going through a phase in her life where she didn't know who she was any more and was scared of that. This song is for her too, and it reminds us that celebrities and singers aren't unphasable and untouchable and have feelings too."
                overall_comments["You Don't Know My Name"] = "“You Don't Know My Name” is the lead single of Alicia's second studio album The Diary Of Alicia Keys; the song won a Grammy Award for Best R&B Song in 2005. \n \
                    The track is built around a sample from the 1970s New York group The Main Ingredient's “Let Me Prove My Love to You”."
                break
            elif title == "Alright":
                time.sleep(1)
                overall_comments["Alright"] = "Monét's “Alright” is a bold R&B anthem celebrating self-empowerment and unapologetic sensuality. In this track, Monét speaks to the noncommittal nature of modern relationships, talking about how she views sexual partners as almost disposable, fully embracing and reclaiming the promiscuity that she has been labelled with. \n \
                    With candid lyricism and sultry vocals, she declares independence in the chorus, repeating the mantra that life is “Alright.” The song captures the essence of resilience and individuality, as Monét skillfully combines provocative storytelling with infectious beats by iconic producer Kaytranada. \n \
                        “Alright” stands as a testament to Monét's artistry, offering listeners a liberating journey through the complexities of relationships and self-discovery."
                
                overall_comments["Right My Wrongs"] = "The 14th and final track on Bryson Tiller's highly anticipated debut album, T R A P S O U L."
                overall_comments["Awkward"] = "“Awkward” is one of the 7 tracks SZA released for the Deluxe version of her debut album, CTRL celebrating its 5 years anniversary. \n \
                    The lyrics have SZA wondering if making things awkward between her and a friend after crossing a few lines was worth it. She hopes it becomes more than just a friendship, but doesn't know if the feelings are reciprocated."
                break
            elif title == "Coming Back (feat. SZA)":
                time.sleep(1)
                overall_comments["Coming Back (feat. SZA)"] = "This is the first collaboration between Blake and SZA. However, they did both appear on the same project, Black Panther: The Album (Music from and Inspired By), with SZA featuring on “All The Stars,” and Blake featuring on “Bloody Waters” and “King's Dead”."
                overall_comments["Kiss It Better"] = "“Kiss It Better” tells the story of a broken relationship. She is aware that no one does it like him so instead of arguing all night she 'kisses it better'. \n \
                    A preview of the song first appeared in December 2014—over a year before the release of Anti—on Rihanna's Instagram page, featuring guitarist Nuno Bettencourt. \
                    https://www.instagram.com/p/wZn2FQBMxx/ \n \
                    In December 2015, a few weeks before the album's release, the song's producer, Glass John, took to Twitter and ranted about the delays behind Rihanna's album. According to Glass John, “Kiss It Better” was supposed to be the first single for Anti, but Travi$ Scott convinced Rihanna to go with “Bitch Better Have My Money” instead. (Travi$ denied John's claims on Snapchat.) \n \
                    John also released a now-deleted 60-second video preview of the track and threatened, if you don't say your [sic] sorry Kiss It Better isn't going to come out… how about that? \ "
                overall_comments["Saturn"] = "This song explains SZA's confusion of this world. In her mind its dull and how's she's tired of the same thing, she also expresses how life is a pattern to her. For example, In Verse 1, its like she craves for something new and how if there's another universe out there she's ready for it."
                overall_comments["Timeless (with Playboi Carti)"] = "“Timeless” is expected to be on The Weeknd's album Hurry Up Tomorrow. The song was performed live during his concert in São Paulo on September 7, 2024, with Carti also performing on the stage. A demo of the song leaked on September 25, 2024. On the same day, The Weeknd took to his Instagram to post a photo of him with Carti with the caption stating: \n \
                    TIMELESS // TOMORROW NIGHT \n \
                    Shortly after the post, Carti reposts the image of the two on his Instagram story to build up even more hype. \
                    On September 27, The Weeknd officially releases the song on all streaming platforms."
                overall_comments["Rude Boy"] = "The fourth single from Rihanna's fourth studio album Rated R was released on February 19, 2010. The song is about Rihanna taking control of her relationship, and more importantly during sex. \n \
                    According to Songfacts, Rihanna told Q magazine in January 2010: \n \
                    This is about the kind of street, bad boy that girls sometimes like. There's a danger and a swagger there."
                break
            elif title == "Bohemian Rhapsody":
                time.sleep(1)
                overall_comments["Bohemian Rhapsody"] = "Widely considered to be one of the greatest songs of all time, “Bohemian Rhapsody” was the first single released from Queen's fourth studio album, A Night at the Opera. It became an international success, reaching #1 in seven countries and peaking at #9 in the United States. Seventeen years after its initial release, “Bohemian Rhapsody” re-entered the pop charts in the US, peaking at #2 after being featured in the 1992 hit movie Wayne's World. In 2002, the song was listed at #1 in a Guinness World Records poll as Britain's favourite single of all time—ranking higher than four Beatles tracks and “Imagine” by John Lennon. \
                Complex and operatic both musically and lyrically, “Bohemian Rhapsody” (like Led Zeppelin's “Stairway to Heaven” and The Eagles' “Hotel California”) has attracted endless fan theories and commentary. The surviving band members have claimed that the narrative is based on the Faust legend; critics have found possible sources in opera and Freddie Mercury's personal biography; but like any good piece of art, it's open to interpretation.\
                    The word “Bohemian” seems to refer to a group of artists and musicians from the 19th century, known for defying convention and living with disregard for standards; as opposed to the region of Bohemia in the Czech Republic. Meanwhile the term “rhapsody” is a piece of classical music with distinct sections that are played as one movement. Rhapsodies often feature dense themes or narratives.\
                    As of December 2018, “Bohemian Rhapsody” is the most streamed song of the 20th century. \
                    “Bohemian Rhapsody” has got a very diverse song structure. It includes: \
                        \t • Intro (0:00-0:49) \n \
                        \t • Ballad section (0:49-2:37) \n \
                        \t • Brian May's guitar solo (2:37-3:05) \n \
                        \t• Operatic verse (3:05-4:07) \n \
                        \t • Hard-rock verse (4:07-4:54) \n \
                        \t • Coda (4:54-5:55) \n "
                overall_comments["Wanted Dead or Alive"] = "The song “Wanted Dead or Alive” is the third single off Slippery When Wet. It peaked at #7 on the Billboard Hot 100 chart, making Slippery When Wet the first glam metal album to have three singles on the top-10 of the chart, the other ones being “You Give Love a Bad Name” and “Livin' on a Prayer”. \
                The song title was also considered for the album's name, leading to a photo that would be repurposed as the single cover. \
                The song is about the life of a rock star, written in the perspective of a cowboy in the wild west. The band stated that it was extremely easy to write the lyrics because every one of them is based upon their actual experiences as a band."
                overall_comments["Amazing"] = "Co-writer Richie Supa told Fox the song's genesis came from a Narcotics Anonymous meeting he attended: \
                    I told Steven Tyler this woman stood up at a meeting and said: 'I kept the right ones out and let the wrong ones in,' and he said, 'yeah, I had an angel of mercy to see me through all my sin,'"
                overall_comments["I Get Around (Mono)"] = "“I Get Around” features a combination of surf guitars and doo-wop harmonies. Mike Love sings lead vocal on the verses, and sings the opening lines of the first chorus. Brian Wilson performs the rest of the lead vocals on the choruses. The driving bass line that carries the song was played by then unknown studio musician, Glen Campbell. Released in 1964, “I Get Around” was the first Beach Boys song to #1 on the Billboard Pop charts."
                overall_comments["Waterloo"] = "“Waterloo” was Swedish pop group ABBA's breakout song (and also the first single to be released under the name “ABBA”), winning the 1974 Eurovision Song Contest. \
                    The song metaphorically compares a woman “surrendering to her conqueror” (giving up resisting a man's advances) to Napoleon surrendering following his final defeat at the Battle of Waterloo in 1815."
                break
            else: # in case one day this works again
                song = genius.search_song(title, artists[0])

                if song is None:
                    continue

                song_data = genius.song(song.id, text_format='plain')
                overall_comments[title] = (song_data['song']['description']['plain'])


        '''
        for spotify_song in recs:
            title = spotify_song['title']
            artists = spotify_song['artists']
            song = genius.search_song(title, artists[0])

            if song is None:
                continue

            song_data = genius.song(song.id, text_format='plain')
            overall_comments[title] = (song_data['song']['description']['plain'])
        '''
        return jsonify({'genius_facts' : overall_comments}), 200
    
    except spotipy.SpotifyException:
        return jsonify({'error': 'Failed to fetch top tracks'}), 400


@app.route('/api/save-recommended', methods = ['POST'])
def add_recs_to_new_playlist():
    try:
        access_token = get_valid_token()
    except:
        return jsonify({'error': "Bad authorization token"}), 400
    
    if not access_token:
        return jsonify({'error': 'No valid token available. Need token for personalized recommendation'}), 400
    
    spotify = spotipy.Spotify(auth=access_token)
    try:
        data = request.json
        recs = data.get('songs', [])
        playlist_title = data.get('title', [])

        description = "Spotify Recommendation Generated Songs :)"
        user_info = spotify.current_user()['id']

        playlists_response = spotify.current_user_playlists()
        found_curr_playlist = False
        playlist_id = ""

        for playlist in playlists_response['items']:
            if playlist and playlist['name'] == playlist_title:
                found_curr_playlist = True
                playlist_id = playlist['id']

        if not found_curr_playlist:
            spotify.user_playlist_create(user_info, playlist_title, public=False, collaborative=False, description=description)

            for playlist in spotify.current_user_playlists()['items']:
                if playlist and playlist['name'] == playlist_title:
                    found_curr_playlist = True
                    playlist_id = playlist['id']
        
        tracks = [("Alright", "Victoria Monet"),
        ("NVMD", "Denise Julia"),
        ("Right My Wrongs", "Bryson Tiller"),
        ("Shameless", "Avenoir"),
        ("Awkward", "Sza")]

        track_ids = []
        for spotify_song in recs:
            title = spotify_song['title']
            artist = spotify_song['artists'][0]
            query = f"track:{title} artist:{artist}"
            results = spotify.search(q=query, type="track", limit=1)

            if results['tracks']['items']:
                #print(results['tracks']['items'][0])
                #track_ids['items'].append(results['tracks']['items'][0])
                track_ids.append(results['tracks']['items'][0]['id'])
        if track_ids:
            spotify.user_playlist_add_tracks(user_info, playlist_id, track_ids)
        return jsonify({'success_upload' : 'Uploaded playlists to Spotify'}), 200

    except spotipy.SpotifyException:
        return jsonify({'error': 'Failed to upload recommendations'}), 400