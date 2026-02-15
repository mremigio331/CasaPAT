import React from 'react';
import { Box, CircularProgress, Typography } from '@mui/material';

/**
 * LoadingSpinner component displays a centered loading indicator
 * with an optional message below it.
 * 
 * @param {Object} props
 * @param {'small' | 'medium' | 'large'} props.size - Size of the spinner
 * @param {string} props.message - Optional message to display below spinner
 */
const LoadingSpinner = ({ size = 'medium', message }) => {
  const sizeMap = {
    small: 24,
    medium: 40,
    large: 60,
  };

  return (
    <Box
      display="flex"
      flexDirection="column"
      alignItems="center"
      justifyContent="center"
      minHeight="200px"
      gap={2}
    >
      <CircularProgress size={sizeMap[size]} />
      {message && (
        <Typography variant="body2" color="text.secondary">
          {message}
        </Typography>
      )}
    </Box>
  );
};

export default LoadingSpinner;
