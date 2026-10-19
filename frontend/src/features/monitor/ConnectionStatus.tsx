import Chip from '@mui/material/Chip';

import type { ConnectionState } from './useConnectionState';

const STATUS_CHIPS: Record<
  ConnectionState,
  { label: string; color: 'default' | 'success' | 'error' }
> = {
  connecting: { label: 'Подключение…', color: 'default' },
  connected: { label: 'На связи', color: 'success' },
  disconnected: { label: 'Нет связи, переподключение…', color: 'error' },
};

/** Показывает, есть ли связь с сервером у сокета монитора. */
export function ConnectionStatus({ state }: { state: ConnectionState }) {
  const { label, color } = STATUS_CHIPS[state];
  return <Chip label={label} color={color} size="small" variant="outlined" />;
}
