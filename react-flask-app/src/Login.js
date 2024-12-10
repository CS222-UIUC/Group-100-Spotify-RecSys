import React, { useState, useEffect } from 'react';
import Button from '@mui/material/Button';
import IconButton from '@mui/material/IconButton';
import SaveAltIcon from '@mui/icons-material/SaveAlt';
import AddIcon from '@mui/icons-material/Add';
import Select from 'react-select'
import Slider from '@mui/material/Slider';
import { genreOptions } from './Constants';
import TextField from '@mui/material/TextField';
import Dialog from '@mui/material/Dialog';
import DialogActions from '@mui/material/DialogActions';
import DialogContent from '@mui/material/DialogContent';
import DialogContentText from '@mui/material/DialogContentText';
import DialogTitle from '@mui/material/DialogTitle';
import { Container } from '@mui/material';
import Card from '@mui/material/Card';
import CardContent from '@mui/material/CardContent';
import './App.css';
import { SongCard } from './Songcard';

function Login() {
  // personalized recc + login details

  const [token, setToken] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  // general recommendation
  const [selectedGenres, setSelectedGenres] = useState([]);
  const [danceability, setDanceability] = useState(0.5);
  const [tempo, setTempo] = useState(120);

  // playlist setting states
  const [playlistOpen, setPlaylistOpen] = useState(false);
  const [playlistTitle, setPlaylistTitle] = useState("");

  // genius and song fact states
  const [openFact, setOpenFact] = useState(false);
  const [currFact, setCurrFact] = useState(false);
  const [currRecc, setCurrRecc] = useState(null);

  // create new value for overall recommendations
  const [recommendationDisplay, setRecommendationDisplay] = useState(null);
  const [geniusFacts, setGeniusFacts] = useState(null);
  const [transformedRecc, setTransformedRecc] = useState([]);

  // for switching between personalized and general tabs
  const [showGeneral, setShowGeneral] = useState(false);
  const [showPersonal, setShowPersonal] = useState(false);

  useEffect(() => { 
    // extracting code to exchange for token from Spotify
    const urlParams = new URLSearchParams(window.location.search);
    const code = urlParams.get('code');
    if (code) {
      exchangeCodeForToken(code);
      urlParams.delete('code');
      const newUrl = 'http://localhost:3000';
      window.history.replaceState({}, document.title, newUrl);
    }
  }, []);


  useEffect(() => {
    // modifys data for easier input into mui cards
    const transform_song_facts = (songs, facts) => {
      if (!songs) {
        console.log('No song data avail');
        return [];
      }
      return songs.map((song) => ({
        title: song.title,
        artist: Array.isArray(song.artists) ? song.artists.join(', ') : song.artists,
        fact: facts ? facts[song.title] : null
      }));
    };
    
    const transformed = transform_song_facts(recommendationDisplay, geniusFacts);
    console.log('Transformed recommendations:', transformed);
    setTransformedRecc(transformed);
  }, [recommendationDisplay, geniusFacts]);

  const handleSpotifyLogin = () => {
    // opening redirect URL
    window.location.href = 'http://localhost:5000/api/spotify-login';
  };

  const handleSpotifyLogout = () => {

    window.location.href = 'http://localhost:3000'
    setToken(null); // need to clear display
    setRecommendationDisplay(null);
    setGeniusFacts(null);
    setTransformedRecc([]);
  }

  const exchangeCodeForToken = async (code) => {
    // exchange function
    try {
      const response = await fetch(`/api/spotify-callback?code=${code}`);
      const data = await response.json();
      if (data.access_token) {
        setToken(data.access_token);
        console.log('Spotify token retrieved successfully');
      } else {
        console.error('Failed to retrieve Spotify token', data.error);
      }
    } catch (error) {
      console.error('Failed to retrieve Spotify token', error);
    }
  };


  const handleRecommendations = async () => {
    // generates general recommendations, currently mocked

    setShowPersonal(false);
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
        setRecommendationDisplay(data.recommended_songs);
        await fetchGeniusFacts(data.recommended_songs);
      } else {
        console.error(data.error || 'Failed to fetch recommendations');
      }
    } catch (error) {
      console.error('Failed to fetch recommendations', error);
    }
  };


  const fetchTopTracks = async () => {
    // fetches the top tracks for a user on artists and top tracks
    setIsLoading(true);
    setShowGeneral(false);
    setShowPersonal(true);
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
        setRecommendationDisplay(data.top_tracks);
        await fetchGeniusFacts(data.top_tracks);
        setToken(data.token);
      } else {
        console.error('Failed to fetch top tracks', data.error);
      }
    } catch (error) {
      console.log('Failed to fetch top tracks', error);
    } finally {
      setIsLoading(false);
    }
  };

  const fetchPersonalizedRecommended = async () => {
    // fetches the personalized recommendations for a user, currently mocked
    //setIsLoading(true);
    setShowGeneral(false);
    setShowPersonal(true);
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
        setRecommendationDisplay(data.recommended_songs);
        setToken(data.token);
        await fetchGeniusFacts(data.recommended_songs);
      } else {
        console.error('Failed to fetch recommendations', data.error);
      }
    } catch (error) {
      console.error('Error fetching recommendations', error);
    }
  };

  const fetchGeniusFacts = async (songs = recommendationDisplay) => {
    // fetches the genius facts for a given recommendations
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
      console.error('Failed to fetch Genius facts', error);
    } finally {
      setIsLoading(false);
    }
  };


  const handleOpenFact = (recc) => {
    setOpenFact(true);
    setCurrRecc(recc);
  };

  const handleCloseFact = () => {
    setOpenFact(false);
    setCurrRecc(null);
  };

  const renderRecommendations = () => {
    if (!transformedRecc || transformedRecc.length === 0) return null;
    
    return (
      <Container>
          {transformedRecc.map((song, index) => (
            <SongCard 
              key={index}
              song={song}
              handleOpenFact={handleOpenFact}
            />
          ))}
      </Container>
    );
  };

  const renderGeneralDisplay = () => {
    return (
      <div className="recommendations">
      <h2>Recommendation Generator</h2>
        <div className="form-group">
          <label htmlFor="genres">Genres:</label>
          <Select 
            id="genres"
            isMulti
            options={genreOptions}
            value={selectedGenres}
            onChange={setSelectedGenres}
            isOptionDisabled={() => selectedGenres.length >= 5}
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
          <Button onClick={handleRecommendations} className="fetch-button" variant="contained">
            Generate
          </Button>
        </div>
      </div>)
  }
  
  const handlePlaylistOpen = () => {
    setPlaylistOpen(true);
  };

  const handlePlaylistClose = () => {
    setPlaylistOpen(false);
    setPlaylistTitle("");
  };

  const handleSavePlayList = async (songs = recommendationDisplay, title = playlistTitle) => {
    // handles saving recommendations to a given playlist
    setPlaylistOpen(false);
    if (!songs) return;
    try {
      const response = await fetch('/api/save-recommended', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          token,
          songs,
          title
        }),
      });
      const data = await response.json();
      if (response.ok) {
        console.log("Uploaded Spotify songs")
      } else {
        console.error('Unable to upload Spotify songs', data.error);
      }
    } catch (error) {
      console.error('Error uploading Spotify song recommendation', error);
    }
  }
  
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
              {renderGeneralDisplay()}
              {isLoading && <div className="loading">Generating Genius Facts...</div>}
              {renderRecommendations()}
            <Dialog 
              open={openFact} 
              onClose={handleCloseFact}
            >
              <DialogTitle>
                {currRecc?.title}
              </DialogTitle>
              <DialogContent>
                <DialogContentText>
                  {currRecc?.fact || "No additional Genius Facts"}
                </DialogContentText>
              </DialogContent>
              <DialogActions>
                <Button onClick={handleCloseFact}>Close</Button>
              </DialogActions>
            </Dialog>
          </div>
        ) : (
          <div>
            <button className="App-login-button" onClick={handleSpotifyLogout}>
              Logout
            </button>

            <div className="content-container">
              <div className="button-group">
                <Button onClick={fetchTopTracks} variant="contained" disabled={isLoading} className="fetch-button">
                  Get Top 5 Tracks
                </Button>
                <Button onClick={fetchPersonalizedRecommended} variant="contained" disabled={isLoading} className="fetch-button">
                  Get Personalized Recommendations
                </Button>
                <Button onClick={() => {setShowGeneral(!showGeneral); setShowPersonal(false);setRecommendationDisplay(null);
    setGeniusFacts(null);
    setTransformedRecc([]);}} variant="contained" disabled={isLoading} className="fetch-button">
                  {'Show General Recommendations'}
                </Button>
                <Button variant="contained" startIcon={<SaveAltIcon />} onClick={handlePlaylistOpen} className="fetch-button">
                  Save Recommendations
                </Button>
              </div>
              {showGeneral && renderGeneralDisplay()}
              {isLoading && <div className="loading">Generating Genius Facts...</div>}
              {renderRecommendations()}
            </div>

            <Dialog open={playlistOpen} onClose={handlePlaylistClose}>
              <DialogTitle>Playlist Name</DialogTitle>
              <DialogContent>
                <DialogContentText>
                  To write your recommendations to a playlist, please enter a title for your generated recommendations
                </DialogContentText>
                <TextField 
                  value={playlistTitle} 
                  onChange={(e) => setPlaylistTitle(e.target.value)} 
                  required 
                  id="outlined-basic" 
                  variant="outlined" 
                  fullWidth 
                  margin="dense"
                />
              </DialogContent>
              <DialogActions>
                <Button onClick={handlePlaylistClose}>Cancel</Button>
                <Button onClick={() => handleSavePlayList()} disabled={!playlistTitle}>Save</Button>
              </DialogActions>
            </Dialog>

            <Dialog 
              open={openFact} 
              onClose={handleCloseFact}
            >
              <DialogTitle>
                {currRecc?.title}
              </DialogTitle>
              <DialogContent>
                <DialogContentText>
                  {currRecc?.fact || "No additional Genius Facts"}
                </DialogContentText>
              </DialogContent>
              <DialogActions>
                <Button onClick={handleCloseFact}>Close</Button>
              </DialogActions>
            </Dialog>
          </div>
        )}
      </header>
    </div>
  );
}

export default Login;