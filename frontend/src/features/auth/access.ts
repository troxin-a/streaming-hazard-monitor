import { ROLE_LABELS, type User } from '@/entities/user';

import type { AccessLevel } from './types';

export const ACCESS_LEVEL_LABELS: Record<AccessLevel, string> = {
  ...ROLE_LABELS,
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

/** Может ли пользователь создавать, изменять и удалять записи своей компании. */
export function canManage(user: User): boolean {
  return getAccessLevel(user) !== 'employee';
}
