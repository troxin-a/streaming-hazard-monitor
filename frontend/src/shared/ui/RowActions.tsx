import DeleteIcon from '@mui/icons-material/Delete';
import EditIcon from '@mui/icons-material/Edit';
import IconButton from '@mui/material/IconButton';
import Tooltip from '@mui/material/Tooltip';
import type { ReactNode } from 'react';

interface RowActionsProps {
  onEdit: () => void;
  onDelete: () => void;
  deleteDisabled?: boolean;
  /** Дополнительные кнопки перед «Изменить». */
  children?: ReactNode;
}

/** Кнопки действий над строкой таблицы. */
export function RowActions({ onEdit, onDelete, deleteDisabled, children }: RowActionsProps) {
  return (
    <>
      {children}
      <Tooltip title="Изменить">
        <IconButton size="small" aria-label="Изменить" onClick={onEdit}>
          <EditIcon fontSize="small" />
        </IconButton>
      </Tooltip>
      <Tooltip title="Удалить">
        {/* span нужен, чтобы подсказка работала и на отключённой кнопке */}
        <span>
          <IconButton
            size="small"
            aria-label="Удалить"
            onClick={onDelete}
            disabled={deleteDisabled}
          >
            <DeleteIcon fontSize="small" />
          </IconButton>
        </span>
      </Tooltip>
    </>
  );
}
