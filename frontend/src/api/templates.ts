import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { api } from './client'
import type { ResumeTemplate } from '@/types'

export function useTemplates(projectId: string) {
  return useQuery({
    queryKey: ['templates', projectId],
    queryFn: () =>
      api.get<ResumeTemplate[]>(`/templates?project_id=${projectId}`),
    enabled: !!projectId,
  })
}

export function useUploadTemplate() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({
      projectId,
      role,
      file,
    }: {
      projectId: string
      role: string
      file: File
    }) => {
      const formData = new FormData()
      formData.append('project_id', projectId)
      formData.append('role', role)
      formData.append('file', file)
      return api.upload<ResumeTemplate>('/templates/upload', formData)
    },
    onSuccess: (_data, variables) => {
      queryClient.invalidateQueries({
        queryKey: ['templates', variables.projectId],
      })
    },
  })
}
