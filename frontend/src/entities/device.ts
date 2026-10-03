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
