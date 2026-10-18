import Alert from '@mui/material/Alert';
import Box from '@mui/material/Box';
import Pagination from '@mui/material/Pagination';
import Skeleton from '@mui/material/Skeleton';
import Stack from '@mui/material/Stack';
import Typography from '@mui/material/Typography';
import { keepPreviousData, useQuery } from '@tanstack/react-query';
import { useState } from 'react';

import type { Building } from '@/entities/building';
import { devices, listBuildingDevices } from '@/entities/device';
import { getErrorMessage } from '@/shared/api/client';

import { DeviceTile } from './DeviceTile';

/** Карточек датчиков на странице здания. */
const PAGE_SIZE = 12;

interface BuildingDevicesProps {
  building: Building;
  /** Номер текущей секунды, общий для всех карточек страницы. */
  tick: number;
}

/** Датчики здания карточками со своей постраничной загрузкой. */
export function BuildingDevices({ building, tick }: BuildingDevicesProps) {
  const [page, setPage] = useState(1);
  const { data, isPending, isError, error } = useQuery({
    queryKey: [devices.key, 'monitor', building.uuid, page],
    queryFn: () => listBuildingDevices(building.uuid, page, PAGE_SIZE),
    placeholderData: keepPreviousData,
  });

  return (
    <Stack spacing={1.5}>
      <Typography variant="h6" component="h3">
        {building.name}
      </Typography>
      {isPending && <Skeleton variant="rounded" height={160} aria-label="Загрузка" />}
      {isError && <Alert severity="error">{getErrorMessage(error)}</Alert>}
      {data && data.total === 0 && (
        <Typography color="text.secondary">В здании нет датчиков.</Typography>
      )}
      {data && data.total > 0 && (
        <>
          <Box
            sx={{
              display: 'grid',
              gap: 2,
              gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))',
            }}
          >
            {data.items.map((device) => (
              <DeviceTile key={device.uuid} device={device} tick={tick} />
            ))}
          </Box>
          {data.pages > 1 && (
            <Pagination
              size="small"
              count={data.pages}
              page={page}
              onChange={(_, value) => setPage(value)}
            />
          )}
        </>
      )}
    </Stack>
  );
}
