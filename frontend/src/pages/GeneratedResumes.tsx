import { useGeneratedResumes, getDownloadUrl } from '@/api/optimize'
import { Card, Button, Badge, Skeleton } from '@/components/ui'
import { useAppStore } from '@/stores/app'

const ROLE_LABELS: Record<string, string> = {
  business_analyst: 'Business Analyst',
  business_intelligence_analyst: 'Business Intelligence Analyst',
  project_manager: 'Project Manager',
  product_owner: 'Product Owner',
}

export function GeneratedResumes() {
  const projectId = useAppStore((s: { selectedProjectId: string | null }) => s.selectedProjectId)
  const { data: resumes, isLoading } = useGeneratedResumes(projectId ?? '')

  if (!projectId) {
    return (
      <div className="flex items-center justify-center py-20">
        <p className="text-gray-500">Select a project first from the Dashboard.</p>
      </div>
    )
  }

  if (isLoading) {
    return (
      <div>
        <h2 className="mb-6 text-2xl font-bold text-gray-900">Generated Resumes</h2>
        <div className="space-y-3">
          {Array.from({ length: 4 }).map((_, i) => (
            <Skeleton key={i} className="h-16 w-full" />
          ))}
        </div>
      </div>
    )
  }

  if (!resumes || resumes.length === 0) {
    return (
      <div>
        <h2 className="mb-6 text-2xl font-bold text-gray-900">Generated Resumes</h2>
        <Card>
          <Card.Body className="py-12 text-center">
            <p className="text-gray-500">
              No generated resumes yet. Go to JD Builder and click "Generate Resumes".
            </p>
          </Card.Body>
        </Card>
      </div>
    )
  }

  return (
    <div>
      <div className="mb-6 flex items-center justify-between">
        <h2 className="text-2xl font-bold text-gray-900">Generated Resumes</h2>
        <Badge variant="success">{resumes.length} resumes</Badge>
      </div>

      <div className="overflow-hidden rounded-lg border">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">
                Role
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">
                JD
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">
                ATS Score
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">
                Generated
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">
                PDF
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200 bg-white">
            {resumes.map((resume) => (
              <tr key={resume.id} className="hover:bg-gray-50">
                <td className="whitespace-nowrap px-6 py-4 text-sm font-medium text-gray-900">
                  {ROLE_LABELS[resume.role] || resume.role}
                </td>
                <td className="px-6 py-4 text-sm text-gray-500">
                  {resume.jd_title}
                </td>
                <td className="whitespace-nowrap px-6 py-4 text-sm">
                  {resume.ats_before != null && resume.ats_after != null ? (
                    <span>
                      <span className="text-gray-500">{resume.ats_before}</span>
                      <span className="mx-1 text-gray-300">→</span>
                      <span className="font-medium text-green-600">{resume.ats_after}</span>
                    </span>
                  ) : (
                    <span className="text-gray-400">—</span>
                  )}
                </td>
                <td className="whitespace-nowrap px-6 py-4 text-sm text-gray-500">
                  {new Date(resume.created_at).toLocaleDateString("en-IN", {
                    day: "numeric",
                    month: "short",
                    year: "numeric",
                    hour: "2-digit",
                    minute: "2-digit",
                    hour12: true,
                    timeZone: "Asia/Kolkata",
                  })}
                </td>
                <td className="whitespace-nowrap px-6 py-4 text-sm">
                  {resume.pdf_path ? (
                    <Button
                      variant="secondary"
                      size="sm"
                      onClick={() => window.open(getDownloadUrl(resume.id), '_blank')}
                    >
                      Download
                    </Button>
                  ) : (
                    <span className="text-gray-400">Pending</span>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
