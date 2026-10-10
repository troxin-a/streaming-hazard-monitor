const SESSION_EXPIRED = 'Сеанс истёк. Войдите заново.';

/** Тексты ошибок бэкенда и их перевод. */
const DETAIL_TRANSLATIONS: Record<string, string> = {
  'Incorrect username or password': 'Неверный логин или пароль',
  'Not authenticated': 'Требуется вход',
  'Invalid authorization token': SESSION_EXPIRED,
  'Token invalid type': SESSION_EXPIRED,
  'Token invalid signature error': SESSION_EXPIRED,
  'Token decode error': SESSION_EXPIRED,
  'Token expired signature error': SESSION_EXPIRED,
  'User inactive': 'Пользователь удалён или отключён',
  'Access denied': 'Недостаточно прав',
  'Cannot delete yourself': 'Нельзя удалить самого себя',
  'User not found': 'Пользователь не найден',
  'Company not found': 'Компания не найдена',
  'Building not found': 'Здание не найдено',
  'Device not found': 'Датчик не найден',
  'Device has no api key': 'У датчика нет API-ключа',
  'Device already has an api key': 'У датчика уже есть API-ключ',
  'Thresholds not found': 'У датчика нет своих порогов',
  'Passwords must be the same': 'Пароли не совпадают',
  'Incorrect password': 'Текущий пароль указан неверно',
  'Building is required for an employee': 'Сотруднику нужно указать здание',
  'Company is required': 'Укажите компанию',
};

const STATUS_MESSAGES: Record<number, string> = {
  400: 'Проверьте правильность заполнения полей',
  401: 'Требуется вход',
  403: 'Недостаточно прав',
  404: 'Запись не найдена',
  409: 'Запись с такими данными уже существует или используется другими записями',
  422: 'Проверьте правильность заполнения полей',
};

interface ValidationIssue {
  message?: string;
}

function translate(text: unknown): string | undefined {
  return typeof text === 'string' ? DETAIL_TRANSLATIONS[text] : undefined;
}

/** Переводит ответ API с ошибкой; неизвестный текст заменяется общей фразой по коду ответа. */
export function translateApiError(status: number, detail: unknown): string {
  if (Array.isArray(detail)) {
    const messages = (detail as ValidationIssue[]).map((issue) => translate(issue.message));
    if (messages.length > 0 && messages.every(Boolean)) {
      return messages.join('; ');
    }
  }
  const fallback =
    status >= 500 ? 'Ошибка сервера. Попробуйте позже.' : `Ошибка запроса (${status})`;
  return translate(detail) ?? STATUS_MESSAGES[status] ?? fallback;
}
