# Group-100-Spotify-RecSys

Music is a universal language for everyone. As someone who enjoys listening to and discovering new music (with >1500 songs in one of ours' favorites playlist), we wanted an option to discover new listening tastes. We want to be able to create a recommendation service for users to find new music relative to the aspects of the songs they listen to and search for : ex. Genre, bpm, key, artist, track. We wanted to diverge from traditional recommendation systems by also including more niche information about the artist or song lyrics. This could give a user a more in-depth enjoyable experience that feels more connected, than a typical impersonal recommendation. The react-flask app is built on npx packages (create-react-app,  react-flask-app)

In this project, we are creating a React-Flask app. 
This project does the following:
1. Authenticates a user with Spotify on Login
2. Offers multitude of functions: Get top 5 tracks, get filtered recommendation, get personalized recommendation
3. Save playlist to your Spotify Account
## Developers
- Allison Daemicke: Implemented all backend and frontend functionalities for Spotify Recommendation
- Priya Datt: Wrote functions to gather recommendation data, tokenization, and genius facts from Spotify and Genius APIs


## Project Architecture
![screenshot](spotify_architecture/spotify_arch.png)

## Setup Instructions
To install all Python dependencies: 

```python
pip install -r requirements.txt
```
Ensure you also have Node.js and Python installed.

To install all React dependencies:
```
npm install
```

To run the React app, run the following:
```
cd react-flask-app && npm start
```

To run the Flask app, run the following:
```
cd react-flask-app/api/ && flask run
```


referred to [https://blog.miguelgrinberg.com/post/how-to-create-a-react--flask-project/page/2#comments] for react flask app tutorial
