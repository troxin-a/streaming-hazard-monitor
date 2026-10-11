import Stack from '@mui/material/Stack';
import { useState } from 'react';

import { type Building, buildings } from '@/entities/building';
import { canManage } from '@/features/auth/access';
import { useCurrentUser } from '@/features/auth/hooks';
import { BuildingCard } from '@/features/buildings/BuildingCard';
import { BuildingFormDialog } from '@/features/buildings/BuildingFormDialog';
import { type Column, DataTable } from '@/shared/ui/DataTable';
import { PageHeader } from '@/shared/ui/PageHeader';

const columns: Column<Building>[] = [
  { header: 'Название', render: (building) => building.name },
  { header: 'Компания', render: (building) => building.company.name },
];

export function BuildingsPage() {
  const manage = canManage(useCurrentUser());
  const [creating, setCreating] = useState(false);

  return (
    <Stack spacing={2}>
      <PageHeader title="Здания" onAdd={manage ? () => setCreating(true) : undefined} />
      <DataTable
        resource={buildings}
        columns={columns}
        searchLabel="Поиск по названию"
        card={
          manage
            ? (building, onClose) => (
                <BuildingCard building={building} columns={columns} onClose={onClose} />
              )
            : undefined
        }
      />
      {creating && <BuildingFormDialog onClose={() => setCreating(false)} />}
    </Stack>
  );
}
