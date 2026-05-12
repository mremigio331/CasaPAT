import { useMutation, useQueryClient } from '@tanstack/react-query';
import { apiRequestDelete } from '../../api/casapatApi';

const useDeleteDevice = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (deviceName) => apiRequestDelete(`/pat/data/device?device_name=${encodeURIComponent(deviceName)}`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['door', 'devices', 'all'] });
      queryClient.invalidateQueries({ queryKey: ['air', 'devices', 'all'] });
    },
  });
};

export default useDeleteDevice;
