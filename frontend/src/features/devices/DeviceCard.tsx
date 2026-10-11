import DeleteIcon from '@mui/icons-material/Delete';
import EditIcon from '@mui/icons-material/Edit';
import KeyIcon from '@mui/icons-material/Key';
import KeyOffIcon from '@mui/icons-material/KeyOff';
import TuneIcon from '@mui/icons-material/Tune';
import Button from '@mui/material/Button';
import { useState } from 'react';

import { type Device, devices, revokeApiKey } from '@/entities/device';
import { ConfirmDialog } from '@/shared/ui/ConfirmDialog';
import type { Column } from '@/shared/ui/DataTable';
import { RecordCard } from '@/shared/ui/RecordCard';

import { ApiKeyDialog } from './ApiKeyDialog';
import { DeviceFormDialog } from './DeviceFormDialog';
import { ThresholdsDialog } from './ThresholdsDialog';

type CardView = 'edit' | 'thresholds' | 'apiKey';

interface DeviceCardProps {
  device: Device;
  columns: Column<Device>[];
  /** Можно ли изменять и удалять датчик, менять пороги и управлять ключом. */
  manage: boolean;
  onClose: () => void;
}

/** Карточка датчика с действиями над ним. */
export function DeviceCard({ device, columns, manage, onClose }: DeviceCardProps) {
  const [view, setView] = useState<CardView | null>(null);
  const [confirming, setConfirming] = useState<'delete' | 'revoke' | null>(null);
  const showCard = () => setView(null);

  const views = {
    edit: <DeviceFormDialog device={device} onClose={showCard} />,
    thresholds: <ThresholdsDialog device={device} editable={manage} onClose={showCard} />,
    apiKey: <ApiKeyDialog device={device} onClose={showCard} />,
  };

  return (
    <>
      <RecordCard
        title={device.name}
        row={device}
        columns={columns}
        onClose={onClose}
        view={view && views[view]}
      >
        {manage && (
          <Button variant="outlined" startIcon={<EditIcon />} onClick={() => setView('edit')}>
            Изменить
          </Button>
        )}
        <Button variant="outlined" startIcon={<TuneIcon />} onClick={() => setView('thresholds')}>
          Пороги
        </Button>
        {manage &&
          (device.has_api_key ? (
            <Button
              variant="outlined"
              color="warning"
              startIcon={<KeyOffIcon />}
              onClick={() => setConfirming('revoke')}
            >
              Отозвать API-ключ
            </Button>
          ) : (
            <Button variant="outlined" startIcon={<KeyIcon />} onClick={() => setView('apiKey')}>
              Выпустить API-ключ
            </Button>
          ))}
        {manage && (
          <Button
            variant="outlined"
            color="error"
            startIcon={<DeleteIcon />}
            onClick={() => setConfirming('delete')}
          >
            Удалить
          </Button>
        )}
      </RecordCard>
      {confirming === 'delete' && (
        <ConfirmDialog
          title="Удалить датчик?"
          text={`Датчик «${device.name}» будет удалён.`}
          action={() => devices.remove(device.uuid)}
          successMessage="Датчик удалён"
          onClose={() => setConfirming(null)}
        />
      )}
      {confirming === 'revoke' && (
        <ConfirmDialog
          title="Отозвать API-ключ?"
          text={`Датчик «${device.name}» не сможет отправлять показания, пока не получит новый ключ.`}
          confirmLabel="Отозвать"
          action={() => revokeApiKey(device.uuid)}
          successMessage="API-ключ отозван"
          onClose={() => setConfirming(null)}
        />
      )}
    </>
  );
}
