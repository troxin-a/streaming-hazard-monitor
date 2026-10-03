import { notify } from '@/shared/lib/notifications';

import { translateApiError } from './errors';
import { tokenStorage, type Tokens } from './tokenStorage';

const API_PREFIX = '/api';
const REFRESH_PATH = '/auth/token/refresh/';
const HTTP_UNAUTHORIZED = 401;
const HTTP_NO_CONTENT = 204;

interface RequestOptions {
  method?: 'GET' | 'POST' | 'PATCH' | 'DELETE';
  body?: unknown;
  /** Подставлять ли access-токен и обновлять его при 401. */
  auth?: boolean;
}

/** Ответ API с кодом ошибки. */
export class ApiError extends Error {
  readonly status: number;
  readonly detail: unknown;

  constructor(status: number, detail: unknown) {
    super(typeof detail === 'string' ? detail : `HTTP ${status}`);
    this.name = 'ApiError';
    this.status = status;
    this.detail = detail;
  }
}

function send(path: string, options: RequestOptions, access?: string): Promise<Response> {
  const headers: Record<string, string> = {};
  if (options.body !== undefined) {
    headers['Content-Type'] = 'application/json';
  }
  if (access) {
    headers.Authorization = `Bearer ${access}`;
  }
  return fetch(`${API_PREFIX}${path}`, {
    method: options.method ?? 'GET',
    headers,
    body: options.body === undefined ? undefined : JSON.stringify(options.body),
  });
}

async function toApiError(response: Response): Promise<ApiError> {
  try {
    const data = (await response.json()) as { detail?: unknown };
    return new ApiError(response.status, data.detail);
  } catch {
    // Тело ответа не JSON (например, прокси вернул 502): остаётся только код.
    return new ApiError(response.status, undefined);
  }
}

async function requestNewTokens(): Promise<Tokens | null> {
  const current = tokenStorage.get();
  if (!current) {
    return null;
  }
  const response = await send(REFRESH_PATH, { method: 'POST', body: { refresh: current.refresh } });
  if (response.status === HTTP_UNAUTHORIZED) {
    tokenStorage.clear();
    notify('Сеанс истёк. Войдите заново.', 'info');
    return null;
  }
  if (!response.ok) {
    throw await toApiError(response);
  }
  const tokens = (await response.json()) as Tokens;
  tokenStorage.set(tokens);
  return tokens;
}

let refreshing: Promise<Tokens | null> | null = null;

/** Обновляет токены; параллельные запросы делят одно обращение к серверу. */
function refreshTokens(): Promise<Tokens | null> {
  refreshing ??= requestNewTokens().finally(() => {
    refreshing = null;
  });
  return refreshing;
}

/** Выполняет запрос к API и возвращает разобранный JSON. */
export async function request<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const auth = options.auth ?? true;
  let response = await send(path, options, auth ? tokenStorage.get()?.access : undefined);

  if (response.status === HTTP_UNAUTHORIZED && auth) {
    const tokens = await refreshTokens();
    if (tokens) {
      response = await send(path, options, tokens.access);
    }
  }

  if (!response.ok) {
    throw await toApiError(response);
  }
  if (response.status === HTTP_NO_CONTENT) {
    return undefined as T;
  }
  return (await response.json()) as T;
}

/** Возвращает текст ошибки для показа пользователю. */
export function getErrorMessage(error: unknown): string {
  if (error instanceof ApiError) {
    return translateApiError(error.status, error.detail);
  }
  return 'Сервер недоступен. Проверьте соединение и попробуйте ещё раз.';
}
