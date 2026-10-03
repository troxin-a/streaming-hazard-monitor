import { useSyncExternalStore } from 'react';

export type NotificationSeverity = 'success' | 'info' | 'error';

interface NotificationState {
  /** Номер уведомления: меняется при каждом новом, даже с тем же текстом. */
  id: number;
  message: string;
  severity: NotificationSeverity;
  open: boolean;
}

type Listener = () => void;

const listeners = new Set<Listener>();
let state: NotificationState = { id: 0, message: '', severity: 'success', open: false };

function update(next: NotificationState): void {
  state = next;
  listeners.forEach((listener) => listener());
}

function subscribe(listener: Listener): () => void {
  listeners.add(listener);
  return () => listeners.delete(listener);
}

/** Показывает всплывающее уведомление; новое заменяет предыдущее. */
export function notify(message: string, severity: NotificationSeverity = 'success'): void {
  update({ id: state.id + 1, message, severity, open: true });
}

export function dismissNotification(): void {
  update({ ...state, open: false });
}

export function useNotification(): NotificationState {
  return useSyncExternalStore(subscribe, () => state);
}
