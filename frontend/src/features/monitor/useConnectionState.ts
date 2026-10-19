import { useEffect, useState } from 'react';

import type { MonitorSocket } from './monitorSocket';

export type ConnectionState = 'connecting' | 'connected' | 'disconnected';

/** Следит, есть ли связь с сервером у сокета монитора. */
export function useConnectionState(socket: MonitorSocket): ConnectionState {
  const [state, setState] = useState<ConnectionState>('connecting');

  useEffect(
    () =>
      socket.onConnectionChange((connected) => setState(connected ? 'connected' : 'disconnected')),
    [socket],
  );

  return state;
}
