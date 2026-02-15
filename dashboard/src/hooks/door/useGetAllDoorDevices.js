import { useQuery } from '@tanstack/react-query';
import { apiRequestGet } from '../../api/casapatApi';

/**
 * Hook to fetch all door sensor devices
 * @param {boolean} enabled - Whether the query should run
 * @returns {Object} Query result with devices data and status
 */
const useGetAllDoorDevices = (enabled = true) => {
  const { data, isFetching, isError, status, error, refetch } = useQuery({
    queryKey: ['door', 'devices', 'all'],
    queryFn: () => apiRequestGet('/doors/get_devices/door_devices'),
    enabled,
    staleTime: 1000 * 60 * 5, // 5 minutes
    cacheTime: 1000 * 60 * 15, // 15 minutes
    retry: 3,
    retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
  });

  return {
    doorDevices: data?.data?.devices || data?.data || [],
    isDoorDevicesFetching: isFetching,
    isDoorDevicesError: isError,
    doorDevicesStatus: status,
    doorDevicesError: error,
    doorDevicesRefetch: refetch,
  };
};

export default useGetAllDoorDevices;
