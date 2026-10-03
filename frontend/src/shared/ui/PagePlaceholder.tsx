import Stack from '@mui/material/Stack';
import Typography from '@mui/material/Typography';

interface PagePlaceholderProps {
  title: string;
  text: string;
}

/** Заголовок страницы с поясняющим текстом вместо содержимого. */
export function PagePlaceholder({ title, text }: PagePlaceholderProps) {
  return (
    <Stack spacing={1}>
      <Typography variant="h4" component="h1">
        {title}
      </Typography>
      <Typography color="text.secondary">{text}</Typography>
    </Stack>
  );
}
