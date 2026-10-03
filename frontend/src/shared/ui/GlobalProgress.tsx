import Fade from '@mui/material/Fade';
import LinearProgress from '@mui/material/LinearProgress';
import { useIsFetching, useIsMutating } from '@tanstack/react-query';

/** Задержка появления, чтобы полоса не мигала на быстрых запросах. */
const SHOW_DELAY_MS = 150;

/** Тонкая полоса вверху экрана, видимая, пока выполняется любой запрос к API. */
export function GlobalProgress() {
  const busy = useIsFetching() + useIsMutating() > 0;

  return (
    <Fade in={busy} unmountOnExit style={{ transitionDelay: busy ? `${SHOW_DELAY_MS}ms` : '0ms' }}>
      <LinearProgress
        color="secondary"
        aria-label="Выполняется запрос"
        sx={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          height: 3,
          zIndex: (theme) => theme.zIndex.tooltip + 1,
        }}
      />
    </Fade>
  );
}
