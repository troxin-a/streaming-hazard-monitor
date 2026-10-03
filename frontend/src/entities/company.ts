import { createResource } from '@/shared/api/resource';

export interface Company {
  uuid: string;
  name: string;
}

export interface CompanyInput {
  name: string;
}

export const companies = createResource<Company, CompanyInput>('company');
