import React, { useState, useEffect } from 'react';
import { Button as BaseButton, buttonClasses } from '@mui/base/Button';
import Select, { StylesConfig } from 'react-select'
import Slider from '@mui/material/Slider';
import Recommendations from './Recommendation';
import './App.css';


const genreOptions = [
  { value: 'acoustic', label: 'Acoustic' },
  { value: 'alt-rock', label: 'Alt-Rock' },
  { value: 'alternative', label: 'Alternative' },
  { value: 'blues', label: 'Blues' },
  { value: 'classical', label: 'Classical' },
  { value: 'country', label: 'Country' },
  { value: 'dance', label: 'Dance' },
  { value: 'edm', label: 'EDM' },
  { value: 'hip-hop', label: 'Hip-Hop' },
  { value: 'indie', label: 'Indie' },
  { value: 'k-pop', label: 'K-Pop' },
  { value: 'metal', label: 'Metal' },
  { value: 'pop', label: 'Pop' },
  { value: 'r-n-b', label: 'R&B' },
  { value: 'rock', label: 'Rock' },
  { value: 'sad', label: 'Sad' },
  { value: 'soul', label: 'Soul' },
  { value: 'study', label: 'Study' },
  { value: 'techno', label: 'Techno' },
  { value: 'work-out', label: 'Work-Out' }
];

function Login() {
  const [topTracks, setTopTracks] = useState(null);
  const [recommendedPersonalizedTracks, setRecommendedPersonalizedTracks] = useState(null);
  const [token, setToken] = useState(null);
  const [geniusFacts, setGeniusFacts] = useState(null);
  const [isLoading, setIsLoading] = useState(false);


  const [selectedGenres, setSelectedGenres] = useState([]);
  const [danceability, setDanceability] = useState(0.5);
  const [tempo, setTempo] = useState(120);
  const [recommendations, setRecommendations] = useState([]);


  useEffect(() => {
    const urlParams = new URLSearchParams(window.location.search);
    const code = urlParams.get('code');
    if (code) {
      exchangeCodeForToken(code);
      urlParams.delete('code');
      const newUrl = 'http://localhost:3000';
      window.history.replaceState({}, document.title, newUrl);
    }
  }, []);

  const handleSpotifyLogin = () => {
    window.location.href = 'http://localhost:5000/api/spotify-login';
  };

  const handleSpotifyLogout = () => {
    window.location.href = 'http://localhost:3000'
    setToken(null);
  }

  const exchangeCodeForToken = async (code) => {
    try {
      const response = await fetch(`/api/spotify-callback?code=${code}`);
      const data = await response.json();
      if (data.access_token) {
        setToken(data.access_token);
        console.log('Spotify token retrieved successfully.');
      } else {
        console.error('Failed to retrieve Spotify token.', data.error);
      }
    } catch (error) {
      console.error('Error exchanging code for token.', error);
    }
  };


  const handleRecommendations = async () => {
    const genres = selectedGenres.map(option => option.value);
    const requestData = {
      genres,
      danceability,
      tempo
    };

    try {
      const response = await fetch('/api/recc', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(requestData),
      });

      const data = await response.json();

      if (response.ok) {
        setRecommendations(data.recommended_songs || []);
      } else {
        console.error(data.error || 'Failed to fetch recommendations');
      }
    } catch (error) {
      console.error('Error fetching recommendations:', error);
    }
  };


  const fetchTopTracks = async () => {
    setIsLoading(true);
    try {
      const response = await fetch('/api/display-songs', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ token }),
      });
      const data = await response.json();
      if (response.ok) {
        setTopTracks(data.top_tracks);
        setToken(data.token);
      } else {
        console.error('Failed to fetch top tracks', data.error);
      }
    } catch (error) {
      console.log('Error fetching top tracks', error);
    } finally {
      setIsLoading(false);
    }
  };

  const fetchPersonalizedRecommended = async () => {
    //setIsLoading(true);
    try {
      const response = await fetch('/api/personal-recc', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ token }),
      });
      const data = await response.json();
      if (response.ok) {
        setRecommendedPersonalizedTracks(data.recommended_songs);
        setToken(data.token);

        await fetchGeniusFacts(data.recommended_songs);
      } else {
        console.error('Failed to fetch recommendations', data.error);
      }
    } catch (error) {
      console.error('Error fetching recommendations', error);
    }
  };

  const fetchGeniusFacts = async (songs = recommendedPersonalizedTracks) => {
    if (!songs) return;
    setIsLoading(true);
    try {
      const response = await fetch('/api/genius-facts', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          token,
          songs,
        }),
      });
      const data = await response.json();
      if (response.ok) {
        setGeniusFacts(data.genius_facts);
      } else {
        console.error('Failed to fetch Genius facts', data.error);
      }
    } catch (error) {
      console.error('Error fetching Genius facts', error);
    } finally {
      setIsLoading(false);
    }
  };

  const renderSongList = (songs, title) => {
    if (!songs) return null;
    return (
      <div className="song-list">
        <h3>{title}</h3>
        <ul>
          {songs.map((song, index) => (
            <li key={index}>
              {song.title} - {song.artists.join(', ')}
            </li>
          ))}
        </ul>
      </div>
    );
  };

  const renderGeniusFacts = () => {
    if (!geniusFacts) return null;
    
    return (
      <div className="genius-facts">
        <h3>Genius Facts</h3>
        {Object.entries(geniusFacts)
          .filter(([song, description]) => description && description !== '?') 
          .map(([song, description], index) => (
            <div key={index} className="song-fact">
              <h4>{song}</h4>
              <p>{description}</p>
            </div>
          ))}
      </div>
    );
  };


  return (
    <div className="App">
      <header className="App-header">
        <img src="/1200px-Spotify.png" className="App-spotify-logo" alt="Spotify logo" />
        <h1 className="App-title">Spotify Recommendation</h1>
        
        {!token ? (
          <div>
            <button className="App-login-button" onClick={handleSpotifyLogin}>
              Login with Spotify
            </button>
            
            <div className="recommendations">
              <h2>Get Recommendations</h2>
              <div className="form-group">
                <label htmlFor="genres">Select Genres:</label>
                <Select
                  id="genres"
                  isMulti
                  options={genreOptions}
                  value={selectedGenres}
                  onChange={setSelectedGenres}
                  isOptionDisabled={() => (selectedGenres.length >= 5 )} // figure out if can also disable if less than 1
                  className="genre-select"
                  classNamePrefix="select"
                />
              </div>
              <div className="form-group">
                <label htmlFor="danceability">Danceability: {danceability}</label>
                <Slider
                  id="danceability"
                  value={danceability}
                  onChange={(e, value) => setDanceability(value)}
                  min={0}
                  max={1}
                  step={0.01}
                />
              </div>
              <div className="form-group">
                <label htmlFor="tempo">Tempo: {tempo} BPM</label>
                <Slider
                  id="tempo"
                  value={tempo}
                  onChange={(e, value) => setTempo(value)}
                  min={60}
                  max={200}
                />
              </div>
              <div className="form-group">
                <button onClick={handleRecommendations} className="fetch-button">
                  Generate
                </button>
              </div>
              {renderSongList(recommendations, "")}
            </div>
          </div>
        ) : ( // logged in here 
        <div>
        <button className="App-login-button" onClick={handleSpotifyLogin}>
              Login with Spotify
            </button>

          <div className="content-container">
            <div className="button-group">
              <button onClick={fetchTopTracks} disabled={isLoading} className="fetch-button">
                Get Top 5 Tracks
              </button>
              <button onClick={fetchPersonalizedRecommended} disabled={isLoading} className="fetch-button">
                Get Personalized Recommendations
              </button>
            </div>
  
            {isLoading && <div className="loading">Loading...</div>}
            {renderSongList(topTracks, "Your Top 5 Tracks")}
            {!isLoading && (
              <>
                {renderSongList(recommendedPersonalizedTracks, "Your Personalized Recommendations")}
                {renderGeniusFacts()}
              </>
            )}
          </div>
          </div>
        )}
      </header>
    </div>
  );
  
}

export default Login;