import React from 'react';
import Card from '@mui/material/Card';
import CardContent from '@mui/material/CardContent';
import Typography from '@mui/material/Typography';
import IconButton from '@mui/material/IconButton';
import InfoIcon from '@mui/icons-material/Info';
import Box from '@mui/material/Box';

export const SongCard = ({ song, handleOpenFact }) => {
    return (
      <Card>
        <CardContent>
          <Box display="flex" justifyContent="space-between" alignItems="left">
            <Box>
              <h7>
                {song.title}
              </h7>
              <Typography color="green" variant="h6" alignItems="left">
                {song.artist}
              </Typography>
            </Box>
            
            {song.fact && (
              <IconButton onClick={(e) => {handleOpenFact(song);}}>
                <InfoIcon color="#1ed760"/>
              </IconButton >
            )}
          </Box>
        </CardContent>
      </Card>
    );
  };