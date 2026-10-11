import { createContext } from 'react';

/** Закрывает карточку записи; вне карточки значение null. */
export const CardContext = createContext<(() => void) | null>(null);
