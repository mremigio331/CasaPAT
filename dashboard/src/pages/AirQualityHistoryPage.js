import { useState, useEffect } from 'react';
import {
  Container,
  Typography,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Button,
  Alert,
  Paper,
  Grid,
} from '@mui/material';
import RefreshIcon from '@mui/icons-material/Refresh';
import LoadingSpinner from '../components/LoadingSpinner';
import TimeRangeSelector from '../components/TimeRangeSelector';
import AirQualityChart from '../components/AirQualityChart';
import useGetAllAirDevices from '../hooks/air/useGetAllAirDevices';
import useGetAirDeviceHistory from '../hooks/air/useGetAirDeviceHistory';
import useResponsive from '../hooks/useResponsive';
import { TIME_RANGE_OPTIONS } from '../utils/constants';

/**
 * AirQualityHistoryPage component - Displays historical air quality data
 * with device selector, time range controls, and metric charts
 */
const AirQualityHistoryPage = () => {
  const [selectedDeviceId, setSelectedDeviceId] = useState('');
  const [timeRange, setTimeRange] = useState('24h');

  // Get responsive layout information
  const { isMobile } = useResponsive();

  // Fetch all devices to populate the device selector
  const {
    airDevices,
    isAirDevicesFetching,
    isAirDevicesError,
    airDevicesError,
    airDevicesRefetch,
  } = useGetAllAirDevices();

  // Fetch historical data for the selected device
  const {
    airDeviceHistory,
    isAirDeviceHistoryFetching,
    isAirDeviceHistoryError,
    airDeviceHistoryError,
    airDeviceHistoryRefetch,
  } = useGetAirDeviceHistory(
    selectedDeviceId,
    timeRange,
    !!selectedDeviceId // Only fetch if a device is selected
  );

  // Auto-select first device when devices are loaded
  useEffect(() => {
    if (airDevices && airDevices.length > 0 && !selectedDeviceId) {
      // airDevices is an array of strings (device names)
      setSelectedDeviceId(airDevices[0]);
    }
  }, [airDevices, selectedDeviceId]);

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
    airDevicesRefetch();
  };

  // Handle retry for history loading errors
  const handleRetryHistory = () => {
    airDeviceHistoryRefetch();
  };

  // Show loading spinner while devices are loading
  if (isAirDevicesFetching) {
    return (
      <Container maxWidth="lg" sx={{ mt: 4 }}>
        <LoadingSpinner size="large" message="Loading air quality devices..." />
      </Container>
    );
  }

  // Show error message if devices failed to load
  if (isAirDevicesError) {
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
          Failed to load air quality devices. {airDevicesError?.message || 'Please try again.'}
        </Alert>
      </Container>
    );
  }

  // Show message if no devices are available
  if (!airDevices || airDevices.length === 0) {
    return (
      <Container maxWidth="lg" sx={{ mt: 4 }}>
        <Alert severity="info">
          No air quality devices found. Please check your device configuration.
        </Alert>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ mt: isMobile ? 2 : 4, mb: isMobile ? 2 : 4, px: isMobile ? 1 : 3 }}>
      {/* Page Header */}
      <Typography variant={isMobile ? "h5" : "h4"} component="h1" gutterBottom>
        Air Quality History
      </Typography>
      <Typography variant="body1" color="text.secondary" paragraph>
        View historical air quality metrics for your sensors
      </Typography>

      {/* Device Selector */}
      <Paper elevation={2} sx={{ p: isMobile ? 2 : 3, mb: isMobile ? 2 : 3 }}>
        <FormControl fullWidth sx={{ mb: 2 }}>
          <InputLabel id="device-selector-label">Select Air Quality Device</InputLabel>
          <Select
            labelId="device-selector-label"
            id="device-selector"
            value={selectedDeviceId}
            label="Select Air Quality Device"
            onChange={handleDeviceChange}
          >
            {airDevices.map((deviceName) => (
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
      {isAirDeviceHistoryFetching && (
        <LoadingSpinner size="large" message="Loading air quality history..." />
      )}

      {/* Error State */}
      {isAirDeviceHistoryError && !isAirDeviceHistoryFetching && (
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
          Failed to load air quality history. {airDeviceHistoryError?.message || 'Please try again.'}
        </Alert>
      )}

      {/* Empty State */}
      {!isAirDeviceHistoryFetching && !isAirDeviceHistoryError && (!airDeviceHistory || airDeviceHistory.length === 0) && (
        <Alert severity="info" sx={{ mb: 3 }}>
          No air quality data found for the selected time range.
        </Alert>
      )}

      {/* Charts - Only show if data is available */}
      {!isAirDeviceHistoryFetching && !isAirDeviceHistoryError && airDeviceHistory && airDeviceHistory.length > 0 && (
        <Grid container spacing={isMobile ? 2 : 3}>
          {/* PM2.5 Chart */}
          <Grid item xs={12} md={6}>
            <Paper elevation={2} sx={{ p: isMobile ? 2 : 3 }}>
              <AirQualityChart 
                data={airDeviceHistory} 
                metric="PM25" 
                height={isMobile ? 250 : 300} 
              />
            </Paper>
          </Grid>

          {/* PM10 Chart */}
          <Grid item xs={12} md={6}>
            <Paper elevation={2} sx={{ p: isMobile ? 2 : 3 }}>
              <AirQualityChart 
                data={airDeviceHistory} 
                metric="PM10" 
                height={isMobile ? 250 : 300} 
              />
            </Paper>
          </Grid>

          {/* Temperature Chart */}
          <Grid item xs={12} md={6}>
            <Paper elevation={2} sx={{ p: isMobile ? 2 : 3 }}>
              <AirQualityChart 
                data={airDeviceHistory} 
                metric="temperature" 
                height={isMobile ? 250 : 300} 
              />
            </Paper>
          </Grid>

          {/* Humidity Chart */}
          <Grid item xs={12} md={6}>
            <Paper elevation={2} sx={{ p: isMobile ? 2 : 3 }}>
              <AirQualityChart 
                data={airDeviceHistory} 
                metric="humidity" 
                height={isMobile ? 250 : 300} 
              />
            </Paper>
          </Grid>
        </Grid>
      )}
    </Container>
  );
};

export default AirQualityHistoryPage;
