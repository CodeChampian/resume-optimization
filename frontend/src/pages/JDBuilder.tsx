import { useState } from 'react'
import { useJDs, useAddJD, useBulkAddJDs, useDeleteJD } from '@/api/jds'
import { useStartOptimization, useGeneratedResumes } from '@/api/optimize'
import { Card, Button, Badge, Spinner, Modal } from '@/components/ui'
import { useAppStore } from '@/stores/app'

const ROLES = [
  { value: 'business_analyst', label: 'Business Analyst' },
  { value: 'business_intelligence_analyst', label: 'Business Intelligence Analyst' },
  { value: 'project_manager', label: 'Project Manager' },
  { value: 'product_owner', label: 'Product Owner' },
]

export function JDBuilder() {
  const projectId = useAppStore((s) => s.selectedProjectId)
  const { data: jds, isLoading } = useJDs(projectId ?? '')
  const addJD = useAddJD()
  const bulkAddJDs = useBulkAddJDs()
  const deleteJD = useDeleteJD()
  const startOptimization = useStartOptimization()
  const { data: generated } = useGeneratedResumes(projectId ?? '')

  const [newJDCompany, setNewJDCompany] = useState<Record<string, string>>({})
  const [newJDContent, setNewJDContent] = useState<Record<string, string>>({})
  const [bulkText, setBulkText] = useState<Record<string, string>>({})
  const [bulkModal, setBulkModal] = useState<string | null>(null)

  if (!projectId) {
    return (
      <div className="flex items-center justify-center py-20">
        <p className="text-gray-500">Select a project first from the Dashboard.</p>
      </div>
    )
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-20">
        <Spinner className="h-8 w-8 text-blue-600" />
      </div>
    )
  }

  const jdsByRole = new Map<string, NonNullable<typeof jds>>()
  if (jds) {
    for (const jd of jds) {
      const list = jdsByRole.get(jd.role) || []
      list.push(jd)
      jdsByRole.set(jd.role, list)
    }
  }

  const handleAddJD = (role: string) => {
    const company = newJDCompany[role]?.trim()
    const content = newJDContent[role]?.trim()
    if (!company || !content) return
    addJD.mutate(
      { project_id: projectId, role, company_name: company, content },
      {
        onSuccess: () => {
          setNewJDCompany((prev) => ({ ...prev, [role]: '' }))
          setNewJDContent((prev) => ({ ...prev, [role]: '' }))
        },
      },
    )
  }

  const handleBulkAdd = (role: string) => {
    const text = bulkText[role]?.trim()
    if (!text) return
    const items = text
      .split('\n')
      .filter((l: string) => l.trim())
      .map((line: string) => {
        const sepIdx = line.indexOf('|')
        if (sepIdx !== -1) {
          return {
            company_name: line.slice(0, sepIdx).trim(),
            content: line.slice(sepIdx + 1).trim(),
          }
        }
        return { company_name: 'Unknown', content: line.trim() }
      })
      .filter((item: { company_name: string; content: string }) => item.content)
    if (items.length === 0) return
    bulkAddJDs.mutate(
      { project_id: projectId, role, items },
      { onSuccess: () => { setBulkText((prev) => ({ ...prev, [role]: '' })); setBulkModal(null) } },
    )
  }

  const generatedCount = generated?.length ?? 0

  return (
    <div>
      <div className="mb-6 flex items-center justify-between">
        <h2 className="text-2xl font-bold text-gray-900">JD Builder</h2>
        <div className="flex items-center gap-3">
          <span className="text-sm text-gray-500">
            {generatedCount > 0 ? `${generatedCount} resumes generated` : ''}
          </span>
          <Button
            onClick={() => startOptimization.mutate(projectId)}
            loading={startOptimization.isPending}
          >
            Generate Resumes
          </Button>
        </div>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        {ROLES.map((role) => {
          const roleJDs = jdsByRole.get(role.value) || []
          return (
            <Card key={role.value}>
              <Card.Header className="flex items-center justify-between">
                <h3 className="font-semibold text-gray-900">{role.label}</h3>
                <Badge>{roleJDs.length} JDs</Badge>
              </Card.Header>
              <Card.Body className="space-y-4">
                {roleJDs.map((jd) => (
                  <div key={jd.id} className="rounded-md border bg-gray-50 p-3">
                    <div className="flex items-start justify-between gap-2">
                      <div className="min-w-0 flex-1">
                        <p className="text-sm font-medium text-gray-900">{jd.company_name}</p>
                        <p className="mt-1 text-xs text-gray-500 line-clamp-2">{jd.content}</p>
                      </div>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => deleteJD.mutate(jd.id)}
                        loading={deleteJD.isPending}
                        className="shrink-0 text-red-500 hover:text-red-700"
                      >
                        Del
                      </Button>
                    </div>
                  </div>
                ))}

                <input
                  value={newJDCompany[role.value] || ''}
                  onChange={(e) =>
                    setNewJDCompany((prev) => ({ ...prev, [role.value]: e.target.value }))
                  }
                  placeholder="Company name..."
                  className="w-full rounded-md border px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
                <textarea
                  value={newJDContent[role.value] || ''}
                  onChange={(e) =>
                    setNewJDContent((prev) => ({ ...prev, [role.value]: e.target.value }))
                  }
                  placeholder="Paste job description content here..."
                  rows={4}
                  className="w-full rounded-md border px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                />

                <div className="flex gap-2">
                  <Button
                    variant="secondary"
                    size="sm"
                    onClick={() => handleAddJD(role.value)}
                    loading={addJD.isPending}
                  >
                    + Add JD
                  </Button>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => setBulkModal(role.value)}
                  >
                    Bulk Add
                  </Button>
                </div>
              </Card.Body>
            </Card>
          )
        })}
      </div>

      <Modal
        open={!!bulkModal}
        onClose={() => setBulkModal(null)}
        title="Bulk Add JDs"
      >
        <div className="space-y-4">
          <p className="text-sm text-gray-600">
            One JD per line. Format: <code className="rounded bg-gray-100 px-1">Company Name | JD description</code>
          </p>
          <textarea
            value={bulkText[bulkModal || ''] || ''}
            onChange={(e) =>
              setBulkText((prev) => ({ ...prev, [bulkModal || '']: e.target.value }))
            }
            placeholder="Google | Senior software engineer with 5+ years..."
            rows={8}
            className="w-full rounded-md border px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <Button
            className="w-full"
            onClick={() => bulkModal && handleBulkAdd(bulkModal)}
            loading={bulkAddJDs.isPending}
          >
            Add All
          </Button>
        </div>
      </Modal>
    </div>
  )
}
