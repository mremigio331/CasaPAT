import React from 'react';
import { Container, Typography, Box, Button, Alert, Grid } from '@mui/material';
import useGetAllAirDevices from '../hooks/air/useGetAllAirDevices';
import useGetAllDoorDevices from '../hooks/door/useGetAllDoorDevices';
import useGetLatestAirReading from '../hooks/air/useGetLatestAirReading';
import useGetLatestDoorReading from '../hooks/door/useGetLatestDoorReading';
import LoadingSpinner from '../components/LoadingSpinner';
import DeviceStatusCard from '../components/DeviceStatusCard';

/**
 * DeviceCard component that fetches and displays latest reading for an air quality device
 */
const AirDeviceCard = ({ deviceName }) => {
  const { 
    latestAirReading, 
    isLatestAirReadingFetching, 
    isLatestAirReadingError, 
    lastUpdated 
  } = useGetLatestAirReading(deviceName);

  // Determine status based on data
  const getStatus = () => {
    if (isLatestAirReadingFetching) return 'Loading...';
    if (isLatestAirReadingError) return 'Error';
    if (!latestAirReading) return 'No data';

    // For air quality devices, show PM2.5 as primary metric
    return `PM2.5: ${latestAirReading.PM25 || 'N/A'} µg/m³`;
  };

  // Determine if device is online based on data availability
  const isOnline = !isLatestAirReadingError && !!latestAirReading;

  // Get timestamp from data or lastUpdated
  const timestamp = latestAirReading?.Timestamp || lastUpdated || new Date();

  return (
    <DeviceStatusCard
      deviceId={deviceName}
      deviceName={deviceName}
      deviceType="Air Quality"
      status={getStatus()}
      lastUpdated={timestamp}
      isOnline={isOnline}
    />
  );
};

/**
 * DeviceCard component that fetches and displays latest reading for a door sensor device
 */
const DoorDeviceCard = ({ deviceName }) => {
  const { 
    latestDoorReading, 
    isLatestDoorReadingFetching, 
    isLatestDoorReadingError, 
    lastUpdated 
  } = useGetLatestDoorReading(deviceName);

  // Determine status based on data
  const getStatus = () => {
    if (isLatestDoorReadingFetching) return 'Loading...';
    if (isLatestDoorReadingError) return 'Error';
    if (!latestDoorReading) return 'No data';

    // For door sensors, show open/closed status
    return latestDoorReading.door_status || 'Unknown';
  };

  // Determine if device is online based on data availability
  const isOnline = !isLatestDoorReadingError && !!latestDoorReading;

  // Get timestamp from data or lastUpdated
  const timestamp = latestDoorReading?.timestamp || lastUpdated || new Date();

  return (
    <DeviceStatusCard
      deviceId={deviceName}
      deviceName={deviceName}
      deviceType="Door Sensor"
      status={getStatus()}
      lastUpdated={timestamp}
      isOnline={isOnline}
    />
  );
};

/**
 * HomePage component displays all devices grouped by type
 * Shows current status for air quality and door sensors
 */
const HomePage = () => {
  const { 
    airDevices, 
    isAirDevicesFetching, 
    isAirDevicesError, 
    airDevicesError, 
    airDevicesRefetch 
  } = useGetAllAirDevices();

  const { 
    doorDevices, 
    isDoorDevicesFetching, 
    isDoorDevicesError, 
    doorDevicesError, 
    doorDevicesRefetch 
  } = useGetAllDoorDevices();

  const isLoading = isAirDevicesFetching || isDoorDevicesFetching;
  const isError = isAirDevicesError || isDoorDevicesError;
  const error = isAirDevicesError ? airDevicesError : isDoorDevicesError ? doorDevicesError : null;

  // Display loading spinner while fetching devices
  if (isLoading) {
    return (
      <Container maxWidth="lg" sx={{ mt: 4 }}>
        <LoadingSpinner size="large" message="Loading devices..." />
      </Container>
    );
  }

  // Display error message with retry button
  if (isError) {
    return (
      <Container maxWidth="lg" sx={{ mt: 4 }}>
        <Alert 
          severity="error" 
          sx={{ mb: 2 }}
          action={
            <Button color="inherit" size="small" onClick={() => {
              airDevicesRefetch();
              doorDevicesRefetch();
            }}>
              Retry
            </Button>
          }
        >
          {error?.message || 'Failed to load devices. Please try again.'}
        </Alert>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Typography variant="h4" component="h1" gutterBottom>
        Device Dashboard
      </Typography>
      
      {/* Air Quality Sensors Section */}
      <Box sx={{ mt: 4 }}>
        <Typography variant="h5" component="h2" gutterBottom sx={{ mb: 3 }}>
          Air Quality Sensors
        </Typography>
        {airDevices.length === 0 ? (
          <Typography variant="body2" color="text.secondary">
            No air quality sensors found
          </Typography>
        ) : (
          <Grid container spacing={3}>
            {airDevices.map((deviceName) => (
              <Grid item xs={12} sm={6} md={4} key={deviceName}>
                <AirDeviceCard deviceName={deviceName} />
              </Grid>
            ))}
          </Grid>
        )}
      </Box>

      {/* Door Sensors Section */}
      <Box sx={{ mt: 4 }}>
        <Typography variant="h5" component="h2" gutterBottom sx={{ mb: 3 }}>
          Door Sensors
        </Typography>
        {doorDevices.length === 0 ? (
          <Typography variant="body2" color="text.secondary">
            No door sensors found
          </Typography>
        ) : (
          <Grid container spacing={3}>
            {doorDevices.map((deviceName) => (
              <Grid item xs={12} sm={6} md={4} key={deviceName}>
                <DoorDeviceCard deviceName={deviceName} />
              </Grid>
            ))}
          </Grid>
        )}
      </Box>
    </Container>
  );
};

export default HomePage;
