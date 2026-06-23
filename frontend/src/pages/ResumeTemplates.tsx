import { useState } from 'react'
import { useTemplates, useUploadTemplate } from '@/api/templates'
import { Card, Badge, FileUpload, Spinner, Button } from '@/components/ui'
import { useAppStore } from '@/stores/app'

const ROLES = [
  { value: 'business_analyst', label: 'Business Analyst' },
  { value: 'business_intelligence_analyst', label: 'Business Intelligence Analyst' },
  { value: 'project_manager', label: 'Project Manager' },
  { value: 'product_owner', label: 'Product Owner' },
]

export function ResumeTemplates() {
  const projectId = useAppStore((s) => s.selectedProjectId)
  const { data: templates, isLoading } = useTemplates(projectId ?? '')
  const uploadTemplate = useUploadTemplate()
  const uploadVars = uploadTemplate.variables
  const [previewRole, setPreviewRole] = useState<string | null>(null)

  const getTemplate = (role: string) =>
    templates?.find((t) => t.role === role)

  const handleUpload = (role: string, file: File) => {
    if (!projectId) return
    uploadTemplate.mutate({ projectId, role, file })
  }

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

  return (
    <div>
      <h2 className="mb-6 text-2xl font-bold text-gray-900">Resume Templates</h2>
      <p className="mb-6 text-gray-600">
        Upload a LaTeX (.tex) resume template for each role.
      </p>

      <div className="grid gap-6 md:grid-cols-2">
        {ROLES.map((role) => {
          const template = getTemplate(role.value)
          const showPreview = previewRole === role.value
          return (
            <Card key={role.value}>
              <Card.Header className="flex items-center justify-between">
                <h3 className="font-semibold text-gray-900">{role.label}</h3>
                {template && <Badge variant="success">Uploaded</Badge>}
              </Card.Header>
              <Card.Body>
                {template ? (
                  <div className="space-y-3">
                    <p className="text-sm text-gray-600">
                      File: {template.filename}
                    </p>
                    <Button
                      variant="secondary"
                      size="sm"
                      onClick={() => setPreviewRole(showPreview ? null : role.value)}
                    >
                      {showPreview ? 'Hide Preview' : 'Show Preview'}
                    </Button>
                    {showPreview && (
                      <iframe
                        src={`/api/templates/${template.id}/preview`}
                        className="h-96 w-full rounded-md border"
                        title="Template Preview"
                      />
                    )}
                    <FileUpload
                      accept=".tex"
                      onFile={(file) => handleUpload(role.value, file)}
                      loading={uploadTemplate.isPending}
                    />
                    <p className="text-xs text-gray-400">
                      Upload a new file to replace the current template.
                    </p>
                  </div>
                ) : (
                  <FileUpload
                    accept=".tex"
                    onFile={(file) => handleUpload(role.value, file)}
                    loading={uploadTemplate.isPending &&
                      uploadVars?.role === role.value}
                  />
                )}
              </Card.Body>
            </Card>
          )
        })}
      </div>
    </div>
  )
}
