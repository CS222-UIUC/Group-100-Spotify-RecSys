import React, { useState } from 'react';
import Select from 'react-select';
import Slider from '@mui/material/Slider';
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

function Recommendations() {
  const [selectedGenres, setSelectedGenres] = useState([]);
  const [danceability, setDanceability] = useState(0.5);
  const [tempo, setTempo] = useState(120);
  const [recommendations, setRecommendations] = useState([]);

  const handleFetchRecommendations = async () => {
    const genres = selectedGenres.map(option => option.value);
    const requestData = {
      genres,
      danceability,
      tempo
    };

    try {
      const response = await fetch('/api/recommendations', {
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

  return (
    <div className="recommendations">
      <h1>Get Spotify Recommendations</h1>
      <div className="form-group">
        <label htmlFor="genres">Select Genres:</label>
        <Select
          id="genres"
          isMulti
          options={genreOptions}
          value={selectedGenres}
          onChange={setSelectedGenres}
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
        <button onClick={handleFetchRecommendations} className="fetch-button">
          Get Recommendations
        </button>
      </div>
      {recommendations.length > 0 && (
        <div className="recommendations-list">
          <h2>Recommendations</h2>
          <ul>
            {recommendations.map((track, index) => (
              <li key={index}>
                {track.title} by {track.artists.join(', ')}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

export default Recommendations;
