import { createBrowserRouter, Navigate } from 'react-router-dom'
import { AppLayout } from '@/components/layout/AppLayout'
import { Dashboard } from '@/pages/Dashboard'
import { CreateProject } from '@/pages/CreateProject'
import { ResumeTemplates } from '@/pages/ResumeTemplates'
import { JDBuilder } from '@/pages/JDBuilder'
import { GeneratedResumes } from '@/pages/GeneratedResumes'

export const router = createBrowserRouter([
  {
    element: <AppLayout />,
    children: [
      { path: '/', element: <Dashboard /> },
      { path: '/projects/new', element: <CreateProject /> },
      { path: '/templates', element: <ResumeTemplates /> },
      { path: '/jds', element: <JDBuilder /> },
      { path: '/generated', element: <GeneratedResumes /> },
      { path: '*', element: <Navigate to="/" replace /> },
    ],
  },
])
