import { zodResolver } from '@hookform/resolvers/zod';
import Alert from '@mui/material/Alert';
import Box from '@mui/material/Box';
import Button from '@mui/material/Button';
import Dialog from '@mui/material/Dialog';
import DialogActions from '@mui/material/DialogActions';
import DialogContent from '@mui/material/DialogContent';
import DialogTitle from '@mui/material/DialogTitle';
import InputAdornment from '@mui/material/InputAdornment';
import Skeleton from '@mui/material/Skeleton';
import Stack from '@mui/material/Stack';
import TextField from '@mui/material/TextField';
import { useQuery } from '@tanstack/react-query';
import { useForm } from 'react-hook-form';
import { z } from 'zod';

import {
  ALERT_LEVEL_LABELS,
  ALERT_LEVELS,
  type AlertLevel,
  createThresholds,
  type Device,
  DEVICE_TYPE_LABELS,
  DEVICE_TYPE_UNITS,
  getThresholds,
  resetThresholds,
  type Threshold,
  thresholdsKey,
  type ThresholdValues,
  updateThresholds,
} from '@/entities/device';
import { getErrorMessage } from '@/shared/api/client';
import { useResourceMutation } from '@/shared/api/hooks';
import { errorProps } from '@/shared/ui/form';

/** Число, которое помещается в Numeric(10, 3) на сервере. */
const DECIMAL_PATTERN = /^-?\d{1,7}(\.\d{1,3})?$/;
/** Высота заглушки на время загрузки, примерно как у четырёх полей формы. */
const SKELETON_HEIGHT = 280;

/** Убирает незначащие нули: «20.000» превращается в «20». */
function formatValue(value: string): string {
  return String(Number(value));
}

/** Раскладывает пороги по уровням; для уровня без порога остаётся пустая строка. */
function toValues(thresholds: Threshold[]): ThresholdValues {
  const values: ThresholdValues = { level_1: '', level_2: '', level_3: '', level_4: '' };
  for (const threshold of thresholds) {
    values[threshold.level] = formatValue(threshold.value);
  }
  return values;
}

/** Схема формы: пустое поле заменяется загруженным значением этого уровня. */
function buildSchema(loaded: ThresholdValues) {
  const level = (key: AlertLevel) =>
    z
      .string()
      .transform((text) => (text.trim() || loaded[key]).replace(',', '.'))
      .refine((text) => text !== '', 'Введите значение')
      .refine(
        (text) => text === '' || DECIMAL_PATTERN.test(text),
        'Число, не больше трёх знаков после запятой',
      );

  return z
    .object({
      level_1: level('level_1'),
      level_2: level('level_2'),
      level_3: level('level_3'),
      level_4: level('level_4'),
    })
    .superRefine((values, context) => {
      ALERT_LEVELS.slice(1).forEach((key, index) => {
        if (Number(values[key]) <= Number(values[ALERT_LEVELS[index]])) {
          context.addIssue({
            code: 'custom',
            path: [key],
            message: 'Должен быть выше порога предыдущего уровня',
          });
        }
      });
    });
}

interface ThresholdsFormProps {
  device: Device;
  thresholds: Threshold[];
  /** Можно ли менять пороги; без этого форма только показывает значения. */
  editable: boolean;
  onClose: () => void;
}

function ThresholdsForm({ device, thresholds, editable, onClose }: ThresholdsFormProps) {
  const loaded = toValues(thresholds);
  const hasOwn = thresholds.some((threshold) => !threshold.is_default);
  const unit = DEVICE_TYPE_UNITS[device.type];

  const save = useResourceMutation(
    (values: ThresholdValues) =>
      hasOwn ? updateThresholds(device.uuid, values) : createThresholds(device.uuid, values),
    'Пороги сохранены',
  );
  const reset = useResourceMutation(
    () => resetThresholds(device.uuid),
    'Действуют значения по умолчанию',
  );
  const pending = save.isPending || reset.isPending;
  const error = save.error ?? reset.error;

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<ThresholdValues>({
    resolver: zodResolver(buildSchema(loaded)),
    defaultValues: loaded,
  });

  return (
    <form
      noValidate
      onSubmit={handleSubmit((values) => save.mutate(values, { onSuccess: onClose }))}
    >
      <DialogContent>
        <Stack spacing={2} sx={{ pt: 1 }}>
          {error != null && <Alert severity="error">{getErrorMessage(error)}</Alert>}
          {thresholds.length === 0 ? (
            <Alert severity="warning">
              Для типа «{DEVICE_TYPE_LABELS[device.type]}» значения по умолчанию не заданы.
            </Alert>
          ) : (
            <Alert severity="info">
              {hasOwn
                ? 'Для датчика заданы свои пороги.'
                : `Действуют значения по умолчанию для типа «${DEVICE_TYPE_LABELS[device.type]}».`}
            </Alert>
          )}
          {ALERT_LEVELS.map((level) => (
            <TextField
              key={level}
              label={ALERT_LEVEL_LABELS[level]}
              placeholder={loaded[level]}
              disabled={!editable}
              slotProps={{
                inputLabel: { shrink: true },
                htmlInput: { inputMode: 'decimal' },
                input: {
                  endAdornment: <InputAdornment position="end">{unit}</InputAdornment>,
                },
              }}
              {...errorProps(errors[level])}
              {...register(level)}
            />
          ))}
        </Stack>
      </DialogContent>
      <DialogActions>
        {editable && hasOwn && (
          <Button
            color="warning"
            disabled={pending}
            onClick={() => reset.mutate(undefined, { onSuccess: onClose })}
          >
            Сбросить к умолчаниям
          </Button>
        )}
        <Box sx={{ flexGrow: 1 }} />
        <Button onClick={onClose} disabled={pending}>
          {editable ? 'Отмена' : 'Закрыть'}
        </Button>
        {editable && (
          <Button
            type="submit"
            variant="contained"
            loading={save.isPending}
            disabled={reset.isPending}
          >
            Сохранить
          </Button>
        )}
      </DialogActions>
    </form>
  );
}

interface ThresholdsDialogProps {
  device: Device;
  /** Можно ли менять пороги. */
  editable: boolean;
  onClose: () => void;
}

/** Показывает пороги датчика по уровням алерта и даёт задать свои вместо значений по умолчанию. */
export function ThresholdsDialog({ device, editable, onClose }: ThresholdsDialogProps) {
  const { data, isPending, isError, error } = useQuery({
    queryKey: thresholdsKey(device.uuid),
    queryFn: () => getThresholds(device.uuid),
  });

  return (
    <Dialog open fullWidth maxWidth="xs" onClose={onClose}>
      <DialogTitle>Пороги датчика «{device.name}»</DialogTitle>
      {data ? (
        <ThresholdsForm device={device} thresholds={data} editable={editable} onClose={onClose} />
      ) : (
        <>
          <DialogContent>
            {isPending && (
              <Skeleton variant="rounded" height={SKELETON_HEIGHT} aria-label="Загрузка" />
            )}
            {isError && <Alert severity="error">{getErrorMessage(error)}</Alert>}
          </DialogContent>
          <DialogActions>
            <Button onClick={onClose}>Закрыть</Button>
          </DialogActions>
        </>
      )}
    </Dialog>
  );
}
