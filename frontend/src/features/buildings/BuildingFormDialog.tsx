import { zodResolver } from '@hookform/resolvers/zod';
import TextField from '@mui/material/TextField';
import { useForm } from 'react-hook-form';
import { z } from 'zod';

import { type Building, buildings } from '@/entities/building';
import { companies } from '@/entities/company';
import { useCurrentUser } from '@/features/auth/hooks';
import { useResourceMutation } from '@/shared/api/hooks';
import { errorProps } from '@/shared/ui/form';
import { FormDialog } from '@/shared/ui/FormDialog';
import { ResourceField } from '@/shared/ui/ResourceField';

const buildingSchema = z.object({
  name: z.string().trim().min(1, 'Введите название'),
  company_uuid: z.string().min(1, 'Выберите компанию'),
});

type BuildingValues = z.infer<typeof buildingSchema>;

interface BuildingFormDialogProps {
  /** Изменяемое здание; без него форма создаёт новое. */
  building?: Building;
  onClose: () => void;
}

export function BuildingFormDialog({ building, onClose }: BuildingFormDialogProps) {
  const currentUser = useCurrentUser();
  const save = useResourceMutation((values: BuildingValues) =>
    building ? buildings.update(building.uuid, values) : buildings.create(values),
  );
  // Компанию выбирает только суперпользователь, директор работает в своей.
  const ownCompany = currentUser.is_superuser ? '' : (currentUser.company?.uuid ?? '');
  const {
    control,
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<BuildingValues>({
    resolver: zodResolver(buildingSchema),
    defaultValues: {
      name: building?.name ?? '',
      company_uuid: building?.company.uuid ?? ownCompany,
    },
  });

  return (
    <FormDialog
      title={building ? 'Изменить здание' : 'Новое здание'}
      error={save.error}
      pending={save.isPending}
      onSubmit={handleSubmit((values) => save.mutate(values, { onSuccess: onClose }))}
      onClose={onClose}
    >
      <TextField label="Название" autoFocus {...errorProps(errors.name)} {...register('name')} />
      {currentUser.is_superuser && (
        <ResourceField
          control={control}
          name="company_uuid"
          label="Компания"
          resource={companies}
          initialOption={building?.company}
        />
      )}
    </FormDialog>
  );
}
