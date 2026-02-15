import React from 'react';
import { ToggleButtonGroup, ToggleButton, Box, useMediaQuery, useTheme } from '@mui/material';

/**
 * TimeRangeSelector component allows users to select predefined time ranges
 * for viewing historical data. Responsive design adapts to mobile screens.
 * 
 * @param {Object} props
 * @param {string} props.value - Currently selected time range
 * @param {Function} props.onChange - Callback when selection changes
 * @param {Array} props.options - Array of time range options
 */
const TimeRangeSelector = ({ 
  value, 
  onChange, 
  options = [
    { label: 'Last 24 Hours', value: '24h' },
    { label: 'Last 7 Days', value: '7d' },
    { label: 'Last 30 Days', value: '30d' },
  ] 
}) => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));
  
  const handleChange = (event, newValue) => {
    if (newValue !== null) {
      onChange(newValue);
    }
  };

  return (
    <Box sx={{ display: 'flex', justifyContent: 'center', my: 2 }}>
      <ToggleButtonGroup
        value={value}
        exclusive
        onChange={handleChange}
        aria-label="time range selector"
        color="primary"
        orientation={isMobile ? "vertical" : "horizontal"}
        fullWidth={isMobile}
        sx={{
          // Touch-friendly button sizes on mobile
          '& .MuiToggleButton-root': {
            minHeight: isMobile ? 44 : 36,
            fontSize: isMobile ? '0.875rem' : '0.875rem',
            px: isMobile ? 2 : 1.5,
          },
        }}
      >
        {options.map((option) => (
          <ToggleButton
            key={option.value}
            value={option.value}
            aria-label={option.label}
          >
            {option.label}
          </ToggleButton>
        ))}
      </ToggleButtonGroup>
    </Box>
  );
};

export default TimeRangeSelector;
