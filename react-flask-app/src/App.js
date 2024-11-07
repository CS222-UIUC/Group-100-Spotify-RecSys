import React, { useState, useEffect } from 'react';
//import { useLocation, useNavigate } from 'react-router-dom'
import './App.css';

function App() {

  const [topTracks, setTopTracks] = useState(null);
  const [token, setToken] = useState(null);
  //const [searchParams, setSearchParams] = useSearchParams();
  //const location = useLocation();
  //const history = useNavigate();

  useEffect(() => {

    const urlParams = new URLSearchParams(window.location.search);
    const code = urlParams.get('code');
    if (code) {
      exchangeCodeForToken(code);
      urlParams.delete('code');
      const newUrl = `${window.location.pathname}`;
      window.history.replaceState({}, document.title, newUrl);
    }
  }, []);

  
  const handleSpotifyLogin = () => {
    window.open('http://localhost:5000/api/spotify-login', '_self');
  };

  const exchangeCodeForToken = async (code) => {
    try {
      const response = await fetch(`/api/spotify-callback?code=${code}`);
      const data = await response.json();
      if (data.access_token) {
        setToken(data.access_token);
        console.log('Spotify token retrieved successfully.');
      } else {
        console.error('Failed to retrieve Spotify token.');
      }
    } catch (error) {
      console.error('Error exchanging code for token:', error);
    }
  };

  const fetchTopTracks = async () => {
    try {
      const response = await fetch('/api/display-songs', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ token: null }), 
      });
      const data = await response.json();
      if (data.top_tracks) {
        setTopTracks(data.top_tracks);
        setToken(data.access_token);
      } else {
        console.error('Failed to fetch top tracks:', data.error);
      }
    } catch (error) {
      console.error('Error fetching top tracks:', error);
    }
  };

  return (
    <div className="App">
      <header className="App-header">

        <button onClick={handleSpotifyLogin}>Login with Spotify</button>
        
        <div>
          <button onClick={fetchTopTracks}>Get Top 5 Tracks</button>
          {topTracks && (
            <div>
              <h3>Your Top 5 Tracks:</h3>
              <pre>{JSON.stringify(topTracks, null, 2)}</pre>
            </div>
          )}
        </div>
      </header>
    </div>
  );
}

export default App;
