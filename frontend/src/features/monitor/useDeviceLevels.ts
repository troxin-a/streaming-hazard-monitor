import { type QueryClient, useQueryClient } from '@tanstack/react-query';
import { useEffect } from 'react';

import { type AlertLevel, type Device, devices } from '@/entities/device';
import type { Page } from '@/shared/api/resource';

import type { MonitorSocket, SocketMessage } from './monitorSocket';

/** Смена уровня датчика, которую присылает сервер. */
interface DeviceLevelMessage extends SocketMessage {
  type: 'level';
  device_uuid: string;
  level: AlertLevel | null;
  /** Время приёма показания, на котором сменился уровень. */
  changed_at: string;
}

function isDevicePage(data: unknown): data is Page<Device> {
  return typeof data === 'object' && data !== null && 'items' in data;
}

/** Записывает новый уровень датчика во все загруженные страницы датчиков. */
function applyLevel(queryClient: QueryClient, message: DeviceLevelMessage): void {
  queryClient.setQueriesData({ queryKey: [devices.key] }, (data: unknown) => {
    if (!isDevicePage(data) || !data.items.some((device) => device.uuid === message.device_uuid)) {
      return data;
    }
    return {
      ...data,
      items: data.items.map((device) =>
        device.uuid === message.device_uuid ? { ...device, level: message.level } : device,
      ),
    };
  });
}

/**
 * Обновляет загруженные страницы датчиков по сменам уровня из сокета монитора.
 * После обрыва и переподключения перечитывает страницы, чтобы не потерять смены за время обрыва.
 */
export function useDeviceLevels(socket: MonitorSocket): void {
  const queryClient = useQueryClient();

  useEffect(() => {
    let wasConnected = false;
    const offMessage = socket.onMessage('level', (message) => {
      applyLevel(queryClient, message as DeviceLevelMessage);
    });
    const offConnection = socket.onConnectionChange((connected) => {
      // При обрыве перечитывание заодно обновит истёкший access-токен для следующей попытки.
      if (!connected || wasConnected) {
        void queryClient.invalidateQueries({ queryKey: [devices.key] });
      }
      wasConnected = true;
    });
    return () => {
      offMessage();
      offConnection();
    };
  }, [socket, queryClient]);
}
