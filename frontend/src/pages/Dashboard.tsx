import { useNavigate } from 'react-router-dom'
import { useProjects, useCreateProject } from '@/api/projects'
import { Card, Button, Spinner } from '@/components/ui'
import { useAppStore } from '@/stores/app'

export function Dashboard() {
  const navigate = useNavigate()
  const { data: projects, isLoading } = useProjects()
  const createProject = useCreateProject()
  const setSelectedProjectId = useAppStore((s) => s.setSelectedProjectId)

  const handleCreate = () => {
    const name = prompt('Enter project name:')
    if (name?.trim()) {
      createProject.mutate(name.trim(), {
        onSuccess: (project) => {
          setSelectedProjectId(project.id)
          if (projects && projects.length === 0) {
            navigate('/templates')
          }
        },
      })
    }
  }

  const handleSelect = (id: string) => {
    setSelectedProjectId(id)
    navigate('/templates')
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-20">
        <Spinner className="h-8 w-8 text-blue-600" />
      </div>
    )
  }

  return (
    <div>
      <div className="mb-6 flex items-center justify-between">
        <h2 className="text-2xl font-bold text-gray-900">Projects</h2>
        <Button onClick={handleCreate} loading={createProject.isPending}>
          + New Project
        </Button>
      </div>

      {!projects || projects.length === 0 ? (
        <Card className="text-center">
          <Card.Body className="py-12">
            <p className="text-gray-500">No projects yet. Create your first project to get started.</p>
          </Card.Body>
        </Card>
      ) : (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {projects.map((project) => (
            <div
              key={project.id}
              className="cursor-pointer transition-shadow hover:shadow-md"
              onClick={() => handleSelect(project.id)}
            >
            <Card>
              <Card.Body>
                <h3 className="font-semibold text-gray-900">{project.name}</h3>
                <p className="mt-1 text-sm text-gray-500">
                  {new Date(project.created_at).toLocaleDateString()}
                </p>
              </Card.Body>
            </Card>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
