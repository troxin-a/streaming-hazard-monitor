import LogoutIcon from '@mui/icons-material/Logout';
import MenuIcon from '@mui/icons-material/Menu';
import PasswordIcon from '@mui/icons-material/Password';
import AppBar from '@mui/material/AppBar';
import Box from '@mui/material/Box';
import Chip from '@mui/material/Chip';
import Drawer from '@mui/material/Drawer';
import IconButton from '@mui/material/IconButton';
import List from '@mui/material/List';
import ListItemButton from '@mui/material/ListItemButton';
import ListItemIcon from '@mui/material/ListItemIcon';
import ListItemText from '@mui/material/ListItemText';
import Toolbar from '@mui/material/Toolbar';
import Tooltip from '@mui/material/Tooltip';
import Typography from '@mui/material/Typography';
import { useState } from 'react';
import { NavLink, Outlet } from 'react-router';

import { ACCESS_LEVEL_LABELS, getAccessLevel, hasAccess } from '@/features/auth/access';
import { ChangePasswordDialog } from '@/features/auth/ChangePasswordDialog';
import { logout, useCurrentUser } from '@/features/auth/hooks';
import { APP_NAME } from '@/shared/config';

import { sections } from './sections';

const DRAWER_WIDTH = 240;

interface NavigationProps {
  onNavigate: () => void;
}

function Navigation({ onNavigate }: NavigationProps) {
  const user = useCurrentUser();
  const visibleSections = sections.filter((section) => hasAccess(user, section.allowed));

  return (
    <Box component="nav" aria-label="Разделы">
      <Toolbar />
      <List>
        {visibleSections.map((section) => (
          <ListItemButton
            key={section.path}
            component={NavLink}
            to={section.path}
            end={section.path === '/'}
            onClick={onNavigate}
            sx={{ '&.active': { bgcolor: 'action.selected' } }}
          >
            <ListItemIcon>{section.icon}</ListItemIcon>
            <ListItemText primary={section.label} />
          </ListItemButton>
        ))}
      </List>
    </Box>
  );
}

/** Каркас приложения: шапка, боковое меню и область страницы. */
export function AppLayout() {
  const user = useCurrentUser();
  const [mobileOpen, setMobileOpen] = useState(false);
  const [passwordOpen, setPasswordOpen] = useState(false);
  const closeMobile = () => setMobileOpen(false);

  return (
    <Box sx={{ display: 'flex' }}>
      <AppBar position="fixed" sx={{ zIndex: (theme) => theme.zIndex.drawer + 1 }}>
        <Toolbar sx={{ gap: 1 }}>
          <IconButton
            color="inherit"
            edge="start"
            aria-label="Открыть меню"
            onClick={() => setMobileOpen(true)}
            sx={{ display: { md: 'none' } }}
          >
            <MenuIcon />
          </IconButton>
          <Typography variant="h6" component="div" noWrap sx={{ flexGrow: 1 }}>
            {APP_NAME}
          </Typography>
          <Typography noWrap sx={{ display: { xs: 'none', sm: 'block' } }}>
            {user.name}
          </Typography>
          <Chip
            label={ACCESS_LEVEL_LABELS[getAccessLevel(user)]}
            size="small"
            variant="outlined"
            sx={{ color: 'inherit', borderColor: 'currentColor' }}
          />
          <Tooltip title="Сменить пароль">
            <IconButton
              color="inherit"
              aria-label="Сменить пароль"
              onClick={() => setPasswordOpen(true)}
            >
              <PasswordIcon />
            </IconButton>
          </Tooltip>
          <Tooltip title="Выйти">
            <IconButton color="inherit" edge="end" aria-label="Выйти" onClick={logout}>
              <LogoutIcon />
            </IconButton>
          </Tooltip>
        </Toolbar>
      </AppBar>
      {passwordOpen && <ChangePasswordDialog onClose={() => setPasswordOpen(false)} />}

      <Drawer
        variant="temporary"
        open={mobileOpen}
        onClose={closeMobile}
        sx={{ display: { xs: 'block', md: 'none' }, '& .MuiDrawer-paper': { width: DRAWER_WIDTH } }}
      >
        <Navigation onNavigate={closeMobile} />
      </Drawer>
      <Drawer
        variant="permanent"
        sx={{
          display: { xs: 'none', md: 'block' },
          width: DRAWER_WIDTH,
          flexShrink: 0,
          '& .MuiDrawer-paper': { width: DRAWER_WIDTH },
        }}
      >
        <Navigation onNavigate={closeMobile} />
      </Drawer>

      <Box component="main" sx={{ flexGrow: 1, minWidth: 0, p: 3 }}>
        <Toolbar />
        <Outlet />
      </Box>
    </Box>
  );
}
