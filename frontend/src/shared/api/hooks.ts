import { keepPreviousData, useMutation, useQuery, useQueryClient } from '@tanstack/react-query';

import type { Listable, PageParams } from './resource';

/** Сколько записей загружается для выпадающих списков; это максимум, который отдаёт API. */
const OPTIONS_SIZE = 100;

/** Страница списка сущности. */
export function useResourcePage<T>(resource: Listable<T>, params: PageParams) {
  return useQuery({
    queryKey: [resource.key, 'page', params.page, params.size],
    queryFn: () => resource.list(params),
    placeholderData: keepPreviousData,
  });
}

/** Записи сущности для выпадающего списка. */
export function useResourceOptions<T>(resource: Listable<T>, enabled = true) {
  return useQuery({
    queryKey: [resource.key, 'options'],
    queryFn: () => resource.list({ page: 1, size: OPTIONS_SIZE }),
    select: (page) => page.items,
    enabled,
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
