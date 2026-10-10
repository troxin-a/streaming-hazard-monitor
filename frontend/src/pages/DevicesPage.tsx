import KeyIcon from '@mui/icons-material/Key';
import KeyOffIcon from '@mui/icons-material/KeyOff';
import TuneIcon from '@mui/icons-material/Tune';
import Chip from '@mui/material/Chip';
import IconButton from '@mui/material/IconButton';
import Stack from '@mui/material/Stack';
import Tooltip from '@mui/material/Tooltip';
import { useState } from 'react';

import { type Device, DEVICE_TYPE_LABELS, devices, revokeApiKey } from '@/entities/device';
import { canManage } from '@/features/auth/access';
import { useCurrentUser } from '@/features/auth/hooks';
import { ApiKeyDialog } from '@/features/devices/ApiKeyDialog';
import { DeviceFormDialog } from '@/features/devices/DeviceFormDialog';
import { ThresholdsDialog } from '@/features/devices/ThresholdsDialog';
import { ConfirmDialog } from '@/shared/ui/ConfirmDialog';
import { type Column, DataTable } from '@/shared/ui/DataTable';
import { PageHeader } from '@/shared/ui/PageHeader';
import { RowActions } from '@/shared/ui/RowActions';

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
  const [editing, setEditing] = useState<Device | 'new' | null>(null);
  const [deleting, setDeleting] = useState<Device | null>(null);
  const [issuingKey, setIssuingKey] = useState<Device | null>(null);
  const [revokingKey, setRevokingKey] = useState<Device | null>(null);
  const [viewingThresholds, setViewingThresholds] = useState<Device | null>(null);

  const renderThresholdsAction = (device: Device) => (
    <Tooltip title="Пороги">
      <IconButton size="small" aria-label="Пороги" onClick={() => setViewingThresholds(device)}>
        <TuneIcon fontSize="small" />
      </IconButton>
    </Tooltip>
  );

  const renderManageActions = (device: Device) => (
    <RowActions onEdit={() => setEditing(device)} onDelete={() => setDeleting(device)}>
      {renderThresholdsAction(device)}
      {device.has_api_key ? (
        <Tooltip title="Отозвать API-ключ">
          <IconButton
            size="small"
            aria-label="Отозвать API-ключ"
            onClick={() => setRevokingKey(device)}
          >
            <KeyOffIcon fontSize="small" />
          </IconButton>
        </Tooltip>
      ) : (
        <Tooltip title="Выпустить API-ключ">
          <IconButton
            size="small"
            aria-label="Выпустить API-ключ"
            onClick={() => setIssuingKey(device)}
          >
            <KeyIcon fontSize="small" />
          </IconButton>
        </Tooltip>
      )}
    </RowActions>
  );

  return (
    <Stack spacing={2}>
      <PageHeader title="Датчики" onAdd={manage ? () => setEditing('new') : undefined} />
      <DataTable
        resource={devices}
        columns={columns}
        searchLabel="Поиск по названию или серийному номеру"
        actions={manage ? renderManageActions : renderThresholdsAction}
      />
      {editing && (
        <DeviceFormDialog
          device={editing === 'new' ? undefined : editing}
          onClose={() => setEditing(null)}
        />
      )}
      {deleting && (
        <ConfirmDialog
          title="Удалить датчик?"
          text={`Датчик «${deleting.name}» будет удалён.`}
          action={() => devices.remove(deleting.uuid)}
          successMessage="Датчик удалён"
          onClose={() => setDeleting(null)}
        />
      )}
      {viewingThresholds && (
        <ThresholdsDialog
          device={viewingThresholds}
          editable={manage}
          onClose={() => setViewingThresholds(null)}
        />
      )}
      {issuingKey && <ApiKeyDialog device={issuingKey} onClose={() => setIssuingKey(null)} />}
      {revokingKey && (
        <ConfirmDialog
          title="Отозвать API-ключ?"
          text={`Датчик «${revokingKey.name}» не сможет отправлять показания, пока не получит новый ключ.`}
          confirmLabel="Отозвать"
          action={() => revokeApiKey(revokingKey.uuid)}
          successMessage="API-ключ отозван"
          onClose={() => setRevokingKey(null)}
        />
      )}
    </Stack>
  );
}
