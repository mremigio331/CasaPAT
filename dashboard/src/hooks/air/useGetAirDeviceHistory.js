import { useQuery } from '@tanstack/react-query';
import { apiRequestGet } from '../../api/casapatApi';

/**
 * Hook to fetch historical data for an air quality device
 * @param {string} deviceId - The device ID
 * @param {string} timeRange - Time range for historical data (optional)
 * @param {boolean} enabled - Whether the query should run
 * @returns {Object} Query result with historical data and status
 */
const useGetAirDeviceHistory = (deviceId, timeRange = null, enabled = true) => {
  const isEnabled = enabled && !!deviceId;

  const { data, isFetching, isError, status, error, refetch } = useQuery({
    queryKey: ['air', 'device', deviceId, 'history', timeRange],
    queryFn: () => apiRequestGet(`/air/info/full?device_name=${deviceId}`),
    enabled: isEnabled,
    staleTime: 1000 * 60 * 5, // 5 minutes
    cacheTime: 1000 * 60 * 10, // 10 minutes
    retry: 3,
    retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
  });

  return {
    airDeviceHistory: data?.data?.database_entries || [],
    isAirDeviceHistoryFetching: isFetching,
    isAirDeviceHistoryError: isError,
    airDeviceHistoryStatus: status,
    airDeviceHistoryError: error,
    airDeviceHistoryRefetch: refetch,
  };
};

export default useGetAirDeviceHistory;
