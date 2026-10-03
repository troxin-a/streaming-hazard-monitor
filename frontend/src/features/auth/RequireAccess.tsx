import type { ReactNode } from 'react';

import { PagePlaceholder } from '@/shared/ui/PagePlaceholder';

import { hasAccess } from './access';
import { useCurrentUser } from './hooks';
import type { AccessLevel } from './types';

interface RequireAccessProps {
  allowed?: AccessLevel[];
  children: ReactNode;
}

/** Показывает раздел только пользователям с подходящим уровнем доступа. */
export function RequireAccess({ allowed, children }: RequireAccessProps) {
  const user = useCurrentUser();

  if (!hasAccess(user, allowed)) {
    return <PagePlaceholder title="Нет доступа" text="У вас нет прав на просмотр этого раздела." />;
  }
  return children;
}
