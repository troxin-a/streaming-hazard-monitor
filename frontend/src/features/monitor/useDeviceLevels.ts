import { type QueryClient, useQueryClient } from '@tanstack/react-query';
import { useEffect } from 'react';

import { type AlertLevel, type Device, devices } from '@/entities/device';
import { tokenStorage } from '@/shared/api/tokenStorage';
import type { Page } from '@/shared/api/resource';

/** Пауза перед повторным подключением после обрыва, мс. */
const RECONNECT_DELAY = 3000;

/** Смена уровня датчика, которую присылает сервер. */
interface DeviceLevelMessage {
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

function levelsUrl(token: string): string {
  const protocol = window.location.protocol === 'https:' ? 'wss' : 'ws';
  return `${protocol}://${window.location.host}/api/device/levels/?token=${encodeURIComponent(token)}`;
}

/**
 * Держит открытым сокет уровней датчиков и обновляет по нему загруженные страницы датчиков.
 * После обрыва переподключается и перечитывает страницы, чтобы не потерять смены за время обрыва.
 */
export function useDeviceLevels(): void {
  const queryClient = useQueryClient();

  useEffect(() => {
    let socket: WebSocket | null = null;
    let reconnectTimer: number | undefined;
    let stopped = false;
    let wasConnected = false;

    function connect(): void {
      const token = tokenStorage.get()?.access;
      if (!token) {
        return;
      }
      socket = new WebSocket(levelsUrl(token));
      socket.onopen = () => {
        if (wasConnected) {
          void queryClient.invalidateQueries({ queryKey: [devices.key] });
        }
        wasConnected = true;
      };
      socket.onmessage = (event: MessageEvent<string>) => {
        applyLevel(queryClient, JSON.parse(event.data) as DeviceLevelMessage);
      };
      socket.onclose = () => {
        if (stopped) {
          return;
        }
        // Смены за время обрыва не придут: при следующем подключении страницы перечитаются.
        wasConnected = true;
        // Перечитывание заодно обновит истёкший access-токен для следующей попытки.
        void queryClient.invalidateQueries({ queryKey: [devices.key] });
        reconnectTimer = window.setTimeout(connect, RECONNECT_DELAY);
      };
    }

    connect();
    return () => {
      stopped = true;
      window.clearTimeout(reconnectTimer);
      socket?.close();
    };
  }, [queryClient]);
}
