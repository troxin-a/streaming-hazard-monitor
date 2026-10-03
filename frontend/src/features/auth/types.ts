export type UserRole = 'employee' | 'director';

/** Уровень доступа в интерфейсе: роль в компании либо суперпользователь. */
export type AccessLevel = UserRole | 'superuser';

export interface Company {
  uuid: string;
  name: string;
}

export interface Building {
  uuid: string;
  name: string;
  company: Company;
}

export interface User {
  uuid: string;
  name: string;
  is_superuser: boolean;
  role: UserRole;
  building: Building | null;
}

export interface Credentials {
  username: string;
  password: string;
  remember_me: boolean;
}
