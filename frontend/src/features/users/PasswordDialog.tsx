import { zodResolver } from '@hookform/resolvers/zod';
import TextField from '@mui/material/TextField';
import { useForm } from 'react-hook-form';
import { z } from 'zod';

import { type User, users } from '@/entities/user';
import { useResourceMutation } from '@/shared/api/hooks';
import { errorProps } from '@/shared/ui/form';
import { FormDialog } from '@/shared/ui/FormDialog';

const passwordSchema = z
  .object({
    password1: z.string().min(1, 'Введите пароль'),
    password2: z.string(),
  })
  .refine((values) => values.password1 === values.password2, {
    path: ['password2'],
    message: 'Пароли не совпадают',
  });

type PasswordValues = z.infer<typeof passwordSchema>;

interface PasswordDialogProps {
  user: User;
  onClose: () => void;
}

/** Задаёт пользователю новый пароль. */
export function PasswordDialog({ user, onClose }: PasswordDialogProps) {
  const save = useResourceMutation((values: PasswordValues) => users.update(user.uuid, values));
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<PasswordValues>({
    resolver: zodResolver(passwordSchema),
    defaultValues: { password1: '', password2: '' },
  });

  return (
    <FormDialog
      title={`Сменить пароль ${user.username}`}
      error={save.error}
      pending={save.isPending}
      onSubmit={handleSubmit((values) => save.mutate(values, { onSuccess: onClose }))}
      onClose={onClose}
    >
      <TextField
        label="Новый пароль"
        type="password"
        autoComplete="new-password"
        autoFocus
        {...errorProps(errors.password1)}
        {...register('password1')}
      />
      <TextField
        label="Повторите пароль"
        type="password"
        autoComplete="new-password"
        {...errorProps(errors.password2)}
        {...register('password2')}
      />
    </FormDialog>
  );
}
