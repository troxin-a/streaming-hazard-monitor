import PasswordIcon from '@mui/icons-material/Password';
import IconButton from '@mui/material/IconButton';
import Stack from '@mui/material/Stack';
import Tooltip from '@mui/material/Tooltip';
import { useState } from 'react';

import { type User, users } from '@/entities/user';
import { ACCESS_LEVEL_LABELS, getAccessLevel } from '@/features/auth/access';
import { useCurrentUser } from '@/features/auth/hooks';
import { PasswordDialog } from '@/features/users/PasswordDialog';
import { UserFormDialog } from '@/features/users/UserFormDialog';
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
  const [editing, setEditing] = useState<User | 'new' | null>(null);
  const [deleting, setDeleting] = useState<User | null>(null);
  const [changingPassword, setChangingPassword] = useState<User | null>(null);

  return (
    <Stack spacing={2}>
      <PageHeader title="Пользователи" onAdd={() => setEditing('new')} />
      <DataTable
        resource={users}
        columns={columns}
        searchLabel="Поиск по имени или логину"
        actions={(user) => (
          <RowActions
            onEdit={() => setEditing(user)}
            onDelete={() => setDeleting(user)}
            deleteDisabled={user.uuid === currentUser.uuid}
          >
            {/* Свой пароль меняется через шапку, с проверкой текущего. */}
            {user.uuid !== currentUser.uuid && (
              <Tooltip title="Сменить пароль">
                <IconButton
                  size="small"
                  aria-label="Сменить пароль"
                  onClick={() => setChangingPassword(user)}
                >
                  <PasswordIcon fontSize="small" />
                </IconButton>
              </Tooltip>
            )}
          </RowActions>
        )}
      />
      {changingPassword && (
        <PasswordDialog user={changingPassword} onClose={() => setChangingPassword(null)} />
      )}
      {editing && (
        <UserFormDialog
          user={editing === 'new' ? undefined : editing}
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
