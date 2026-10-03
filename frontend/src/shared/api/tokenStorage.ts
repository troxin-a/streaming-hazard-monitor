export interface Tokens {
  access: string;
  refresh: string;
}

const STORAGE_KEY = 'shm.tokens';

type Listener = () => void;

const listeners = new Set<Listener>();

function read(): Tokens | null {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    return raw ? (JSON.parse(raw) as Tokens) : null;
  } catch {
    // Хранилище недоступно или значение повреждено: считаем, что пользователь не вошёл.
    return null;
  }
}

let tokens = read();

function update(next: Tokens | null): void {
  tokens = next;
  listeners.forEach((listener) => listener());
}

// Вход или выход в соседней вкладке.
window.addEventListener('storage', (event) => {
  if (event.key === STORAGE_KEY) {
    update(read());
  }
});

/** Хранилище JWT-токенов с подпиской на изменения. */
export const tokenStorage = {
  get(): Tokens | null {
    return tokens;
  },

  set(next: Tokens): void {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(next));
    update(next);
  },

  clear(): void {
    localStorage.removeItem(STORAGE_KEY);
    update(null);
  },

  subscribe(listener: Listener): () => void {
    listeners.add(listener);
    return () => listeners.delete(listener);
  },
};
