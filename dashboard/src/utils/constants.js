/**
 * Application-wide constants
 */

// API Configuration
export const API_BASE_URL = 'http://pat.local:5000';

// Timestamp staleness threshold (10 minutes in milliseconds)
export const STALE_THRESHOLD = 10 * 60 * 1000;

// Time range options for historical data
export const TIME_RANGE = {
  LAST_24_HOURS: '24h',
  LAST_7_DAYS: '7d',
  LAST_30_DAYS: '30d',
  CUSTOM: 'custom',
};

// Time range display labels
export const TIME_RANGE_LABELS = {
  [TIME_RANGE.LAST_24_HOURS]: 'Last 24 Hours',
  [TIME_RANGE.LAST_7_DAYS]: 'Last 7 Days',
  [TIME_RANGE.LAST_30_DAYS]: 'Last 30 Days',
  [TIME_RANGE.CUSTOM]: 'Custom Range',
};

// Time range options array for selectors
export const TIME_RANGE_OPTIONS = [
  { value: TIME_RANGE.LAST_24_HOURS, label: TIME_RANGE_LABELS[TIME_RANGE.LAST_24_HOURS] },
  { value: TIME_RANGE.LAST_7_DAYS, label: TIME_RANGE_LABELS[TIME_RANGE.LAST_7_DAYS] },
  { value: TIME_RANGE.LAST_30_DAYS, label: TIME_RANGE_LABELS[TIME_RANGE.LAST_30_DAYS] },
];

// Device types
export const DEVICE_TYPE = {
  AIR: 'air',
  DOOR: 'door',
};

// Query configuration
export const QUERY_CONFIG = {
  STALE_TIME: {
    DEVICES: 5 * 60 * 1000, // 5 minutes
    LATEST_READING: 1 * 60 * 1000, // 1 minute
    HISTORY: 5 * 60 * 1000, // 5 minutes
  },
  CACHE_TIME: {
    DEFAULT: 10 * 60 * 1000, // 10 minutes
  },
  REFETCH_INTERVAL: {
    DEVICES: 5 * 60 * 1000, // 5 minutes
    LATEST_READING: 2 * 60 * 1000, // 2 minutes
  },
};
