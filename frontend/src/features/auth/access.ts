import type { AccessLevel, User } from './types';

export const ACCESS_LEVEL_LABELS: Record<AccessLevel, string> = {
  employee: 'Сотрудник',
  director: 'Директор',
  superuser: 'Суперпользователь',
};

/** Возвращает уровень доступа пользователя. */
export function getAccessLevel(user: User): AccessLevel {
  return user.is_superuser ? 'superuser' : user.role;
}

/** Проверяет доступ; пустой список уровней означает «доступно всем». */
export function hasAccess(user: User, allowed?: AccessLevel[]): boolean {
  return !allowed || allowed.includes(getAccessLevel(user));
}
