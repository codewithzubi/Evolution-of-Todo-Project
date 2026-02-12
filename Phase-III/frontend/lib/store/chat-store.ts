import { create } from 'zustand'

interface ChatStore {
  isOpen: boolean
  isMinimized: boolean
  toggleOpen: () => void
  toggleMinimize: () => void
  open: () => void
  close: () => void
}

export const useChatStore = create<ChatStore>((set) => ({
  isOpen: false,
  isMinimized: false,
  toggleOpen: () => set((state) => ({ isOpen: !state.isOpen })),
  toggleMinimize: () => set((state) => ({ isMinimized: !state.isMinimized })),
  open: () => set({ isOpen: true, isMinimized: false }),
  close: () => set({ isOpen: false }),
}))
