import Alert from '@mui/material/Alert';
import Button from '@mui/material/Button';
import CircularProgress from '@mui/material/CircularProgress';
import Stack from '@mui/material/Stack';
import { Navigate, Outlet, useLocation } from 'react-router';

import { getErrorMessage } from '@/shared/api/client';

import { useCurrentUserQuery, useIsAuthenticated, useLogout } from './hooks';

/** Пускает дальше только вошедшего пользователя, остальных отправляет на страницу входа. */
export function RequireAuth() {
  const location = useLocation();
  const isAuthenticated = useIsAuthenticated();
  const { isPending, isError, error, refetch } = useCurrentUserQuery();
  const logout = useLogout();

  if (!isAuthenticated) {
    return <Navigate to="/login" replace state={{ from: location.pathname }} />;
  }

  if (isPending) {
    return (
      <Stack sx={{ minHeight: '100vh', alignItems: 'center', justifyContent: 'center' }}>
        <CircularProgress aria-label="Загрузка" />
      </Stack>
    );
  }

  if (isError) {
    return (
      <Stack
        spacing={2}
        sx={{ minHeight: '100vh', alignItems: 'center', justifyContent: 'center', p: 2 }}
      >
        <Alert severity="error">{getErrorMessage(error)}</Alert>
        <Stack direction="row" spacing={1}>
          <Button variant="contained" onClick={() => refetch()}>
            Повторить
          </Button>
          <Button onClick={logout}>Выйти</Button>
        </Stack>
      </Stack>
    );
  }

  return <Outlet />;
}
