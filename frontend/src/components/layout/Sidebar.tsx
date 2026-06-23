import { NavLink } from 'react-router-dom'
import { cn } from '@/lib/utils'

const links = [
  { to: '/', label: 'Dashboard' },
  { to: '/templates', label: 'Resume Templates' },
  { to: '/jds', label: 'JD Builder' },
  { to: '/generated', label: 'Generated Resumes' },
]

export function Sidebar() {
  return (
    <aside className="flex h-full w-64 flex-col border-r bg-gray-50">
      <div className="border-b px-6 py-5">
        <h1 className="text-lg font-bold text-gray-900">Resume Optimizer</h1>
      </div>
      <nav className="flex-1 space-y-1 p-4">
        {links.map((link) => (
          <NavLink
            key={link.to}
            to={link.to}
            className={({ isActive }) =>
              cn(
                'block rounded-md px-3 py-2 text-sm font-medium transition-colors',
                isActive
                  ? 'bg-blue-100 text-blue-700'
                  : 'text-gray-600 hover:bg-gray-100 hover:text-gray-900',
              )
            }
          >
            {link.label}
          </NavLink>
        ))}
      </nav>
    </aside>
  )
}
