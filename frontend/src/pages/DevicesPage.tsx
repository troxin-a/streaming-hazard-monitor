import Chip from '@mui/material/Chip';
import Stack from '@mui/material/Stack';
import { useState } from 'react';

import { type Device, DEVICE_TYPE_LABELS, devices } from '@/entities/device';
import { canManage } from '@/features/auth/access';
import { useCurrentUser } from '@/features/auth/hooks';
import { DeviceCard } from '@/features/devices/DeviceCard';
import { DeviceFormDialog } from '@/features/devices/DeviceFormDialog';
import { type Column, DataTable } from '@/shared/ui/DataTable';
import { PageHeader } from '@/shared/ui/PageHeader';

const columns: Column<Device>[] = [
  { header: 'Название', render: (device) => device.name },
  { header: 'Серийный номер', render: (device) => device.serial_number },
  { header: 'Тип', render: (device) => DEVICE_TYPE_LABELS[device.type] },
  { header: 'Здание', render: (device) => device.building.name },
  { header: 'Компания', render: (device) => device.building.company.name },
  {
    header: 'API-ключ',
    render: (device) =>
      device.has_api_key ? (
        <Chip label="Выпущен" color="success" size="small" variant="outlined" />
      ) : (
        <Chip label="Нет" size="small" variant="outlined" />
      ),
  },
];

export function DevicesPage() {
  const manage = canManage(useCurrentUser());
  const [creating, setCreating] = useState(false);

  return (
    <Stack spacing={2}>
      <PageHeader title="Датчики" onAdd={manage ? () => setCreating(true) : undefined} />
      <DataTable
        resource={devices}
        columns={columns}
        searchLabel="Поиск по названию или серийному номеру"
        card={(device, onClose) => (
          <DeviceCard device={device} columns={columns} manage={manage} onClose={onClose} />
        )}
      />
      {creating && <DeviceFormDialog onClose={() => setCreating(false)} />}
    </Stack>
  );
}
