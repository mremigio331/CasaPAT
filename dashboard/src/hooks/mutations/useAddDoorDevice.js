import { useMutation, useQueryClient } from '@tanstack/react-query';
import { apiRequestPost } from '../../api/casapatApi';

const useAddDoorDevice = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (deviceName) => apiRequestPost('/doors/register', { device_name: deviceName }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['door', 'devices', 'all'] });
    },
  });
};

export default useAddDoorDevice;
