import type { UserRole } from '@/entities/user';

/** Уровень доступа в интерфейсе: роль в компании либо суперпользователь. */
export type AccessLevel = UserRole | 'superuser';

export interface Credentials {
  username: string;
  password: string;
  remember_me: boolean;
}

export interface PasswordChange {
  old_password: string;
  password1: string;
  password2: string;
}
