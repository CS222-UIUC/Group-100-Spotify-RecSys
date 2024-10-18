import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react'; 
import App from './App';

global.fetch = jest.fn();

describe('App Component', () => {
  afterEach(() => {
    jest.clearAllMocks(); 
  });

  test('fetches time', async () => {
    fetch.mockResolvedValueOnce({
      json: jest.fn().mockResolvedValueOnce({ time: '12:00 PM' }), 
    });

    render(<App />);
    
    const timeElement = await screen.findByText(/The current time is 12:00 PM/i);
    expect(timeElement).toBeInTheDocument();
  });
    
});
