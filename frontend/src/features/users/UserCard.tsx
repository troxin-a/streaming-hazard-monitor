import DeleteIcon from '@mui/icons-material/Delete';
import EditIcon from '@mui/icons-material/Edit';
import PasswordIcon from '@mui/icons-material/Password';
import Button from '@mui/material/Button';
import { useState } from 'react';

import { type User, users } from '@/entities/user';
import { useCurrentUser } from '@/features/auth/hooks';
import { ConfirmDialog } from '@/shared/ui/ConfirmDialog';
import type { Column } from '@/shared/ui/DataTable';
import { RecordCard } from '@/shared/ui/RecordCard';

import { PasswordDialog } from './PasswordDialog';
import { UserFormDialog } from './UserFormDialog';

type CardView = 'edit' | 'password';

interface UserCardProps {
  user: User;
  columns: Column<User>[];
  onClose: () => void;
}

/** Карточка пользователя с действиями над ним. */
export function UserCard({ user, columns, onClose }: UserCardProps) {
  const isCurrentUser = user.uuid === useCurrentUser().uuid;
  const [view, setView] = useState<CardView | null>(null);
  const [deleting, setDeleting] = useState(false);
  const showCard = () => setView(null);

  const views = {
    edit: <UserFormDialog user={user} onClose={showCard} />,
    password: <PasswordDialog user={user} onClose={showCard} />,
  };

  return (
    <>
      <RecordCard
        title={user.name}
        row={user}
        columns={columns}
        onClose={onClose}
        view={view && views[view]}
      >
        <Button variant="outlined" startIcon={<EditIcon />} onClick={() => setView('edit')}>
          Изменить
        </Button>
        {/* Свой пароль меняется через шапку, с проверкой текущего. */}
        {!isCurrentUser && (
          <Button
            variant="outlined"
            startIcon={<PasswordIcon />}
            onClick={() => setView('password')}
          >
            Сменить пароль
          </Button>
        )}
        <Button
          variant="outlined"
          color="error"
          startIcon={<DeleteIcon />}
          onClick={() => setDeleting(true)}
          disabled={isCurrentUser}
        >
          Удалить
        </Button>
      </RecordCard>
      {deleting && (
        <ConfirmDialog
          title="Удалить пользователя?"
          text={`Пользователь «${user.name}» будет удалён.`}
          action={() => users.remove(user.uuid)}
          successMessage="Пользователь удалён"
          onClose={() => setDeleting(false)}
        />
      )}
    </>
  );
}
