import React, { useState, useEffect } from 'react';
import {
  Box,
  Container,
  Typography,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Button,
  Alert,
  Paper,
} from '@mui/material';
import RefreshIcon from '@mui/icons-material/Refresh';
import LoadingSpinner from '../components/LoadingSpinner';
import TimeRangeSelector from '../components/TimeRangeSelector';
import DoorEventChart from '../components/DoorEventChart';
import useGetAllDoorDevices from '../hooks/door/useGetAllDoorDevices';
import useGetDoorDeviceHistory from '../hooks/door/useGetDoorDeviceHistory';
import useResponsive from '../hooks/useResponsive';
import { TIME_RANGE_OPTIONS } from '../utils/constants';
import { formatRelativeTime } from '../utils/dateFormatters';

/**
 * DoorHistoryPage component - Displays historical door sensor data
 * with device selector, time range controls, and event visualization
 */
const DoorHistoryPage = () => {
  const [selectedDeviceId, setSelectedDeviceId] = useState('');
  const [timeRange, setTimeRange] = useState('24h');

  // Get responsive layout information
  const { isMobile, isTablet } = useResponsive();

  // Fetch all devices to populate the device selector
  const {
    doorDevices,
    isDoorDevicesFetching,
    isDoorDevicesError,
    doorDevicesError,
    doorDevicesRefetch,
  } = useGetAllDoorDevices();

  // Fetch historical data for the selected device
  const {
    doorDeviceHistory,
    isDoorDeviceHistoryFetching,
    isDoorDeviceHistoryError,
    doorDeviceHistoryError,
    doorDeviceHistoryRefetch,
  } = useGetDoorDeviceHistory(
    selectedDeviceId,
    timeRange,
    !!selectedDeviceId // Only fetch if a device is selected
  );

  // Auto-select first device when devices are loaded
  useEffect(() => {
    if (doorDevices && doorDevices.length > 0 && !selectedDeviceId) {
      // doorDevices is an array of strings (device names)
      setSelectedDeviceId(doorDevices[0]);
    }
  }, [doorDevices, selectedDeviceId]);

  // Handle device selection change
  const handleDeviceChange = (event) => {
    setSelectedDeviceId(event.target.value);
  };

  // Handle time range change
  const handleTimeRangeChange = (newRange) => {
    setTimeRange(newRange);
  };

  // Handle retry for device loading errors
  const handleRetryDevices = () => {
    doorDevicesRefetch();
  };

  // Handle retry for history loading errors
  const handleRetryHistory = () => {
    doorDeviceHistoryRefetch();
  };

  // Show loading spinner while devices are loading
  if (isDoorDevicesFetching) {
    return (
      <Container maxWidth="lg" sx={{ mt: 4 }}>
        <LoadingSpinner size="large" message="Loading door devices..." />
      </Container>
    );
  }

  // Show error message if devices failed to load
  if (isDoorDevicesError) {
    return (
      <Container maxWidth="lg" sx={{ mt: 4 }}>
        <Alert
          severity="error"
          action={
            <Button color="inherit" size="small" onClick={handleRetryDevices}>
              <RefreshIcon sx={{ mr: 0.5 }} />
              Retry
            </Button>
          }
        >
          Failed to load door devices. {doorDevicesError?.message || 'Please try again.'}
        </Alert>
      </Container>
    );
  }

  // Show message if no devices are available
  if (!doorDevices || doorDevices.length === 0) {
    return (
      <Container maxWidth="lg" sx={{ mt: 4 }}>
        <Alert severity="info">
          No door devices found. Please check your device configuration.
        </Alert>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ mt: isMobile ? 2 : 4, mb: isMobile ? 2 : 4, px: isMobile ? 1 : 3 }}>
      {/* Page Header */}
      <Typography variant={isMobile ? "h5" : "h4"} component="h1" gutterBottom>
        Door Sensor History
      </Typography>
      <Typography variant="body1" color="text.secondary" paragraph>
        View historical door open/closed events for your door sensors
      </Typography>

      {/* Device Selector */}
      <Paper elevation={2} sx={{ p: isMobile ? 2 : 3, mb: isMobile ? 2 : 3 }}>
        <FormControl fullWidth sx={{ mb: 2 }}>
          <InputLabel id="device-selector-label">Select Door Device</InputLabel>
          <Select
            labelId="device-selector-label"
            id="device-selector"
            value={selectedDeviceId}
            label="Select Door Device"
            onChange={handleDeviceChange}
          >
            {doorDevices.map((deviceName) => (
              <MenuItem
                key={deviceName}
                value={deviceName}
              >
                {deviceName}
              </MenuItem>
            ))}
          </Select>
        </FormControl>

        {/* Time Range Selector */}
        <TimeRangeSelector
          value={timeRange}
          onChange={handleTimeRangeChange}
          options={TIME_RANGE_OPTIONS}
        />
      </Paper>

      {/* Loading State */}
      {isDoorDeviceHistoryFetching && (
        <LoadingSpinner size="large" message="Loading door history..." />
      )}

      {/* Error State */}
      {isDoorDeviceHistoryError && !isDoorDeviceHistoryFetching && (
        <Alert
          severity="error"
          action={
            <Button color="inherit" size="small" onClick={handleRetryHistory}>
              <RefreshIcon sx={{ mr: 0.5 }} />
              Retry
            </Button>
          }
          sx={{ mb: 3 }}
        >
          Failed to load door history. {doorDeviceHistoryError?.message || 'Please try again.'}
        </Alert>
      )}

      {/* Empty State */}
      {!isDoorDeviceHistoryFetching && !isDoorDeviceHistoryError && (!doorDeviceHistory || doorDeviceHistory.length === 0) && (
        <Alert severity="info" sx={{ mb: 3 }}>
          No door events found for the selected time range.
        </Alert>
      )}

      {/* Chart and Event List - Only show if data is available */}
      {!isDoorDeviceHistoryFetching && !isDoorDeviceHistoryError && doorDeviceHistory && doorDeviceHistory.length > 0 && (
        <Box sx={{ 
          display: 'flex', 
          flexDirection: isMobile ? 'column' : 'column',
          gap: isMobile ? 2 : 3 
        }}>
          {/* Door Event Chart */}
          <Paper elevation={2} sx={{ p: isMobile ? 2 : 3 }}>
            <DoorEventChart data={doorDeviceHistory} height={isMobile ? 300 : 400} />
          </Paper>

          {/* Event List */}
          <Paper elevation={2} sx={{ p: isMobile ? 2 : 3 }}>
            <Typography variant="h6" gutterBottom>
              Event List
            </Typography>
            <Box sx={{ maxHeight: isMobile ? 300 : 400, overflow: 'auto' }}>
              {doorDeviceHistory.map((event, index) => (
                <Box
                  key={index}
                  sx={{
                    display: 'flex',
                    flexDirection: isMobile ? 'column' : 'row',
                    justifyContent: 'space-between',
                    alignItems: isMobile ? 'flex-start' : 'center',
                    p: isMobile ? 1.5 : 2,
                    gap: isMobile ? 0.5 : 0,
                    borderBottom: index < doorDeviceHistory.length - 1 ? '1px solid #e0e0e0' : 'none',
                    '&:hover': {
                      backgroundColor: '#f5f5f5',
                    },
                  }}
                >
                  <Box>
                    <Typography
                      variant="body1"
                      sx={{
                        fontWeight: 'bold',
                        color: event.status === 'open' ? '#f44336' : '#4caf50',
                        textTransform: 'capitalize',
                      }}
                    >
                      {event.status}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      {formatRelativeTime(event.timestamp)}
                    </Typography>
                  </Box>
                  <Typography variant="caption" color="text.secondary">
                    {new Date(event.timestamp).toLocaleString()}
                  </Typography>
                </Box>
              ))}
            </Box>
          </Paper>
        </Box>
      )}
    </Container>
  );
};

export default DoorHistoryPage;
