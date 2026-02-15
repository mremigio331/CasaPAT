import React from 'react';
import { Card, CardContent, Typography, Box, Chip, useMediaQuery, useTheme } from '@mui/material';
import { formatRelativeTime, isStaleTimestamp } from '../utils/dateFormatters';
import { STALE_THRESHOLD } from '../utils/constants';

/**
 * DeviceStatusCard component displays device information with status and timestamp
 * Responsive design with touch-friendly tap targets for mobile
 * 
 * @param {Object} props
 * @param {string} props.deviceId - Unique device identifier
 * @param {string} props.deviceName - Display name of the device
 * @param {string} props.deviceType - Type of device (e.g., 'air', 'door')
 * @param {string|number} props.status - Current status value
 * @param {string|Date} props.lastUpdated - Timestamp of last update
 * @param {boolean} props.isOnline - Whether device is currently online
 */
const DeviceStatusCard = ({
  deviceId,
  deviceName,
  deviceType,
  status,
  lastUpdated,
  isOnline
}) => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));
  
  const timestamp = new Date(lastUpdated);
  const isStale = isStaleTimestamp(timestamp, STALE_THRESHOLD);
  
  // Determine status color based on device type and status value
  const getStatusColor = () => {
    if (!isOnline) return 'error';
    if (isStale) return 'warning';
    return 'success';
  };

  return (
    <Card 
      sx={{ 
        minWidth: isMobile ? 'auto' : 275, 
        mb: 2,
        // Touch-friendly tap target
        minHeight: isMobile ? 140 : 'auto',
      }}
    >
      <CardContent sx={{ p: isMobile ? 2 : 2.5 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: isMobile ? 1.5 : 2 }}>
          <Box>
            <Typography variant={isMobile ? "subtitle1" : "h6"} component="div" gutterBottom>
              {deviceName}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              {deviceType}
            </Typography>
          </Box>
          {!isOnline && (
            <Chip 
              label="Offline" 
              color="error" 
              size="small"
              sx={{ 
                // Touch-friendly size on mobile
                minHeight: isMobile ? 28 : 24,
                fontSize: isMobile ? '0.75rem' : '0.8125rem',
              }}
            />
          )}
        </Box>

        <Box sx={{ mb: isMobile ? 1 : 1 }}>
          <Typography variant="body2" color="text.secondary">
            Status:
          </Typography>
          <Typography variant={isMobile ? "h6" : "h5"} component="div">
            {status}
          </Typography>
        </Box>

        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <Box
            sx={{
              width: isMobile ? 10 : 8,
              height: isMobile ? 10 : 8,
              borderRadius: '50%',
              bgcolor: getStatusColor() === 'success' ? 'success.main' : 
                       getStatusColor() === 'warning' ? 'warning.main' : 
                       'error.main'
            }}
          />
          <Typography 
            variant="caption" 
            color={isStale ? 'warning.main' : 'text.secondary'}
            sx={{ 
              fontWeight: isStale ? 600 : 400,
              fontSize: isMobile ? '0.75rem' : '0.75rem',
            }}
          >
            {formatRelativeTime(timestamp)}
          </Typography>
        </Box>
      </CardContent>
    </Card>
  );
};

export default DeviceStatusCard;
