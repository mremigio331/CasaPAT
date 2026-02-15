import { useQuery } from '@tanstack/react-query';
import { apiRequestGet } from '../../api/casapatApi';

/**
 * Hook to fetch all air quality devices
 * @param {boolean} enabled - Whether the query should run
 * @returns {Object} Query result with devices data and status
 */
const useGetAllAirDevices = (enabled = true) => {
  const { data, isFetching, isError, status, error, refetch } = useQuery({
    queryKey: ['air', 'devices', 'all'],
    queryFn: () => apiRequestGet('/air/get_devices/air_devices'),
    enabled,
    staleTime: 1000 * 60 * 5, // 5 minutes
    cacheTime: 1000 * 60 * 15, // 15 minutes
    retry: 3,
    retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
  });

  return {
    airDevices: data?.data?.devices || data?.data || [],
    isAirDevicesFetching: isFetching,
    isAirDevicesError: isError,
    airDevicesStatus: status,
    airDevicesError: error,
    airDevicesRefetch: refetch,
  };
};

export default useGetAllAirDevices;
