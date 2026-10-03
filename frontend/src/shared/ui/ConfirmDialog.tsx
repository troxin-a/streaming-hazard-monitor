import Alert from '@mui/material/Alert';
import Button from '@mui/material/Button';
import Dialog from '@mui/material/Dialog';
import DialogActions from '@mui/material/DialogActions';
import DialogContent from '@mui/material/DialogContent';
import DialogContentText from '@mui/material/DialogContentText';
import DialogTitle from '@mui/material/DialogTitle';
import Stack from '@mui/material/Stack';

import { getErrorMessage } from '@/shared/api/client';
import { useResourceMutation } from '@/shared/api/hooks';

interface ConfirmDialogProps {
  title: string;
  text: string;
  confirmLabel?: string;
  action: () => Promise<unknown>;
  onClose: () => void;
}

/** Запрашивает подтверждение, выполняет действие и закрывается при успехе. */
export function ConfirmDialog({
  title,
  text,
  confirmLabel = 'Удалить',
  action,
  onClose,
}: ConfirmDialogProps) {
  const mutation = useResourceMutation(action);

  return (
    <Dialog open fullWidth maxWidth="xs" onClose={mutation.isPending ? undefined : onClose}>
      <DialogTitle>{title}</DialogTitle>
      <DialogContent>
        <Stack spacing={2}>
          {mutation.isError && <Alert severity="error">{getErrorMessage(mutation.error)}</Alert>}
          <DialogContentText>{text}</DialogContentText>
        </Stack>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose} disabled={mutation.isPending}>
          Отмена
        </Button>
        <Button
          color="error"
          variant="contained"
          loading={mutation.isPending}
          onClick={() => mutation.mutate(undefined, { onSuccess: onClose })}
        >
          {confirmLabel}
        </Button>
      </DialogActions>
    </Dialog>
  );
}
