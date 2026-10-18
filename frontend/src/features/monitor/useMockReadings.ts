import { useEffect, useMemo, useState } from 'react';

/** Сколько последних показаний держит график. */
const HISTORY = 60;
/** Как часто приходит новое демо-показание, мс. */
const INTERVAL = 1000;

/** Номер текущей секунды; меняется раз в секунду, одновременно у всех, кто его читает. */
export function useSecondTick(): number {
  const [tick, setTick] = useState(() => Math.floor(Date.now() / INTERVAL));

  useEffect(() => {
    const timer = setInterval(() => setTick(Math.floor(Date.now() / INTERVAL)), INTERVAL);
    return () => clearInterval(timer);
  }, []);

  return tick;
}

/** Число от 0 до 1, одинаковое для одной и той же пары датчика и секунды. */
function noise(seed: number, second: number): number {
  const x = Math.sin(seed * 12.9898 + second * 78.233) * 43758.5453;
  return x - Math.floor(x);
}

function hashSeed(text: string): number {
  let hash = 0;
  for (const char of text) {
    hash = (hash * 31 + char.charCodeAt(0)) % 100000;
  }
  return hash;
}

/** Демо-показания датчика за последние секунды: плавная волна с шумом. */
export function useMockReadings(deviceUuid: string, tick: number): number[] {
  const seed = hashSeed(deviceUuid);
  return useMemo(
    () =>
      Array.from({ length: HISTORY }, (_, index) => {
        const second = tick - HISTORY + 1 + index;
        return 12 + 3 * Math.sin(second / 9 + seed) + noise(seed, second);
      }),
    [seed, tick],
  );
}
