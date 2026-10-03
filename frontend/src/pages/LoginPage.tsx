import Container from '@mui/material/Container';
import Paper from '@mui/material/Paper';
import Stack from '@mui/material/Stack';
import Typography from '@mui/material/Typography';
import { Navigate, useLocation } from 'react-router';

import { useIsAuthenticated } from '@/features/auth/hooks';
import { LoginForm } from '@/features/auth/LoginForm';
import { APP_NAME } from '@/shared/config';

interface LoginLocationState {
  from?: string;
}

export function LoginPage() {
  const location = useLocation();
  const isAuthenticated = useIsAuthenticated();

  if (isAuthenticated) {
    const state = location.state as LoginLocationState | null;
    return <Navigate to={state?.from ?? '/'} replace />;
  }

  return (
    <Container maxWidth="xs" sx={{ minHeight: '100vh', display: 'flex', alignItems: 'center' }}>
      <Paper variant="outlined" sx={{ p: 4, width: '100%' }}>
        <Stack spacing={3}>
          <Stack spacing={0.5}>
            <Typography variant="h5" component="h1">
              {APP_NAME}
            </Typography>
            <Typography color="text.secondary">Войдите, чтобы продолжить</Typography>
          </Stack>
          <LoginForm />
        </Stack>
      </Paper>
    </Container>
  );
}
