import { request } from './client';

export interface Page<T> {
  items: T[];
  total: number;
  page: number;
  size: number;
  pages: number;
}

export interface PageParams {
  /** Номер страницы, начиная с 1. */
  page: number;
  size: number;
}

export interface Listable<T> {
  key: string;
  list(params: PageParams): Promise<Page<T>>;
}

export interface Resource<T, TCreate, TUpdate, TDetail> extends Listable<T> {
  get(uuid: string): Promise<TDetail>;
  create(data: TCreate): Promise<unknown>;
  update(uuid: string, data: TUpdate): Promise<unknown>;
  remove(uuid: string): Promise<void>;
}

/** Описывает CRUD-эндпоинты сущности, лежащие по адресу /api/{key}/. */
export function createResource<T, TCreate, TUpdate = Partial<TCreate>, TDetail = T>(
  key: string,
): Resource<T, TCreate, TUpdate, TDetail> {
  const base = `/${key}/`;
  return {
    key,
    list: ({ page, size }) => request(`${base}?page=${page}&size=${size}`),
    get: (uuid) => request(`${base}${uuid}/`),
    create: (data) => request(base, { method: 'POST', body: data }),
    update: (uuid, data) => request(`${base}${uuid}/`, { method: 'PATCH', body: data }),
    remove: (uuid) => request(`${base}${uuid}/`, { method: 'DELETE' }),
  };
}
