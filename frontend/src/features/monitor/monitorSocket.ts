import { useEffect, useState } from 'react';

import { tokenStorage } from '@/shared/api/tokenStorage';

/** Пауза перед повторным подключением после обрыва, мс. */
const RECONNECT_DELAY = 3000;

/** Сообщение сервера; остальные поля зависят от типа. */
export interface SocketMessage {
  type: string;
}

type MessageHandler = (message: SocketMessage) => void;
type ConnectionHandler = (connected: boolean) => void;

function socketUrl(token: string): string {
  const protocol = window.location.protocol === 'https:' ? 'wss' : 'ws';
  return `${protocol}://${window.location.host}/api/device/monitor/?token=${encodeURIComponent(token)}`;
}

/** Сокет монитора: держит соединение, раздаёт сообщения сервера по типу и переподключается после обрыва. */
export class MonitorSocket {
  private socket: WebSocket | null = null;
  private reconnectTimer: number | undefined;
  private stopped = true;
  private readonly messageHandlers = new Map<string, Set<MessageHandler>>();
  private readonly connectionHandlers = new Set<ConnectionHandler>();

  start(): void {
    this.stopped = false;
    this.connect();
  }

  stop(): void {
    this.stopped = true;
    window.clearTimeout(this.reconnectTimer);
    this.socket?.close();
    this.socket = null;
  }

  /** Подписывает обработчик на сообщения сервера одного типа и возвращает отписку. */
  onMessage(type: string, handler: MessageHandler): () => void {
    const handlers = this.messageHandlers.get(type) ?? new Set<MessageHandler>();
    handlers.add(handler);
    this.messageHandlers.set(type, handlers);
    return () => handlers.delete(handler);
  }

  /** Подписывает обработчик на подключение и обрыв соединения и возвращает отписку. */
  onConnectionChange(handler: ConnectionHandler): () => void {
    this.connectionHandlers.add(handler);
    return () => this.connectionHandlers.delete(handler);
  }

  /** Отправляет сообщение серверу, если соединение открыто. */
  send(message: SocketMessage): void {
    if (this.socket?.readyState === WebSocket.OPEN) {
      this.socket.send(JSON.stringify(message));
    }
  }

  private connect(): void {
    const token = tokenStorage.get()?.access;
    if (!token) {
      return;
    }
    const socket = new WebSocket(socketUrl(token));
    this.socket = socket;
    socket.onopen = () => {
      this.connectionHandlers.forEach((handler) => handler(true));
    };
    socket.onmessage = (event: MessageEvent<string>) => {
      const message = JSON.parse(event.data) as SocketMessage;
      this.messageHandlers.get(message.type)?.forEach((handler) => handler(message));
    };
    socket.onclose = () => {
      // Закрытый при остановке или уже заменённый сокет не переподключается.
      if (this.stopped || socket !== this.socket) {
        return;
      }
      this.connectionHandlers.forEach((handler) => handler(false));
      this.reconnectTimer = window.setTimeout(() => this.connect(), RECONNECT_DELAY);
    };
  }
}

/** Создаёт сокет монитора и держит его открытым, пока компонент на экране. */
export function useMonitorSocket(): MonitorSocket {
  const [socket] = useState(() => new MonitorSocket());

  useEffect(() => {
    socket.start();
    return () => socket.stop();
  }, [socket]);

  return socket;
}
