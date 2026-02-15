import { useQuery } from '@tanstack/react-query';
import { apiRequestGet } from '../../api/casapatApi';

/**
 * Hook to fetch historical data for a door sensor device
 * @param {string} deviceId - The device ID
 * @param {string} timeRange - Time range for historical data (optional)
 * @param {boolean} enabled - Whether the query should run
 * @returns {Object} Query result with historical data and status
 */
const useGetDoorDeviceHistory = (deviceId, timeRange = null, enabled = true) => {
  const isEnabled = enabled && !!deviceId;

  const { data, isFetching, isError, status, error, refetch } = useQuery({
    queryKey: ['door', 'device', deviceId, 'history', timeRange],
    queryFn: () => apiRequestGet(`/doors/info/full?device_name=${deviceId}`),
    enabled: isEnabled,
    staleTime: 1000 * 60 * 5, // 5 minutes
    cacheTime: 1000 * 60 * 10, // 10 minutes
    retry: 3,
    retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
  });

  return {
    doorDeviceHistory: data?.data?.database_entries || [],
    isDoorDeviceHistoryFetching: isFetching,
    isDoorDeviceHistoryError: isError,
    doorDeviceHistoryStatus: status,
    doorDeviceHistoryError: error,
    doorDeviceHistoryRefetch: refetch,
  };
};

export default useGetDoorDeviceHistory;
