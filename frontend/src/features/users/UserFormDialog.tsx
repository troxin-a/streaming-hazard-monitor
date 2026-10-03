import { zodResolver } from '@hookform/resolvers/zod';
import TextField from '@mui/material/TextField';
import { useMemo } from 'react';
import { useForm, useWatch } from 'react-hook-form';
import { z } from 'zod';

import { buildings } from '@/entities/building';
import { companies } from '@/entities/company';
import { ROLE_LABELS, type User, USER_ROLES, users } from '@/entities/user';
import { useCurrentUser } from '@/features/auth/hooks';
import { useResourceMutation } from '@/shared/api/hooks';
import { errorProps } from '@/shared/ui/form';
import { FormDialog } from '@/shared/ui/FormDialog';
import { ResourceField } from '@/shared/ui/ResourceField';
import { SelectField } from '@/shared/ui/SelectField';

const roleOptions = USER_ROLES.map((role) => ({ value: role, label: ROLE_LABELS[role] }));

interface SchemaRules {
  isCreate: boolean;
  /** Компанию выбирает только суперпользователь, у остальных она берётся из их собственной. */
  companyRequired: boolean;
  /** Суперпользователь не привязан к зданию, сотруднику оно обязательно. */
  buildingRequired: boolean;
}

function buildSchema({ isCreate, companyRequired, buildingRequired }: SchemaRules) {
  return z
    .object({
      username: z.string().trim(),
      name: z.string().trim().min(1, 'Введите имя'),
      role: z.enum(USER_ROLES),
      company_uuid: z.string(),
      building_uuid: z.string(),
      password1: z.string(),
      password2: z.string(),
    })
    .superRefine((values, ctx) => {
      const require = (field: keyof typeof values, message: string) =>
        ctx.addIssue({ code: 'custom', path: [field], message });

      if (values.password1 !== values.password2) {
        require('password2', 'Пароли не совпадают');
      }
      if (isCreate && !values.username) {
        require('username', 'Введите логин');
      }
      if (isCreate && !values.password1) {
        require('password1', 'Введите пароль');
      }
      if (companyRequired && !values.company_uuid) {
        require('company_uuid', 'Выберите компанию');
      }
      if (buildingRequired && values.role === 'employee' && !values.building_uuid) {
        require('building_uuid', 'Выберите здание');
      }
    });
}

type UserValues = z.infer<ReturnType<typeof buildSchema>>;

interface UserFormDialogProps {
  /** Изменяемый пользователь; без него форма создаёт нового. */
  user?: User;
  onClose: () => void;
}

export function UserFormDialog({ user, onClose }: UserFormDialogProps) {
  const { is_superuser: isSuperuser } = useCurrentUser();
  const isCreate = !user;
  const targetIsSuperuser = Boolean(user?.is_superuser);
  const schema = useMemo(
    () =>
      buildSchema({
        isCreate,
        companyRequired: isSuperuser && !targetIsSuperuser,
        buildingRequired: !targetIsSuperuser,
      }),
    [isCreate, isSuperuser, targetIsSuperuser],
  );

  const successMessage = user ? 'Пользователь изменён' : 'Пользователь создан';
  const save = useResourceMutation((values: UserValues) => {
    // Роль и компанию бэкенд принимает только от суперпользователя.
    const restricted = isSuperuser
      ? { role: values.role, company_uuid: values.company_uuid || undefined }
      : {};
    if (user) {
      return users.update(user.uuid, {
        ...restricted,
        name: values.name,
        building_uuid: values.building_uuid || null,
      });
    }
    return users.create({
      role: 'employee',
      ...restricted,
      username: values.username,
      name: values.name,
      building_uuid: values.building_uuid || undefined,
      password1: values.password1,
      password2: values.password2,
    });
  }, successMessage);

  const {
    control,
    register,
    handleSubmit,
    setValue,
    formState: { errors },
  } = useForm<UserValues>({
    resolver: zodResolver(schema),
    defaultValues: {
      username: '',
      name: user?.name ?? '',
      role: user?.role ?? 'employee',
      company_uuid: user?.company?.uuid ?? '',
      building_uuid: user?.building?.uuid ?? '',
      password1: '',
      password2: '',
    },
  });

  const companyUuid = useWatch({ control, name: 'company_uuid' });

  return (
    <FormDialog
      title={isCreate ? 'Новый пользователь' : `Изменить пользователя ${user.username}`}
      error={save.error}
      pending={save.isPending}
      onSubmit={handleSubmit((values) => save.mutate(values, { onSuccess: onClose }))}
      onClose={onClose}
    >
      {isCreate && (
        <TextField
          label="Логин"
          autoComplete="off"
          autoFocus
          {...errorProps(errors.username)}
          {...register('username')}
        />
      )}
      <TextField label="Имя" {...errorProps(errors.name)} {...register('name')} />
      {isSuperuser && (
        <SelectField control={control} name="role" label="Роль" options={roleOptions} />
      )}
      {isSuperuser && (
        <ResourceField
          control={control}
          name="company_uuid"
          label="Компания"
          resource={companies}
          initialOption={user?.company}
          onValueChange={() => setValue('building_uuid', '')}
        />
      )}
      <ResourceField
        control={control}
        name="building_uuid"
        label="Здание"
        resource={buildings}
        initialOption={user?.building}
        filter={companyUuid ? (building) => building.company.uuid === companyUuid : undefined}
      />
      {isCreate && (
        <TextField
          label="Пароль"
          type="password"
          autoComplete="new-password"
          {...errorProps(errors.password1)}
          {...register('password1')}
        />
      )}
      {isCreate && (
        <TextField
          label="Повторите пароль"
          type="password"
          autoComplete="new-password"
          {...errorProps(errors.password2)}
          {...register('password2')}
        />
      )}
    </FormDialog>
  );
}
