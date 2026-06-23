import { create } from 'zustand'

interface AppState {
  selectedProjectId: string | null
  setSelectedProjectId: (id: string | null) => void
}

export const useAppStore = create<AppState>((set) => ({
  selectedProjectId: null,
  setSelectedProjectId: (id) => set({ selectedProjectId: id }),
}))
