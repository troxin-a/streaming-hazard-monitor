import { request } from '@/shared/api/client';
import { createResource } from '@/shared/api/resource';

import type { Building } from './building';

export const DEVICE_TYPE_LABELS = {
  co: 'Угарный газ (CO)',
  co2: 'Углекислый газ (CO₂)',
  methane: 'Метан',
  smoke: 'Дым',
  temperature: 'Температура',
  radiation: 'Радиация',
};

export type DeviceType = keyof typeof DEVICE_TYPE_LABELS;

export const DEVICE_TYPES = Object.keys(DEVICE_TYPE_LABELS) as DeviceType[];

/** Единицы измерения показаний по типам датчиков. */
export const DEVICE_TYPE_UNITS: Record<DeviceType, string> = {
  co: 'ppm',
  co2: 'ppm',
  methane: '% НКПР',
  smoke: 'дБ/м',
  temperature: '°C',
  radiation: 'мкЗв/ч',
};

export const ALERT_LEVEL_LABELS = {
  level_1: 'Уровень 1',
  level_2: 'Уровень 2',
  level_3: 'Уровень 3',
  level_4: 'Уровень 4',
};

export type AlertLevel = keyof typeof ALERT_LEVEL_LABELS;

/** Уровни по возрастанию опасности. */
export const ALERT_LEVELS = Object.keys(ALERT_LEVEL_LABELS) as AlertLevel[];

export interface Device {
  uuid: string;
  name: string;
  serial_number: string;
  type: DeviceType;
  has_api_key: boolean;
  building: Building;
}

export interface DeviceInput {
  name: string;
  serial_number: string;
  type: DeviceType;
  building_uuid: string;
}

export const devices = createResource<Device, DeviceInput>('device');

/** Выпускает API-ключ датчика; ключ возвращается один раз. */
export async function issueApiKey(uuid: string): Promise<string> {
  const { key } = await request<{ key: string }>(`/device/${uuid}/api-key/`, { method: 'POST' });
  return key;
}

export function revokeApiKey(uuid: string): Promise<void> {
  return request(`/device/${uuid}/api-key/`, { method: 'DELETE' });
}

export interface Threshold {
  level: AlertLevel;
  /** Десятичное число строкой, например «20.000». */
  value: string;
  /** Порог взят из значений по умолчанию для типа датчика. */
  is_default: boolean;
}

/** Пороги всех уровней: десятичные числа строками. */
export type ThresholdValues = Record<AlertLevel, string>;

/** Ключ кеша порогов датчика. */
export function thresholdsKey(uuid: string): string[] {
  return [devices.key, uuid, 'thresholds'];
}

/** Возвращает пороги датчика: свои, а если их нет — значения по умолчанию его типа. */
export function getThresholds(uuid: string): Promise<Threshold[]> {
  return request(`/device/${uuid}/thresholds/`);
}

/** Задаёт датчику свои пороги вместо значений по умолчанию. */
export function createThresholds(uuid: string, values: ThresholdValues): Promise<unknown> {
  return request(`/device/${uuid}/thresholds/`, { method: 'POST', body: values });
}

export function updateThresholds(uuid: string, values: ThresholdValues): Promise<unknown> {
  return request(`/device/${uuid}/thresholds/`, { method: 'PATCH', body: values });
}

/** Удаляет свои пороги датчика; снова действуют значения по умолчанию. */
export function resetThresholds(uuid: string): Promise<void> {
  return request(`/device/${uuid}/thresholds/`, { method: 'DELETE' });
}
