import Alert from '@mui/material/Alert';
import Button from '@mui/material/Button';
import DialogActions from '@mui/material/DialogActions';
import DialogContent from '@mui/material/DialogContent';
import Stack from '@mui/material/Stack';
import type { FormEventHandler, ReactNode } from 'react';

import { getErrorMessage } from '@/shared/api/client';

import { DialogWindow } from './DialogWindow';

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
    <DialogWindow title={title} onClose={pending ? undefined : onClose}>
      <form noValidate onSubmit={onSubmit}>
        <DialogContent sx={{ pt: 0 }}>
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
    </DialogWindow>
  );
}
