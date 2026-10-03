import Stack from '@mui/material/Stack';
import { useState } from 'react';

import { buildings } from '@/entities/building';
import { companies } from '@/entities/company';
import { type User, users } from '@/entities/user';
import { ACCESS_LEVEL_LABELS, getAccessLevel } from '@/features/auth/access';
import { useCurrentUser } from '@/features/auth/hooks';
import { UserFormDialog } from '@/features/users/UserFormDialog';
import { useResourceOptions } from '@/shared/api/hooks';
import { ConfirmDialog } from '@/shared/ui/ConfirmDialog';
import { type Column, DataTable } from '@/shared/ui/DataTable';
import { PageHeader } from '@/shared/ui/PageHeader';
import { RowActions } from '@/shared/ui/RowActions';

const columns: Column<User>[] = [
  { header: 'Имя', render: (user) => user.name },
  { header: 'Логин', render: (user) => user.username },
  { header: 'Роль', render: (user) => ACCESS_LEVEL_LABELS[getAccessLevel(user)] },
  { header: 'Компания', render: (user) => user.company?.name ?? '—' },
  { header: 'Здание', render: (user) => user.building?.name ?? '—' },
];

export function UsersPage() {
  const currentUser = useCurrentUser();
  const { data: companyOptions } = useResourceOptions(companies);
  const { data: buildingOptions } = useResourceOptions(buildings);
  const [editing, setEditing] = useState<User | 'new' | null>(null);
  const [deleting, setDeleting] = useState<User | null>(null);
  const options = companyOptions && buildingOptions && { companyOptions, buildingOptions };

  return (
    <Stack spacing={2}>
      <PageHeader title="Пользователи" onAdd={() => setEditing('new')} addDisabled={!options} />
      <DataTable
        resource={users}
        columns={columns}
        actions={(user) => (
          <RowActions
            onEdit={() => setEditing(user)}
            onDelete={() => setDeleting(user)}
            deleteDisabled={user.uuid === currentUser.uuid}
          />
        )}
      />
      {editing && options && (
        <UserFormDialog
          user={editing === 'new' ? undefined : editing}
          {...options}
          onClose={() => setEditing(null)}
        />
      )}
      {deleting && (
        <ConfirmDialog
          title="Удалить пользователя?"
          text={`Пользователь «${deleting.name}» будет удалён.`}
          action={() => users.remove(deleting.uuid)}
          onClose={() => setDeleting(null)}
        />
      )}
    </Stack>
  );
}
