import Box from '@mui/material/Box';
import Dialog from '@mui/material/Dialog';
import DialogContent from '@mui/material/DialogContent';
import Stack from '@mui/material/Stack';
import Typography from '@mui/material/Typography';
import type { ReactNode } from 'react';

import { CardContext } from './cardContext';
import type { Column } from './DataTable';
import { WindowTitle } from './DialogWindow';

interface RecordCardProps<T> {
  title: string;
  row: T;
  /** Поля записи: подпись и значение, как в колонках таблицы. */
  columns: Column<T>[];
  onClose: () => void;
  /** Диалог, который показывается на месте карточки; без него видны поля и кнопки. */
  view?: ReactNode;
  /** Кнопки действий над записью. */
  children?: ReactNode;
}

/** Карточка записи в модальном окне: поля записи и кнопки действий над ней. */
export function RecordCard<T>({
  title,
  row,
  columns,
  onClose,
  view,
  children,
}: RecordCardProps<T>) {
  return (
    <Dialog open fullWidth maxWidth="xs" onClose={onClose}>
      {view ? (
        <CardContext value={onClose}>{view}</CardContext>
      ) : (
        <>
          <WindowTitle title={title} onClose={onClose} />
          <DialogContent dividers>
            <Box
              component="dl"
              sx={{ display: 'grid', gridTemplateColumns: { sm: '1fr 1fr' }, gap: 2, m: 0 }}
            >
              {columns.map((column) => (
                <div key={column.header}>
                  <Typography component="dt" variant="caption" sx={{ color: 'text.secondary' }}>
                    {column.header}
                  </Typography>
                  <Typography component="dd" sx={{ m: 0, overflowWrap: 'anywhere' }}>
                    {column.render(row)}
                  </Typography>
                </div>
              ))}
            </Box>
          </DialogContent>
          {children && (
            <Stack spacing={1} sx={{ p: 2 }}>
              {children}
            </Stack>
          )}
        </>
      )}
    </Dialog>
  );
}
