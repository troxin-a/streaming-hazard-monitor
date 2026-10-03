import { createBrowserRouter } from 'react-router';

import { RequireAccess } from '@/features/auth/RequireAccess';
import { RequireAuth } from '@/features/auth/RequireAuth';
import { LoginPage } from '@/pages/LoginPage';
import { NotFoundPage } from '@/pages/NotFoundPage';

import { AppLayout } from './AppLayout';
import { sections } from './sections';

export const router = createBrowserRouter([
  { path: '/login', element: <LoginPage /> },
  {
    element: <RequireAuth />,
    children: [
      {
        element: <AppLayout />,
        children: [
          ...sections.map((section) => ({
            path: section.path,
            element: <RequireAccess allowed={section.allowed}>{section.element}</RequireAccess>,
          })),
          { path: '*', element: <NotFoundPage /> },
        ],
      },
    ],
  },
]);
