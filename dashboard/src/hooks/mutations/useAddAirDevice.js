import { useMutation, useQueryClient } from '@tanstack/react-query';
import { apiRequestPost } from '../../api/casapatApi';

const useAddAirDevice = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (deviceName) => apiRequestPost('/air/register', { device_name: deviceName }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['air', 'devices', 'all'] });
    },
  });
};

export default useAddAirDevice;
