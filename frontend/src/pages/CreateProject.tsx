import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useCreateProject } from '@/api/projects'
import { Button, Input, Card } from '@/components/ui'
import { useAppStore } from '@/stores/app'

export function CreateProject() {
  const navigate = useNavigate()
  const [name, setName] = useState('')
  const createProject = useCreateProject()
  const setSelectedProjectId = useAppStore((s) => s.setSelectedProjectId)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!name.trim()) return

    createProject.mutate(name.trim(), {
      onSuccess: (project) => {
        setSelectedProjectId(project.id)
        navigate('/templates')
      },
    })
  }

  return (
    <div className="mx-auto max-w-md">
      <h2 className="mb-6 text-2xl font-bold text-gray-900">Create Project</h2>
      <Card>
        <Card.Body>
          <form onSubmit={handleSubmit} className="space-y-4">
            <Input
              label="Project Name"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="My Resume Project"
            />
            <Button type="submit" loading={createProject.isPending} className="w-full">
              Create
            </Button>
          </form>
        </Card.Body>
      </Card>
    </div>
  )
}
