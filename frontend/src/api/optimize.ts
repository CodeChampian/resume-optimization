import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { api } from './client'
import type { GeneratedResume } from '@/types'

export function useStartOptimization() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (projectId: string) =>
      api.post<{ message: string; project_id: string }>('/optimize', {
        project_id: projectId,
      }),
    onSuccess: (_data, projectId) => {
      queryClient.invalidateQueries({
        queryKey: ['optimize-status', projectId],
      })
      queryClient.invalidateQueries({
        queryKey: ['generated', projectId],
      })
    },
  })
}

export function useOptimizationStatus(projectId: string) {
  return useQuery({
    queryKey: ['optimize-status', projectId],
    queryFn: () =>
      api.get<{ status: string | null }>(`/optimize/${projectId}/status`),
    enabled: !!projectId,
    refetchInterval: (query) => {
      const status = query.state.data?.status
      if (status === 'processing') return 3000
      return false
    },
  })
}

export function useGeneratedResumes(projectId: string) {
  const { data: statusData } = useOptimizationStatus(projectId)
  const status = statusData?.status

  return useQuery({
    queryKey: ['generated', projectId],
    queryFn: () =>
      api.get<GeneratedResume[]>(`/generated?project_id=${projectId}`),
    enabled: !!projectId,
    refetchInterval: status === 'processing' ? 5000 : false,
  })
}

export function getDownloadUrl(generatedId: string) {
  return `/api/generated/${generatedId}/download`
}
