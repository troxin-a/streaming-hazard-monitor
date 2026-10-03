import { zodResolver } from '@hookform/resolvers/zod';
import TextField from '@mui/material/TextField';
import { useMutation } from '@tanstack/react-query';
import { useForm } from 'react-hook-form';
import { z } from 'zod';

import { notify } from '@/shared/lib/notifications';
import { errorProps } from '@/shared/ui/form';
import { FormDialog } from '@/shared/ui/FormDialog';

import { changeOwnPassword } from './api';

const passwordSchema = z
  .object({
    old_password: z.string().min(1, 'Введите текущий пароль'),
    password1: z.string().min(1, 'Введите новый пароль'),
    password2: z.string(),
  })
  .refine((values) => values.password1 === values.password2, {
    path: ['password2'],
    message: 'Пароли не совпадают',
  });

type PasswordValues = z.infer<typeof passwordSchema>;

interface ChangePasswordDialogProps {
  onClose: () => void;
}

/** Меняет пароль текущего пользователя после проверки текущего пароля. */
export function ChangePasswordDialog({ onClose }: ChangePasswordDialogProps) {
  const save = useMutation({
    mutationFn: changeOwnPassword,
    onSuccess: () => notify('Пароль изменён'),
  });
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<PasswordValues>({
    resolver: zodResolver(passwordSchema),
    defaultValues: { old_password: '', password1: '', password2: '' },
  });

  return (
    <FormDialog
      title="Сменить пароль"
      error={save.error}
      pending={save.isPending}
      onSubmit={handleSubmit((values) => save.mutate(values, { onSuccess: onClose }))}
      onClose={onClose}
    >
      <TextField
        label="Текущий пароль"
        type="password"
        autoComplete="current-password"
        autoFocus
        {...errorProps(errors.old_password)}
        {...register('old_password')}
      />
      <TextField
        label="Новый пароль"
        type="password"
        autoComplete="new-password"
        {...errorProps(errors.password1)}
        {...register('password1')}
      />
      <TextField
        label="Повторите новый пароль"
        type="password"
        autoComplete="new-password"
        {...errorProps(errors.password2)}
        {...register('password2')}
      />
    </FormDialog>
  );
}
