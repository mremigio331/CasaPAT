import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import {
  Container, Typography, Box, Button, IconButton, Paper,
  Table, TableBody, TableCell, TableContainer, TableHead, TableRow,
  Dialog, DialogTitle, DialogContent, DialogContentText, DialogActions,
  TextField, Alert, CircularProgress, Chip, Tooltip,
} from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import EditIcon from '@mui/icons-material/Edit';
import DeleteIcon from '@mui/icons-material/Delete';
import WarningAmberIcon from '@mui/icons-material/WarningAmber';
import useGetAllDoorDevices from '../hooks/door/useGetAllDoorDevices';
import useGetAllAirDevices from '../hooks/air/useGetAllAirDevices';
import useAddDoorDevice from '../hooks/mutations/useAddDoorDevice';
import useAddAirDevice from '../hooks/mutations/useAddAirDevice';
import useDeleteDevice from '../hooks/mutations/useDeleteDevice';
import useUpdateDevice from '../hooks/mutations/useUpdateDevice';
import { apiRequestGet } from '../api/casapatApi';

// Fetch full device info (name, manufacturer, model) for the edit form
const useDeviceInfo = (deviceName, deviceType, enabled) => {
  const route = deviceType === 'door'
    ? `/doors/info/device?device_name=${encodeURIComponent(deviceName)}`
    : `/air/info/device?device_name=${encodeURIComponent(deviceName)}`;

  return useQuery({
    queryKey: ['device', 'info', deviceType, deviceName],
    queryFn: () => apiRequestGet(route),
    enabled: !!deviceName && !!deviceType && enabled,
    staleTime: 0,
    retry: 1,
  });
};

// ── Add Device Dialog ──────────────────────────────────────────────────────────
const AddDeviceDialog = ({ open, deviceType, onClose }) => {
  const [name, setName] = useState('');
  const addDoor = useAddDoorDevice();
  const addAir = useAddAirDevice();

  const mutation = deviceType === 'door' ? addDoor : addAir;
  const label = deviceType === 'door' ? 'Door Sensor' : 'Air Quality Sensor';

  const handleSubmit = () => {
    mutation.mutate(name.trim(), {
      onSuccess: () => {
        setName('');
        onClose();
      },
    });
  };

  const handleClose = () => {
    setName('');
    mutation.reset();
    onClose();
  };

  const errorMessage = mutation.error?.response?.data?.detail || mutation.error?.message;

  return (
    <Dialog open={open} onClose={handleClose} maxWidth="sm" fullWidth>
      <DialogTitle>Add {label}</DialogTitle>
      <DialogContent>
        {errorMessage && <Alert severity="error" sx={{ mb: 2 }}>{errorMessage}</Alert>}
        <TextField
          autoFocus
          label="Device Name"
          fullWidth
          value={name}
          onChange={(e) => setName(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && name.trim() && handleSubmit()}
          helperText="Must match the name the physical sensor is configured to use"
          sx={{ mt: 1 }}
        />
      </DialogContent>
      <DialogActions>
        <Button onClick={handleClose}>Cancel</Button>
        <Button
          onClick={handleSubmit}
          variant="contained"
          disabled={!name.trim() || mutation.isPending}
        >
          {mutation.isPending ? <CircularProgress size={20} /> : 'Add Device'}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

// ── Edit Device Dialog ─────────────────────────────────────────────────────────
const EditDeviceDialog = ({ open, deviceName, deviceType, onClose }) => {
  const [newName, setNewName] = useState('');
  const [manufacturer, setManufacturer] = useState('');
  const [model, setModel] = useState('');
  const updateDevice = useUpdateDevice();

  const { data: infoData, isLoading: infoLoading } = useDeviceInfo(deviceName, deviceType, open);

  React.useEffect(() => {
    if (infoData?.data?.device_info) {
      const info = infoData.data.device_info;
      setNewName(info.DeviceName || deviceName);
      setManufacturer(info.DeviceManufacturer || '');
      setModel(info.DeviceModel || '');
    } else if (deviceName) {
      setNewName(deviceName);
    }
  }, [infoData, deviceName]);

  const handleClose = () => {
    updateDevice.reset();
    onClose();
  };

  const handleSubmit = () => {
    const payload = { device_name: deviceName };
    if (newName.trim() !== deviceName) payload.new_device_name = newName.trim();
    if (manufacturer.trim()) payload.device_manufacturer = manufacturer.trim();
    if (model.trim()) payload.device_model = model.trim();

    updateDevice.mutate(payload, { onSuccess: handleClose });
  };

  const isRenaming = newName.trim() !== deviceName && newName.trim() !== '';
  const errorMessage = updateDevice.error?.response?.data?.detail || updateDevice.error?.message;

  return (
    <Dialog open={open} onClose={handleClose} maxWidth="sm" fullWidth>
      <DialogTitle>Edit Device</DialogTitle>
      <DialogContent>
        {infoLoading ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', py: 3 }}>
            <CircularProgress />
          </Box>
        ) : (
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, mt: 1 }}>
            {errorMessage && <Alert severity="error">{errorMessage}</Alert>}
            {isRenaming && (
              <Alert severity="warning" icon={<WarningAmberIcon />}>
                Renaming a device will break its connection until the physical sensor is reconfigured to use the new name.
              </Alert>
            )}
            <TextField
              label="Device Name"
              fullWidth
              value={newName}
              onChange={(e) => setNewName(e.target.value)}
            />
            <TextField
              label="Manufacturer"
              fullWidth
              value={manufacturer}
              onChange={(e) => setManufacturer(e.target.value)}
            />
            <TextField
              label="Model"
              fullWidth
              value={model}
              onChange={(e) => setModel(e.target.value)}
            />
          </Box>
        )}
      </DialogContent>
      <DialogActions>
        <Button onClick={handleClose}>Cancel</Button>
        <Button
          onClick={handleSubmit}
          variant="contained"
          disabled={!newName.trim() || infoLoading || updateDevice.isPending}
        >
          {updateDevice.isPending ? <CircularProgress size={20} /> : 'Save Changes'}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

// ── Delete Confirmation Dialog ─────────────────────────────────────────────────
const DeleteDeviceDialog = ({ open, deviceName, onClose }) => {
  const deleteDevice = useDeleteDevice();

  const handleDelete = () => {
    deleteDevice.mutate(deviceName, { onSuccess: onClose });
  };

  const handleClose = () => {
    deleteDevice.reset();
    onClose();
  };

  const errorMessage = deleteDevice.error?.response?.data?.detail || deleteDevice.error?.message;

  return (
    <Dialog open={open} onClose={handleClose} maxWidth="sm" fullWidth>
      <DialogTitle>Delete Device</DialogTitle>
      <DialogContent>
        {errorMessage && <Alert severity="error" sx={{ mb: 2 }}>{errorMessage}</Alert>}
        <DialogContentText>
          Are you sure you want to delete <strong>{deviceName}</strong>? This will permanently remove
          the device and all of its historical data. This cannot be undone.
        </DialogContentText>
      </DialogContent>
      <DialogActions>
        <Button onClick={handleClose}>Cancel</Button>
        <Button
          onClick={handleDelete}
          variant="contained"
          color="error"
          disabled={deleteDevice.isPending}
        >
          {deleteDevice.isPending ? <CircularProgress size={20} /> : 'Delete'}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

// ── Device Section ─────────────────────────────────────────────────────────────
const DeviceSection = ({ title, devices, deviceType, isLoading, isError, onRefetch }) => {
  const [addOpen, setAddOpen] = useState(false);
  const [editDevice, setEditDevice] = useState(null);
  const [deleteDevice, setDeleteDevice] = useState(null);

  if (isLoading) {
    return (
      <Box sx={{ mb: 5 }}>
        <Typography variant="h6" gutterBottom>{title}</Typography>
        <CircularProgress size={24} />
      </Box>
    );
  }

  if (isError) {
    return (
      <Box sx={{ mb: 5 }}>
        <Typography variant="h6" gutterBottom>{title}</Typography>
        <Alert severity="error" action={<Button size="small" onClick={onRefetch}>Retry</Button>}>
          Failed to load devices.
        </Alert>
      </Box>
    );
  }

  return (
    <Box sx={{ mb: 5 }}>
      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
        <Typography variant="h6">{title}</Typography>
        <Button variant="outlined" startIcon={<AddIcon />} onClick={() => setAddOpen(true)}>
          Add Device
        </Button>
      </Box>

      {devices.length === 0 ? (
        <Paper variant="outlined" sx={{ p: 3, textAlign: 'center' }}>
          <Typography color="text.secondary">No devices registered.</Typography>
        </Paper>
      ) : (
        <TableContainer component={Paper} variant="outlined">
          <Table size="small">
            <TableHead>
              <TableRow>
                <TableCell>Device Name</TableCell>
                <TableCell>Type</TableCell>
                <TableCell align="right">Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {devices.map((name) => (
                <TableRow key={name} hover>
                  <TableCell>{name}</TableCell>
                  <TableCell>
                    <Chip
                      label={deviceType === 'door' ? 'Door Sensor' : 'Air Quality'}
                      size="small"
                      color={deviceType === 'door' ? 'primary' : 'success'}
                      variant="outlined"
                    />
                  </TableCell>
                  <TableCell align="right">
                    <Tooltip title="Edit">
                      <IconButton size="small" onClick={() => setEditDevice(name)}>
                        <EditIcon fontSize="small" />
                      </IconButton>
                    </Tooltip>
                    <Tooltip title="Delete">
                      <IconButton size="small" color="error" onClick={() => setDeleteDevice(name)}>
                        <DeleteIcon fontSize="small" />
                      </IconButton>
                    </Tooltip>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      )}

      <AddDeviceDialog open={addOpen} deviceType={deviceType} onClose={() => setAddOpen(false)} />
      <EditDeviceDialog
        open={!!editDevice}
        deviceName={editDevice}
        deviceType={deviceType}
        onClose={() => setEditDevice(null)}
      />
      <DeleteDeviceDialog
        open={!!deleteDevice}
        deviceName={deleteDevice}
        onClose={() => setDeleteDevice(null)}
      />
    </Box>
  );
};

// ── Page ───────────────────────────────────────────────────────────────────────
const SystemSettings = () => {
  const { doorDevices, isDoorDevicesFetching, isDoorDevicesError, doorDevicesRefetch } = useGetAllDoorDevices();
  const { airDevices, isAirDevicesFetching, isAirDevicesError, airDevicesRefetch } = useGetAllAirDevices();

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 6 }}>
      <Typography variant="h4" component="h1" gutterBottom>
        Device Management
      </Typography>
      <Typography variant="body2" color="text.secondary" sx={{ mb: 4 }}>
        Add, edit, or remove devices. Device names must match what the physical sensor is configured to report.
      </Typography>

      <DeviceSection
        title="Door Sensors"
        devices={doorDevices}
        deviceType="door"
        isLoading={isDoorDevicesFetching}
        isError={isDoorDevicesError}
        onRefetch={doorDevicesRefetch}
      />

      <DeviceSection
        title="Air Quality Sensors"
        devices={airDevices}
        deviceType="air"
        isLoading={isAirDevicesFetching}
        isError={isAirDevicesError}
        onRefetch={airDevicesRefetch}
      />
    </Container>
  );
};

export default SystemSettings;
