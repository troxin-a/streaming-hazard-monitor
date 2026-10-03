import { zodResolver } from '@hookform/resolvers/zod';
import TextField from '@mui/material/TextField';
import { useForm } from 'react-hook-form';
import { z } from 'zod';

import { type Building, buildings } from '@/entities/building';
import type { Company } from '@/entities/company';
import { useResourceMutation } from '@/shared/api/hooks';
import { errorProps } from '@/shared/ui/form';
import { FormDialog } from '@/shared/ui/FormDialog';
import { SelectField } from '@/shared/ui/SelectField';

const buildingSchema = z.object({
  name: z.string().trim().min(1, 'Введите название'),
  company_uuid: z.string().min(1, 'Выберите компанию'),
});

type BuildingValues = z.infer<typeof buildingSchema>;

interface BuildingFormDialogProps {
  /** Изменяемое здание; без него форма создаёт новое. */
  building?: Building;
  companyOptions: Company[];
  onClose: () => void;
}

export function BuildingFormDialog({ building, companyOptions, onClose }: BuildingFormDialogProps) {
  const save = useResourceMutation((values: BuildingValues) =>
    building ? buildings.update(building.uuid, values) : buildings.create(values),
  );
  const onlyCompany = companyOptions.length === 1 ? companyOptions[0].uuid : '';
  const {
    control,
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<BuildingValues>({
    resolver: zodResolver(buildingSchema),
    defaultValues: {
      name: building?.name ?? '',
      company_uuid: building?.company.uuid ?? onlyCompany,
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
      <SelectField
        control={control}
        name="company_uuid"
        label="Компания"
        options={companyOptions.map((company) => ({ value: company.uuid, label: company.name }))}
      />
    </FormDialog>
  );
}
