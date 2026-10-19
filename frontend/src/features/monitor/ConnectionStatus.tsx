import Chip from '@mui/material/Chip';
import { useEffect, useState } from 'react';

import type { MonitorSocket } from './monitorSocket';

type Status = 'connecting' | 'connected' | 'disconnected';

const STATUS_CHIPS: Record<Status, { label: string; color: 'default' | 'success' | 'error' }> = {
  connecting: { label: 'Подключение…', color: 'default' },
  connected: { label: 'На связи', color: 'success' },
  disconnected: { label: 'Нет связи, переподключение…', color: 'error' },
};

/** Показывает, есть ли связь с сервером у сокета монитора. */
export function ConnectionStatus({ socket }: { socket: MonitorSocket }) {
  const [status, setStatus] = useState<Status>('connecting');

  useEffect(
    () =>
      socket.onConnectionChange((connected) => setStatus(connected ? 'connected' : 'disconnected')),
    [socket],
  );

  const { label, color } = STATUS_CHIPS[status];
  return <Chip label={label} color={color} size="small" variant="outlined" />;
}
