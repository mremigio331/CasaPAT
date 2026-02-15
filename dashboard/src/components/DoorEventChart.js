import React from 'react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from 'recharts';
import { Box, Typography, useMediaQuery, useTheme } from '@mui/material';
import { formatChartTimestamp } from '../utils/dateFormatters';

/**
 * DoorEventChart component - Displays timeline for door open/closed events
 * Responsive design with adjusted font sizes and margins for mobile
 * 
 * @param {Object} props
 * @param {Array} props.data - Array of door events with timestamp and status
 * @param {number} props.height - Optional height for the chart (default: 300)
 */
const DoorEventChart = ({ data, height = 300 }) => {
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

  // Color configuration for door status
  const STATUS_COLORS = {
    open: '#f44336',    // Red for open
    closed: '#4caf50', // Green for closed
  };

  // Transform data for Recharts
  // Convert status to numeric value for bar chart (1 for any event)
  const chartData = data.map((event) => ({
    timestamp: event.timestamp,
    formattedTime: formatChartTimestamp(event.timestamp),
    status: event.status,
    value: 1, // All bars same height, color indicates status
  }));

  // Custom tooltip formatter
  const CustomTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      const statusColor = STATUS_COLORS[data.status] || '#999';
      
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
          <Typography
            variant={isMobile ? "caption" : "body2"}
            sx={{
              color: statusColor,
              fontWeight: 'bold',
              textTransform: 'capitalize',
            }}
          >
            Status: {data.status}
          </Typography>
        </Box>
      );
    }
    return null;
  };

  // Custom Y-axis tick formatter
  const yAxisTickFormatter = (value) => {
    if (value === 0) return 'Closed';
    if (value === 1) return 'Open';
    return '';
  };

  return (
    <Box sx={{ width: '100%', height }}>
      <Typography variant={isMobile ? "subtitle1" : "h6"} sx={{ mb: 1, ml: isMobile ? 1 : 2 }}>
        Door Status Timeline
      </Typography>
      <ResponsiveContainer width="100%" height="90%">
        <BarChart
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
            domain={[0, 1]}
            ticks={[0, 1]}
            tickFormatter={yAxisTickFormatter}
          />
          <Tooltip content={<CustomTooltip />} />
          <Bar dataKey="value" radius={[4, 4, 0, 0]}>
            {chartData.map((entry, index) => (
              <Cell
                key={`cell-${index}`}
                fill={STATUS_COLORS[entry.status] || '#999'}
              />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
      
      {/* Legend */}
      <Box
        sx={{
          display: 'flex',
          justifyContent: 'center',
          gap: isMobile ? 2 : 3,
          mt: 1,
          flexWrap: 'wrap',
        }}
      >
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <Box
            sx={{
              width: isMobile ? 14 : 16,
              height: isMobile ? 14 : 16,
              backgroundColor: STATUS_COLORS.closed,
              borderRadius: 0.5,
            }}
          />
          <Typography variant={isMobile ? "caption" : "body2"}>Closed</Typography>
        </Box>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <Box
            sx={{
              width: isMobile ? 14 : 16,
              height: isMobile ? 14 : 16,
              backgroundColor: STATUS_COLORS.open,
              borderRadius: 0.5,
            }}
          />
          <Typography variant={isMobile ? "caption" : "body2"}>Open</Typography>
        </Box>
      </Box>
    </Box>
  );
};

export default DoorEventChart;
