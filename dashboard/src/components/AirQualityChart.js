import React from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from 'recharts';
import { Box, Typography, useMediaQuery, useTheme } from '@mui/material';
import { formatChartTimestamp } from '../utils/dateFormatters';

/**
 * AirQualityChart component - Displays time-series chart for air quality metrics
 * Responsive design with adjusted font sizes and margins for mobile
 * 
 * @param {Object} props
 * @param {Array} props.data - Array of air quality readings with timestamp and metric values
 * @param {string} props.metric - The metric to display ('PM25', 'PM10', 'temperature', 'humidity')
 * @param {number} props.height - Optional height for the chart (default: 300)
 */
const AirQualityChart = ({ data, metric, height = 300 }) => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));
  
  // Validate inputs
  if (!data || !Array.isArray(data) || data.length === 0) {
    return (
      <Box
        sx={{
          height,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          border: '1px solid #e0e0e0',
          borderRadius: 1,
          backgroundColor: '#f5f5f5',
        }}
      >
        <Typography variant="body2" color="text.secondary">
          No data available
        </Typography>
      </Box>
    );
  }

  if (!metric) {
    return (
      <Box
        sx={{
          height,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          border: '1px solid #e0e0e0',
          borderRadius: 1,
          backgroundColor: '#f5f5f5',
        }}
      >
        <Typography variant="body2" color="text.secondary">
          No metric specified
        </Typography>
      </Box>
    );
  }

  // Metric configuration
  const metricConfig = {
    PM25: {
      label: 'PM2.5 (µg/m³)',
      color: '#ff6b6b',
      unit: 'µg/m³',
    },
    PM10: {
      label: 'PM10 (µg/m³)',
      color: '#4ecdc4',
      unit: 'µg/m³',
    },
    temperature: {
      label: 'Temperature (°C)',
      color: '#ff9f43',
      unit: '°C',
    },
    humidity: {
      label: 'Humidity (%)',
      color: '#5f27cd',
      unit: '%',
    },
  };

  const config = metricConfig[metric];
  
  if (!config) {
    return (
      <Box
        sx={{
          height,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          border: '1px solid #e0e0e0',
          borderRadius: 1,
          backgroundColor: '#f5f5f5',
        }}
      >
        <Typography variant="body2" color="text.secondary">
          Invalid metric: {metric}
        </Typography>
      </Box>
    );
  }

  // Transform data for Recharts
  const chartData = data.map((reading) => {
    // Map metric names to actual API field names (API uses lowercase)
    const metricFieldMap = {
      'PM25': 'pm25',
      'PM10': 'pm10',
      'temperature': 'temperature',
      'humidity': 'humidity',
    };
    
    const fieldName = metricFieldMap[metric] || metric;
    
    return {
      timestamp: reading.timestamp,
      formattedTime: formatChartTimestamp(reading.timestamp),
      value: reading[fieldName],
    };
  });

  // Custom tooltip formatter
  const CustomTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      return (
        <Box
          sx={{
            backgroundColor: 'white',
            border: '1px solid #ccc',
            borderRadius: 1,
            padding: isMobile ? 1 : 1.5,
            boxShadow: 1,
          }}
        >
          <Typography variant={isMobile ? "caption" : "body2"} sx={{ fontWeight: 'bold', mb: 0.5 }}>
            {data.formattedTime}
          </Typography>
          <Typography variant={isMobile ? "caption" : "body2"} color={config.color}>
            {config.label}: {payload[0].value.toFixed(2)} {config.unit}
          </Typography>
        </Box>
      );
    }
    return null;
  };

  return (
    <Box sx={{ width: '100%', height }}>
      <Typography variant={isMobile ? "subtitle1" : "h6"} sx={{ mb: 1, ml: isMobile ? 1 : 2 }}>
        {config.label}
      </Typography>
      <ResponsiveContainer width="100%" height="90%">
        <LineChart
          data={chartData}
          margin={{ 
            top: 5, 
            right: isMobile ? 10 : 30, 
            left: isMobile ? 0 : 20, 
            bottom: 5 
          }}
        >
          <CartesianGrid strokeDasharray="3 3" stroke="#e0e0e0" />
          <XAxis
            dataKey="formattedTime"
            stroke="#666"
            style={{ fontSize: isMobile ? '10px' : '12px' }}
            angle={isMobile ? -45 : 0}
            textAnchor={isMobile ? "end" : "middle"}
            height={isMobile ? 60 : 30}
          />
          <YAxis
            stroke="#666"
            style={{ fontSize: isMobile ? '10px' : '12px' }}
            label={{
              value: config.unit,
              angle: -90,
              position: 'insideLeft',
              style: { fontSize: isMobile ? '10px' : '12px' },
            }}
          />
          <Tooltip content={<CustomTooltip />} />
          <Legend wrapperStyle={{ fontSize: isMobile ? '12px' : '14px' }} />
          <Line
            type="monotone"
            dataKey="value"
            stroke={config.color}
            strokeWidth={isMobile ? 1.5 : 2}
            dot={{ fill: config.color, r: isMobile ? 2 : 3 }}
            activeDot={{ r: isMobile ? 4 : 5 }}
            name={config.label}
          />
        </LineChart>
      </ResponsiveContainer>
    </Box>
  );
};

export default AirQualityChart;
