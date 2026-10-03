import AddIcon from '@mui/icons-material/Add';
import Button from '@mui/material/Button';
import Stack from '@mui/material/Stack';
import Typography from '@mui/material/Typography';

interface PageHeaderProps {
  title: string;
  /** Обработчик кнопки «Добавить»; без него кнопка не показывается. */
  onAdd?: () => void;
}

/** Заголовок раздела с кнопкой добавления записи. */
export function PageHeader({ title, onAdd }: PageHeaderProps) {
  return (
    <Stack
      direction="row"
      spacing={2}
      sx={{ alignItems: 'center', justifyContent: 'space-between' }}
    >
      <Typography variant="h4" component="h1">
        {title}
      </Typography>
      {onAdd && (
        <Button variant="contained" startIcon={<AddIcon />} onClick={onAdd}>
          Добавить
        </Button>
      )}
    </Stack>
  );
}
