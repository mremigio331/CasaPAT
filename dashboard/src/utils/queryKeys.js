/**
 * Query key factory for TanStack Query
 * Provides consistent query keys for all data fetching operations
 */

export const queryKeys = {
  // All devices queries
  allDevices: () => ['devices', 'all'],
  airDevices: () => ['devices', 'air'],
  doorDevices: () => ['devices', 'door'],

  // Latest reading queries
  latestReading: (deviceId, deviceType) => ['devices', deviceType, deviceId, 'latest'],
  airLatestReading: (deviceId) => ['devices', 'air', deviceId, 'latest'],
  doorLatestReading: (deviceId) => ['devices', 'door', deviceId, 'latest'],

  // Historical data queries
  deviceHistory: (deviceId, deviceType, timeRange) => [
    'devices',
    deviceType,
    deviceId,
    'history',
    timeRange || 'all',
  ],
  airHistory: (deviceId, timeRange) => [
    'devices',
    'air',
    deviceId,
    'history',
    timeRange || 'all',
  ],
  doorHistory: (deviceId, timeRange) => [
    'devices',
    'door',
    deviceId,
    'history',
    timeRange || 'all',
  ],
};
