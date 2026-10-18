import Box from '@mui/material/Box';
import Paper from '@mui/material/Paper';
import Stack from '@mui/material/Stack';
import Typography from '@mui/material/Typography';
import { useTheme } from '@mui/material/styles';

import {
  ALERT_LEVEL_COLORS,
  ALERT_LEVEL_LABELS,
  type Device,
  DEVICE_TYPE_LABELS,
  DEVICE_TYPE_UNITS,
  NORMAL_COLOR,
  NORMAL_LABEL,
} from '@/entities/device';

import { Sparkline } from './Sparkline';
import { useMockReadings } from './useMockReadings';

interface DeviceTileProps {
  device: Device;
  /** Номер текущей секунды, общий для всех карточек страницы. */
  tick: number;
}

/** Карточка датчика с графиком показаний на фоне цвета его уровня. */
export function DeviceTile({ device, tick }: DeviceTileProps) {
  const theme = useTheme();
  const readings = useMockReadings(device.uuid, tick);
  const color = device.level ? ALERT_LEVEL_COLORS[device.level] : NORMAL_COLOR;
  const label = device.level ? ALERT_LEVEL_LABELS[device.level] : NORMAL_LABEL;
  const current = readings[readings.length - 1];

  return (
    <Paper variant="outlined" sx={{ p: 2 }}>
      <Stack direction="row" spacing={1} sx={{ alignItems: 'center' }}>
        <Typography variant="subtitle1" noWrap sx={{ flexGrow: 1 }}>
          {device.name}
        </Typography>
        <Typography variant="body2" color="text.secondary" noWrap>
          {label}
        </Typography>
      </Stack>
      <Typography variant="body2" color="text.secondary" noWrap>
        {DEVICE_TYPE_LABELS[device.type]}
      </Typography>
      <Box
        sx={{
          mt: 1,
          px: 1,
          py: 0.5,
          borderRadius: 1,
          bgcolor: color,
          color: theme.palette.getContrastText(color),
        }}
      >
        <Sparkline values={readings} />
      </Box>
      <Stack direction="row" sx={{ justifyContent: 'space-between', alignItems: 'baseline' }}>
        <Typography variant="h6" component="span">
          {current.toFixed(1)} {DEVICE_TYPE_UNITS[device.type]}
        </Typography>
        <Typography variant="caption" color="text.secondary">
          демо-данные
        </Typography>
      </Stack>
    </Paper>
  );
}
