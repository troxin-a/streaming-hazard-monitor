import type { User } from '@/entities/user';
import { request } from '@/shared/api/client';
import type { Tokens } from '@/shared/api/tokenStorage';

import type { Credentials, PasswordChange } from './types';

export function login(credentials: Credentials): Promise<Tokens> {
  return request<Tokens>('/auth/login/', { method: 'POST', body: credentials, auth: false });
}

export function fetchCurrentUser(): Promise<User> {
  return request<User>('/user/me/');
}

export function changeOwnPassword(data: PasswordChange): Promise<void> {
  return request('/user/me/password/', { method: 'POST', body: data });
}
