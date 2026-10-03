import Stack from '@mui/material/Stack';
import { useState } from 'react';

import { type Building, buildings } from '@/entities/building';
import { canManage } from '@/features/auth/access';
import { useCurrentUser } from '@/features/auth/hooks';
import { BuildingFormDialog } from '@/features/buildings/BuildingFormDialog';
import { ConfirmDialog } from '@/shared/ui/ConfirmDialog';
import { type Column, DataTable } from '@/shared/ui/DataTable';
import { PageHeader } from '@/shared/ui/PageHeader';
import { RowActions } from '@/shared/ui/RowActions';

const columns: Column<Building>[] = [
  { header: 'Название', render: (building) => building.name },
  { header: 'Компания', render: (building) => building.company.name },
];

export function BuildingsPage() {
  const manage = canManage(useCurrentUser());
  const [editing, setEditing] = useState<Building | 'new' | null>(null);
  const [deleting, setDeleting] = useState<Building | null>(null);

  return (
    <Stack spacing={2}>
      <PageHeader title="Здания" onAdd={manage ? () => setEditing('new') : undefined} />
      <DataTable
        resource={buildings}
        columns={columns}
        searchLabel="Поиск по названию"
        actions={
          manage
            ? (building) => (
                <RowActions
                  onEdit={() => setEditing(building)}
                  onDelete={() => setDeleting(building)}
                />
              )
            : undefined
        }
      />
      {editing && (
        <BuildingFormDialog
          building={editing === 'new' ? undefined : editing}
          onClose={() => setEditing(null)}
        />
      )}
      {deleting && (
        <ConfirmDialog
          title="Удалить здание?"
          text={`Здание «${deleting.name}» будет удалено.`}
          action={() => buildings.remove(deleting.uuid)}
          onClose={() => setDeleting(null)}
        />
      )}
    </Stack>
  );
}
