import type { UserRole } from '@/entities/user';

/** Уровень доступа в интерфейсе: роль в компании либо суперпользователь. */
export type AccessLevel = UserRole | 'superuser';

export interface Credentials {
  username: string;
  password: string;
  remember_me: boolean;
}
