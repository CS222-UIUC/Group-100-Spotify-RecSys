import logo from './logo.svg';
import './App.css';
import React, { useState, useEffect } from 'react';

function App() {
  const [currentTime, setCurrentTime] = useState(0);
  const [name, setName] = useState('');
  const [responseMessage, setResponseMessage] = useState('');

  useEffect(() => {
    // Fetch the current time from the backend
    fetch('/api/time')
      .then(res => res.json())
      .then(data => {
        setCurrentTime(data.time);
      });
  }, []);

  const handleSendMessage = async () => {
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
      </header>
    </div>
  );
}

export default App;
