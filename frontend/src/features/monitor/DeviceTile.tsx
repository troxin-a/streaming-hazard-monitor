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
  NO_DATA_COLOR,
  NO_DATA_LABEL,
  NORMAL_COLOR,
  NORMAL_LABEL,
} from '@/entities/device';

import { useDeviceOnline, useDeviceReadings } from './deviceReadings';
import { Sparkline } from './Sparkline';

/** Карточка датчика с графиком показаний на фоне цвета его уровня или серого, пока датчик офлайн. */
export function DeviceTile({ device }: { device: Device }) {
  const theme = useTheme();
  const readings = useDeviceReadings(device.uuid);
  const online = useDeviceOnline(readings);
  const current = readings.at(-1);
  let color = device.level ? ALERT_LEVEL_COLORS[device.level] : NORMAL_COLOR;
  let label = device.level ? ALERT_LEVEL_LABELS[device.level] : NORMAL_LABEL;
  if (!online) {
    color = NO_DATA_COLOR;
    label = NO_DATA_LABEL;
  }

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
      <Typography variant="h6" component="span">
        {current === undefined
          ? 'нет данных'
          : `${current.toFixed(1)} ${DEVICE_TYPE_UNITS[device.type]}`}
      </Typography>
    </Paper>
  );
}
