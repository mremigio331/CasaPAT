import { useQuery } from '@tanstack/react-query';
import { apiRequestGet } from '../../api/casapatApi';

/**
 * Hook to fetch latest reading for a door sensor device
 * @param {string} deviceId - The device ID
 * @param {boolean} enabled - Whether the query should run
 * @returns {Object} Query result with latest reading data and status
 */
const useGetLatestDoorReading = (deviceId, enabled = true) => {
  const isEnabled = enabled && !!deviceId;

  const { data, isFetching, isError, status, error, refetch, dataUpdatedAt } = useQuery({
    queryKey: ['door', 'device', deviceId, 'latest'],
    queryFn: () => apiRequestGet(`/doors/info/latest?device_name=${deviceId}`),
    enabled: isEnabled,
    staleTime: 1000 * 60 * 1, // 1 minute
    cacheTime: 1000 * 60 * 10, // 10 minutes
    refetchInterval: 1000 * 60 * 2, // Refetch every 2 minutes
    retry: 3,
    retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
  });

  return {
    latestDoorReading: data?.data?.latest_info || null,
    isLatestDoorReadingFetching: isFetching,
    isLatestDoorReadingError: isError,
    latestDoorReadingStatus: status,
    latestDoorReadingError: error,
    latestDoorReadingRefetch: refetch,
    lastUpdated: dataUpdatedAt ? new Date(dataUpdatedAt) : null,
  };
};

export default useGetLatestDoorReading;
