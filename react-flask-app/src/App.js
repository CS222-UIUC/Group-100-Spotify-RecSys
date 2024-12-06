
import React, { useState, useEffect } from 'react';
import { BrowserRouter, Routes, Route, Link } from 'react-router-dom';
import Login from './Login';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Login />} />
        <Route path="/api/spotify-callback" element={<Login />} />
      </Routes>
    </BrowserRouter>
  );
}
export default App;

