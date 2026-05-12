import { useMutation, useQueryClient } from '@tanstack/react-query';
import { apiRequestPut } from '../../api/casapatApi';

const useUpdateDevice = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (payload) => apiRequestPut('/pat/data/device', payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['door', 'devices', 'all'] });
      queryClient.invalidateQueries({ queryKey: ['air', 'devices', 'all'] });
    },
  });
};

export default useUpdateDevice;
