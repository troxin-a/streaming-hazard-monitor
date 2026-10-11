import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import CloseIcon from '@mui/icons-material/Close';
import Dialog from '@mui/material/Dialog';
import DialogTitle from '@mui/material/DialogTitle';
import IconButton from '@mui/material/IconButton';
import Typography from '@mui/material/Typography';
import { type ReactNode, useContext } from 'react';

import { CardContext } from './cardContext';

interface WindowTitleProps {
  title: string;
  /** Показывать ли кнопку «Назад». */
  withBack?: boolean;
  /** Обработчик кнопки «Назад»; без него кнопка отключена. */
  onBack?: () => void;
  /** Обработчик кнопки «Закрыть»; без него кнопка не показывается. */
  onClose?: () => void;
}

/** Заголовок окна с кнопками «Назад» и «Закрыть». */
export function WindowTitle({ title, withBack, onBack, onClose }: WindowTitleProps) {
  return (
    <DialogTitle component="div" sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
      {withBack && (
        <IconButton edge="start" aria-label="Назад" onClick={onBack} disabled={!onBack}>
          <ArrowBackIcon />
        </IconButton>
      )}
      <Typography variant="h6" component="h2" noWrap sx={{ flexGrow: 1 }}>
        {title}
      </Typography>
      {onClose && (
        <IconButton edge="end" aria-label="Закрыть" onClick={onClose}>
          <CloseIcon />
        </IconButton>
      )}
    </DialogTitle>
  );
}

interface DialogWindowProps {
  title: string;
  maxWidth?: 'xs' | 'sm';
  /** Закрывает окно; без обработчика окно закрыть нельзя. */
  onClose?: () => void;
  children: ReactNode;
}

/** Окно диалога с заголовком; внутри карточки записи занимает её место вместо отдельного окна. */
export function DialogWindow({ title, maxWidth = 'xs', onClose, children }: DialogWindowProps) {
  const closeCard = useContext(CardContext);

  if (closeCard) {
    return (
      <>
        <WindowTitle title={title} withBack onBack={onClose} onClose={closeCard} />
        {children}
      </>
    );
  }

  return (
    <Dialog open fullWidth maxWidth={maxWidth} onClose={onClose}>
      <WindowTitle title={title} />
      {children}
    </Dialog>
  );
}
