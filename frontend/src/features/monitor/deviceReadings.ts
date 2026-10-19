import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useState,
  useSyncExternalStore,
} from 'react';

import type { MonitorSocket, SocketMessage } from './monitorSocket';

/** Сколько последних показаний держит график. */
const HISTORY = 60;

const NO_READINGS: number[] = [];

/** Показания датчиков за секунду, которые присылает сервер. */
interface DeviceReadingsMessage extends SocketMessage {
  type: 'readings';
  items: { device_uuid: string; value: string; received_at: string }[];
}

/** Последние показания датчиков из сокета монитора. */
export class DeviceReadings {
  private readonly values = new Map<string, number[]>();
  private readonly listeners = new Set<() => void>();

  /** Записывает показания из сокета; возвращает отписку. */
  attach(socket: MonitorSocket): () => void {
    return socket.onMessage('readings', (message) => {
      this.add(message as DeviceReadingsMessage);
    });
  }

  /** Последние показания датчика, от старых к новым. */
  get(device: string): number[] {
    return this.values.get(device) ?? NO_READINGS;
  }

  /** Стирает показания датчика. */
  forget(device: string): void {
    this.values.delete(device);
  }

  subscribe(listener: () => void): () => void {
    this.listeners.add(listener);
    return () => this.listeners.delete(listener);
  }

  private add(message: DeviceReadingsMessage): void {
    for (const item of message.items) {
      const values = [...this.get(item.device_uuid), Number(item.value)];
      this.values.set(item.device_uuid, values.slice(-HISTORY));
    }
    this.listeners.forEach((listener) => listener());
  }
}

export const DeviceReadingsContext = createContext<DeviceReadings | null>(null);

/** Создаёт хранилище показаний и наполняет его из сокета монитора. */
export function useDeviceReadingsStore(socket: MonitorSocket): DeviceReadings {
  const [readings] = useState(() => new DeviceReadings());

  useEffect(() => readings.attach(socket), [readings, socket]);

  return readings;
}

/**
 * Последние показания датчика; компонент перерисовывается, когда они меняются.
 * Когда компонент уходит с экрана, показания датчика стираются.
 */
export function useDeviceReadings(device: string): number[] {
  const readings = useContext(DeviceReadingsContext);
  useEffect(() => () => readings?.forget(device), [readings, device]);
  const subscribe = useCallback(
    (listener: () => void) => readings?.subscribe(listener) ?? (() => undefined),
    [readings],
  );
  return useSyncExternalStore(subscribe, () => readings?.get(device) ?? NO_READINGS);
}
