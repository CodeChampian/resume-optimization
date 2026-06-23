import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { api } from './client'
import type { JobDescription } from '@/types'

export function useJDs(projectId: string, role?: string) {
  const params = new URLSearchParams({ project_id: projectId })
  if (role) params.set('role', role)
  return useQuery({
    queryKey: ['jds', projectId, role],
    queryFn: () => api.get<JobDescription[]>(`/jds?${params}`),
    enabled: !!projectId,
  })
}

export function useAddJD() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (data: {
      project_id: string
      role: string
      company_name: string
      content: string
    }) => api.post<JobDescription>('/jds', data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['jds'] })
    },
  })
}

export function useBulkAddJDs() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (data: {
      project_id: string
      role: string
      items: Array<{ company_name: string; content: string }>
    }) => api.post<{ created: number }>('/jds/bulk', data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['jds'] })
    },
  })
}

export function useDeleteJD() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (jdId: string) => api.delete(`/jds/${jdId}`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['jds'] })
    },
  })
}
