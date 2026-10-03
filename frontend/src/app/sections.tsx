import ApartmentIcon from '@mui/icons-material/Apartment';
import BusinessIcon from '@mui/icons-material/Business';
import GroupIcon from '@mui/icons-material/Group';
import MonitorHeartIcon from '@mui/icons-material/MonitorHeart';
import SensorsIcon from '@mui/icons-material/Sensors';
import type { ReactElement } from 'react';

import type { AccessLevel } from '@/features/auth/types';
import { BuildingsPage } from '@/pages/BuildingsPage';
import { CompaniesPage } from '@/pages/CompaniesPage';
import { DevicesPage } from '@/pages/DevicesPage';
import { MonitorPage } from '@/pages/MonitorPage';
import { UsersPage } from '@/pages/UsersPage';

export interface Section {
  path: string;
  label: string;
  icon: ReactElement;
  element: ReactElement;
  /** Кому виден раздел; без поля раздел виден всем. */
  allowed?: AccessLevel[];
}

/** Разделы приложения: из этого списка строятся и меню, и маршруты. */
export const sections: Section[] = [
  { path: '/', label: 'Монитор', icon: <MonitorHeartIcon />, element: <MonitorPage /> },
  { path: '/devices', label: 'Датчики', icon: <SensorsIcon />, element: <DevicesPage /> },
  { path: '/buildings', label: 'Здания', icon: <ApartmentIcon />, element: <BuildingsPage /> },
  {
    path: '/users',
    label: 'Пользователи',
    icon: <GroupIcon />,
    element: <UsersPage />,
    allowed: ['director', 'superuser'],
  },
  {
    path: '/companies',
    label: 'Компании',
    icon: <BusinessIcon />,
    element: <CompaniesPage />,
    allowed: ['superuser'],
  },
];
