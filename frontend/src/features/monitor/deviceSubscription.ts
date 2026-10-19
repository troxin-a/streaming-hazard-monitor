import { createContext, useContext, useEffect, useState } from 'react';

import type { MonitorSocket } from './monitorSocket';

/** Датчики на экране: собирает датчики всех блоков страницы и сообщает серверу их объединение. */
export class DeviceSubscription {
  private readonly socket: MonitorSocket;
  private readonly blocks = new Map<string, string[]>();
  private sendTimer: number | undefined;

  constructor(socket: MonitorSocket) {
    this.socket = socket;
  }

  /** Отправляет набор при каждом подключении сокета; возвращает отписку. */
  attach(): () => void {
    return this.socket.onConnectionChange((connected) => {
      if (connected) {
        this.send();
      }
    });
  }

  /** Заменяет датчики блока. */
  set(block: string, devices: string[]): void {
    this.blocks.set(block, devices);
    this.scheduleSend();
  }

  /** Убирает датчики блока. */
  remove(block: string): void {
    this.blocks.delete(block);
    this.scheduleSend();
  }

  /** Откладывает отправку до конца отрисовки, чтобы блоки одной страницы ушли одним сообщением. */
  private scheduleSend(): void {
    window.clearTimeout(this.sendTimer);
    this.sendTimer = window.setTimeout(() => this.send(), 0);
  }

  private send(): void {
    const message = { type: 'subscribe', devices: [...new Set([...this.blocks.values()].flat())] };
    this.socket.send(message);
  }
}

export const DeviceSubscriptionContext = createContext<DeviceSubscription | null>(null);

/** Создаёт набор датчиков на экране поверх сокета монитора. */
export function useDeviceSubscription(socket: MonitorSocket): DeviceSubscription {
  const [subscription] = useState(() => new DeviceSubscription(socket));

  useEffect(() => subscription.attach(), [subscription]);

  return subscription;
}

/** Сообщает набору датчиков на экране датчики блока, пока блок на экране. */
export function useWatchDevices(block: string, devices: string[]): void {
  const subscription = useContext(DeviceSubscriptionContext);
  const key = devices.join(',');

  useEffect(() => {
    if (!subscription) {
      return;
    }
    subscription.set(block, key ? key.split(',') : []);
    return () => subscription.remove(block);
  }, [subscription, block, key]);
}
