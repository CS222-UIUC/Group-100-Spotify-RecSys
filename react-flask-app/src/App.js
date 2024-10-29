import React, { useState, useEffect } from 'react';
import './App.css';

function App() {
  const [currentTime, setCurrentTime] = useState(0);
  const [name, setName] = useState('');
  const [responseMessage, setResponseMessage] = useState('');

  useEffect(() => {
    fetch('/api/time')
      .then(res => res.json())
      .then(data => {
        setCurrentTime(data.time);
      });
  }, []);

  const handleSendMessage = async () => {
    console.log("Testing send message of name")
    const response = await fetch('/api/send-message', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ name }),
    });
    const data = await response.json();
    setResponseMessage(data.responseMessage);
  };

  const handleSpotifyLogin = () => {
    console.log("Redirecting to Spotify login...");
    window.open('http://localhost:5000/api/spotify-login', '_self');
};

  return (

    <div className="App">
      <header className="App-header">
        <p>The current time is {currentTime}.</p>
        <input
          type="text"
          value={name}
          onChange={e => setName(e.target.value)}
          placeholder="Enter your name"
        />
        <button onClick={handleSendMessage}>Submit</button>
        <p>{responseMessage}</p>

        <button onClick={handleSpotifyLogin}>Login with Spotify</button>
      </header>
    </div>
  );
}

export default App;
