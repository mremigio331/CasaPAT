import { useQuery } from '@tanstack/react-query';
import { apiRequestGet } from '../../api/casapatApi';

/**
 * Hook to fetch current state for all door devices
 * Uses the webhook endpoint for real-time door status
 * @param {boolean} enabled - Whether the query should run
 * @returns {Object} Query result with all door devices current state
 */
const useGetAllDoorsCurrentState = (enabled = true) => {
  const { data, isFetching, isError, status, error, refetch, dataUpdatedAt } = useQuery({
    queryKey: ['door', 'devices', 'current_state'],
    queryFn: () => apiRequestGet('/doors/current_state'),
    enabled,
    staleTime: 1000 * 30, // 30 seconds - update frequently for real-time feel
    cacheTime: 1000 * 60 * 5, // 5 minutes
    refetchInterval: 1000 * 30, // Poll every 30 seconds for updates
    retry: 3,
    retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
  });

  return {
    doorsCurrentState: data?.data?.devices || [],
    isDoorsCurrentStateFetching: isFetching,
    isDoorsCurrentStateError: isError,
    doorsCurrentStateStatus: status,
    doorsCurrentStateError: error,
    doorsCurrentStateRefetch: refetch,
    lastUpdated: dataUpdatedAt ? new Date(dataUpdatedAt) : null,
  };
};

export default useGetAllDoorsCurrentState;
