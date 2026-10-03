import { keepPreviousData, useMutation, useQuery, useQueryClient } from '@tanstack/react-query';

import type { Listable, PageParams } from './resource';

/** Сколько найденных записей показывает поле с поиском. */
const SEARCH_SIZE = 20;

/** Страница списка сущности. */
export function useResourcePage<T>(resource: Listable<T>, params: PageParams) {
  return useQuery({
    queryKey: [resource.key, 'page', params.page, params.size, params.search ?? ''],
    queryFn: () => resource.list(params),
    placeholderData: keepPreviousData,
  });
}

/** Записи сущности, найденные по части названия, для поля с поиском. */
export function useResourceSearch<T>(resource: Listable<T>, search: string) {
  return useQuery({
    queryKey: [resource.key, 'search', search],
    queryFn: () => resource.list({ page: 1, size: SEARCH_SIZE, search }),
    select: (page) => page.items,
    placeholderData: keepPreviousData,
  });
}

/** Изменяющий запрос, после которого загруженные данные перечитываются с сервера. */
export function useResourceMutation<TVariables = void>(
  mutationFn: (variables: TVariables) => Promise<unknown>,
) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn,
    onSuccess: () => queryClient.invalidateQueries(),
  });
}
