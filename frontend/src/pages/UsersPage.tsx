import Stack from '@mui/material/Stack';
import { useState } from 'react';

import { type User, users } from '@/entities/user';
import { ACCESS_LEVEL_LABELS, getAccessLevel } from '@/features/auth/access';
import { UserCard } from '@/features/users/UserCard';
import { UserFormDialog } from '@/features/users/UserFormDialog';
import { type Column, DataTable } from '@/shared/ui/DataTable';
import { PageHeader } from '@/shared/ui/PageHeader';

const columns: Column<User>[] = [
  { header: 'Имя', render: (user) => user.name },
  { header: 'Логин', render: (user) => user.username },
  { header: 'Роль', render: (user) => ACCESS_LEVEL_LABELS[getAccessLevel(user)] },
  { header: 'Компания', render: (user) => user.company?.name ?? '—' },
  { header: 'Здание', render: (user) => user.building?.name ?? '—' },
];

export function UsersPage() {
  const [creating, setCreating] = useState(false);

  return (
    <Stack spacing={2}>
      <PageHeader title="Пользователи" onAdd={() => setCreating(true)} />
      <DataTable
        resource={users}
        columns={columns}
        searchLabel="Поиск по имени или логину"
        card={(user, onClose) => <UserCard user={user} columns={columns} onClose={onClose} />}
      />
      {creating && <UserFormDialog onClose={() => setCreating(false)} />}
    </Stack>
  );
}
