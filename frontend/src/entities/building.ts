import { createResource } from '@/shared/api/resource';

import type { Company } from './company';

export interface Building {
  uuid: string;
  name: string;
  company: Company;
}

export interface BuildingInput {
  name: string;
  company_uuid: string;
}

export const buildings = createResource<Building, BuildingInput>('building');
