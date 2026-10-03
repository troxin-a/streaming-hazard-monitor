import { queryOptions, useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { useCallback, useSyncExternalStore } from 'react';

import { tokenStorage } from '@/shared/api/tokenStorage';

import { fetchCurrentUser, login } from './api';
import type { User } from './types';

const currentUserQuery = queryOptions({
  queryKey: ['current-user'],
  queryFn: fetchCurrentUser,
  staleTime: Infinity,
  retry: false,
});

/** Есть ли сохранённые токены; меняется при входе, выходе и неудачном обновлении токена. */
export function useIsAuthenticated(): boolean {
  return useSyncExternalStore(tokenStorage.subscribe, () => tokenStorage.get() !== null);
}

/** Запрос текущего пользователя; выполняется только при наличии токенов. */
export function useCurrentUserQuery() {
  const isAuthenticated = useIsAuthenticated();
  return useQuery({ ...currentUserQuery, enabled: isAuthenticated });
}

/** Текущий пользователь; вызывается только внутри RequireAuth. */
export function useCurrentUser(): User {
  const { data } = useQuery({ ...currentUserQuery, enabled: false });
  if (!data) {
    throw new Error('useCurrentUser вызван вне RequireAuth');
  }
  return data;
}

export function useLogin() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: login,
    onSuccess: (tokens) => {
      queryClient.clear();
      tokenStorage.set(tokens);
    },
  });
}

export function useLogout(): () => void {
  const queryClient = useQueryClient();
  return useCallback(() => {
    tokenStorage.clear();
    queryClient.clear();
  }, [queryClient]);
}
