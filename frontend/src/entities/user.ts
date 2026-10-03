import { createResource } from '@/shared/api/resource';

import type { Building } from './building';
import type { Company } from './company';

export const ROLE_LABELS = {
  employee: 'Сотрудник',
  director: 'Директор',
};

export type UserRole = keyof typeof ROLE_LABELS;

export const USER_ROLES = Object.keys(ROLE_LABELS) as UserRole[];

export interface User {
  uuid: string;
  username: string;
  name: string;
  is_superuser: boolean;
  role: UserRole;
  company: Company | null;
  building: Building | null;
}

export interface UserCreateInput {
  username: string;
  name: string;
  role: UserRole;
  password1: string;
  password2: string;
  company_uuid?: string;
  building_uuid?: string;
}

export interface UserUpdateInput {
  name?: string;
  role?: UserRole;
  company_uuid?: string;
  /** null открепляет пользователя от здания. */
  building_uuid?: string | null;
  password1?: string;
  password2?: string;
}

export const users = createResource<User, UserCreateInput, UserUpdateInput>('user');
