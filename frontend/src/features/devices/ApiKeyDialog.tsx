import ContentCopyIcon from '@mui/icons-material/ContentCopy';
import Alert from '@mui/material/Alert';
import Button from '@mui/material/Button';
import Dialog from '@mui/material/Dialog';
import DialogActions from '@mui/material/DialogActions';
import DialogContent from '@mui/material/DialogContent';
import DialogContentText from '@mui/material/DialogContentText';
import DialogTitle from '@mui/material/DialogTitle';
import IconButton from '@mui/material/IconButton';
import InputAdornment from '@mui/material/InputAdornment';
import Stack from '@mui/material/Stack';
import TextField from '@mui/material/TextField';
import Tooltip from '@mui/material/Tooltip';
import { useState } from 'react';

import { type Device, issueApiKey } from '@/entities/device';
import { getErrorMessage } from '@/shared/api/client';
import { useResourceMutation } from '@/shared/api/hooks';

interface ApiKeyDialogProps {
  device: Device;
  onClose: () => void;
}

/** Выпускает API-ключ датчика и один раз показывает его. */
export function ApiKeyDialog({ device, onClose }: ApiKeyDialogProps) {
  const [key, setKey] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);
  const issue = useResourceMutation(() => issueApiKey(device.uuid).then(setKey));

  const copy = async () => {
    if (key) {
      await navigator.clipboard.writeText(key);
      setCopied(true);
    }
  };

  return (
    <Dialog open fullWidth maxWidth="sm" onClose={issue.isPending ? undefined : onClose}>
      <DialogTitle>API-ключ датчика «{device.name}»</DialogTitle>
      <DialogContent>
        <Stack spacing={2}>
          {issue.isError && <Alert severity="error">{getErrorMessage(issue.error)}</Alert>}
          {key ? (
            <>
              <Alert severity="warning">
                Скопируйте ключ сейчас: он показывается один раз и на сервере не хранится.
              </Alert>
              <TextField
                label="API-ключ"
                value={key}
                slotProps={{
                  input: {
                    readOnly: true,
                    sx: { fontFamily: 'monospace' },
                    endAdornment: (
                      <InputAdornment position="end">
                        <Tooltip title={copied ? 'Скопировано' : 'Скопировать'}>
                          <IconButton edge="end" aria-label="Скопировать ключ" onClick={copy}>
                            <ContentCopyIcon />
                          </IconButton>
                        </Tooltip>
                      </InputAdornment>
                    ),
                  },
                }}
              />
            </>
          ) : (
            <DialogContentText>
              Датчик будет отправлять показания с этим ключом в заголовке X-API-Key.
            </DialogContentText>
          )}
        </Stack>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose} disabled={issue.isPending}>
          {key ? 'Закрыть' : 'Отмена'}
        </Button>
        {!key && (
          <Button variant="contained" loading={issue.isPending} onClick={() => issue.mutate()}>
            Выпустить ключ
          </Button>
        )}
      </DialogActions>
    </Dialog>
  );
}
