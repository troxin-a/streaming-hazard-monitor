import Alert from '@mui/material/Alert';
import Snackbar from '@mui/material/Snackbar';

import { dismissNotification, useNotification } from '@/shared/lib/notifications';

const AUTO_HIDE_MS = 4000;

/** Показывает уведомления, отправленные через notify. */
export function Notifications() {
  const { id, message, severity, open } = useNotification();

  return (
    <Snackbar
      key={id}
      open={open}
      autoHideDuration={AUTO_HIDE_MS}
      anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
      onClose={(_, reason) => {
        // Клик мимо уведомления не должен его прятать: пользователь мог не успеть прочитать.
        if (reason !== 'clickaway') {
          dismissNotification();
        }
      }}
    >
      <Alert severity={severity} variant="filled" onClose={dismissNotification}>
        {message}
      </Alert>
    </Snackbar>
  );
}
