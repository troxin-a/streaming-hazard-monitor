import { zodResolver } from '@hookform/resolvers/zod';
import TextField from '@mui/material/TextField';
import { useForm } from 'react-hook-form';
import { z } from 'zod';

import type { Building } from '@/entities/building';
import { type Device, DEVICE_TYPE_LABELS, DEVICE_TYPES, devices } from '@/entities/device';
import { useResourceMutation } from '@/shared/api/hooks';
import { errorProps } from '@/shared/ui/form';
import { FormDialog } from '@/shared/ui/FormDialog';
import { SelectField } from '@/shared/ui/SelectField';

const deviceSchema = z.object({
  name: z.string().trim().min(1, 'Введите название'),
  serial_number: z.string().trim().min(1, 'Введите серийный номер'),
  type: z.enum(DEVICE_TYPES),
  building_uuid: z.string().min(1, 'Выберите здание'),
});

type DeviceValues = z.infer<typeof deviceSchema>;

const typeOptions = DEVICE_TYPES.map((type) => ({ value: type, label: DEVICE_TYPE_LABELS[type] }));

interface DeviceFormDialogProps {
  /** Изменяемый датчик; без него форма создаёт новый. */
  device?: Device;
  buildingOptions: Building[];
  onClose: () => void;
}

export function DeviceFormDialog({ device, buildingOptions, onClose }: DeviceFormDialogProps) {
  const save = useResourceMutation((values: DeviceValues) =>
    device ? devices.update(device.uuid, values) : devices.create(values),
  );
  const onlyBuilding = buildingOptions.length === 1 ? buildingOptions[0].uuid : '';
  const {
    control,
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<DeviceValues>({
    resolver: zodResolver(deviceSchema),
    defaultValues: {
      name: device?.name ?? '',
      serial_number: device?.serial_number ?? '',
      type: device?.type ?? 'co',
      building_uuid: device?.building.uuid ?? onlyBuilding,
    },
  });

  return (
    <FormDialog
      title={device ? 'Изменить датчик' : 'Новый датчик'}
      error={save.error}
      pending={save.isPending}
      onSubmit={handleSubmit((values) => save.mutate(values, { onSuccess: onClose }))}
      onClose={onClose}
    >
      <TextField label="Название" autoFocus {...errorProps(errors.name)} {...register('name')} />
      <TextField
        label="Серийный номер"
        {...errorProps(errors.serial_number)}
        {...register('serial_number')}
      />
      <SelectField control={control} name="type" label="Тип" options={typeOptions} />
      <SelectField
        control={control}
        name="building_uuid"
        label="Здание"
        options={buildingOptions.map((building) => ({
          value: building.uuid,
          label: `${building.name} — ${building.company.name}`,
        }))}
      />
    </FormDialog>
  );
}
