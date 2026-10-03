import Alert from '@mui/material/Alert';
import Button from '@mui/material/Button';
import Dialog from '@mui/material/Dialog';
import DialogActions from '@mui/material/DialogActions';
import DialogContent from '@mui/material/DialogContent';
import DialogTitle from '@mui/material/DialogTitle';
import Stack from '@mui/material/Stack';
import type { FormEventHandler, ReactNode } from 'react';

import { getErrorMessage } from '@/shared/api/client';

interface FormDialogProps {
  title: string;
  /** Ошибка сохранения; null, если её нет. */
  error: unknown;
  pending: boolean;
  onSubmit: FormEventHandler<HTMLFormElement>;
  onClose: () => void;
  children: ReactNode;
}

/** Диалог с формой, кнопками «Отмена» и «Сохранить» и показом ошибки сохранения. */
export function FormDialog({
  title,
  error,
  pending,
  onSubmit,
  onClose,
  children,
}: FormDialogProps) {
  return (
    <Dialog open fullWidth maxWidth="xs" onClose={pending ? undefined : onClose}>
      <form noValidate onSubmit={onSubmit}>
        <DialogTitle>{title}</DialogTitle>
        <DialogContent>
          <Stack spacing={2} sx={{ pt: 1 }}>
            {error != null && <Alert severity="error">{getErrorMessage(error)}</Alert>}
            {children}
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={onClose} disabled={pending}>
            Отмена
          </Button>
          <Button type="submit" variant="contained" loading={pending}>
            Сохранить
          </Button>
        </DialogActions>
      </form>
    </Dialog>
  );
}
