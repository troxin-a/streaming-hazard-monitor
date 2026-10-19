import Alert from '@mui/material/Alert';
import Box from '@mui/material/Box';
import Button from '@mui/material/Button';
import Pagination from '@mui/material/Pagination';
import Skeleton from '@mui/material/Skeleton';
import Stack from '@mui/material/Stack';
import Typography from '@mui/material/Typography';
import { useState } from 'react';

import { type Building, buildings } from '@/entities/building';
import type { Company } from '@/entities/company';
import {
  ALERT_LEVEL_COLORS,
  ALERT_LEVEL_LABELS,
  ALERT_LEVELS,
  NORMAL_COLOR,
  NORMAL_LABEL,
} from '@/entities/device';
import { BuildingDevices } from '@/features/monitor/BuildingDevices';
import { DeviceReadingsContext, useDeviceReadingsStore } from '@/features/monitor/deviceReadings';
import {
  DeviceSubscriptionContext,
  useDeviceSubscription,
} from '@/features/monitor/deviceSubscription';
import { useMonitorSocket } from '@/features/monitor/monitorSocket';
import { useDeviceLevels } from '@/features/monitor/useDeviceLevels';
import { getErrorMessage } from '@/shared/api/client';
import { useResourcePage } from '@/shared/api/hooks';

/** Зданий на странице. */
const PAGE_SIZE = 5;

const LEGEND = [
  { label: NORMAL_LABEL, color: NORMAL_COLOR },
  ...ALERT_LEVELS.map((level) => ({
    label: ALERT_LEVEL_LABELS[level],
    color: ALERT_LEVEL_COLORS[level],
  })),
];

/** Здания страницы, сгруппированные по компаниям в порядке их первого появления. */
function groupByCompany(items: Building[]): { company: Company; buildings: Building[] }[] {
  const groups = new Map<string, { company: Company; buildings: Building[] }>();
  for (const building of items) {
    const group = groups.get(building.company.uuid);
    if (group) {
      group.buildings.push(building);
    } else {
      groups.set(building.company.uuid, { company: building.company, buildings: [building] });
    }
  }
  return [...groups.values()];
}

export function MonitorPage() {
  const socket = useMonitorSocket();
  const subscription = useDeviceSubscription(socket);
  const readings = useDeviceReadingsStore(socket);
  useDeviceLevels(socket);
  const [page, setPage] = useState(1);
  const { data, isPending, isError, error, refetch } = useResourcePage(buildings, {
    page,
    size: PAGE_SIZE,
  });

  return (
    <Stack spacing={2}>
      <Typography variant="h4" component="h1">
        Монитор датчиков
      </Typography>
      <Stack direction="row" spacing={2} useFlexGap sx={{ flexWrap: 'wrap' }}>
        {LEGEND.map(({ label, color }) => (
          <Stack key={label} direction="row" spacing={0.75} sx={{ alignItems: 'center' }}>
            <Box sx={{ width: 16, height: 12, borderRadius: 0.5, bgcolor: color }} />
            <Typography variant="body2">{label}</Typography>
          </Stack>
        ))}
      </Stack>
      {isPending && <Skeleton variant="rounded" height={280} aria-label="Загрузка" />}
      {isError && (
        <Alert
          severity="error"
          action={
            <Button color="inherit" size="small" onClick={() => refetch()}>
              Повторить
            </Button>
          }
        >
          {getErrorMessage(error)}
        </Alert>
      )}
      {data && data.total === 0 && <Typography color="text.secondary">Зданий нет.</Typography>}
      {data && data.total > 0 && (
        <DeviceSubscriptionContext value={subscription}>
          <DeviceReadingsContext value={readings}>
            {groupByCompany(data.items).map(({ company, buildings: companyBuildings }) => (
              <Stack key={company.uuid} spacing={3}>
                <Typography variant="h5" component="h2">
                  {company.name}
                </Typography>
                {companyBuildings.map((building) => (
                  <BuildingDevices key={building.uuid} building={building} />
                ))}
              </Stack>
            ))}
            {data.pages > 1 && (
              <Pagination count={data.pages} page={page} onChange={(_, value) => setPage(value)} />
            )}
          </DeviceReadingsContext>
        </DeviceSubscriptionContext>
      )}
    </Stack>
  );
}
