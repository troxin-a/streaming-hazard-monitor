import { zodResolver } from '@hookform/resolvers/zod';
import Alert from '@mui/material/Alert';
import Button from '@mui/material/Button';
import Checkbox from '@mui/material/Checkbox';
import FormControlLabel from '@mui/material/FormControlLabel';
import Stack from '@mui/material/Stack';
import TextField from '@mui/material/TextField';
import { useForm } from 'react-hook-form';
import { z } from 'zod';

import { getErrorMessage } from '@/shared/api/client';

import { useLogin } from './hooks';

const loginSchema = z.object({
  username: z.string().trim().min(1, 'Введите логин'),
  password: z.string().min(1, 'Введите пароль'),
  remember_me: z.boolean(),
});

type LoginValues = z.infer<typeof loginSchema>;

export function LoginForm() {
  const login = useLogin();
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<LoginValues>({
    resolver: zodResolver(loginSchema),
    defaultValues: { username: '', password: '', remember_me: false },
  });

  return (
    <Stack
      component="form"
      spacing={2}
      noValidate
      onSubmit={handleSubmit((values) => login.mutate(values))}
    >
      {login.isError && <Alert severity="error">{getErrorMessage(login.error)}</Alert>}
      <TextField
        label="Логин"
        autoComplete="username"
        autoFocus
        error={Boolean(errors.username)}
        helperText={errors.username?.message}
        {...register('username')}
      />
      <TextField
        label="Пароль"
        type="password"
        autoComplete="current-password"
        error={Boolean(errors.password)}
        helperText={errors.password?.message}
        {...register('password')}
      />
      <FormControlLabel
        control={<Checkbox {...register('remember_me')} />}
        label="Запомнить меня"
      />
      <Button type="submit" variant="contained" size="large" loading={login.isPending}>
        Войти
      </Button>
    </Stack>
  );
}
