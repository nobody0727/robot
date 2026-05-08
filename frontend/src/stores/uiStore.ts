import { create } from 'zustand';

interface UIState {
  sidebarCollapsed: boolean;
  loading: boolean;
  setSidebarCollapsed: (collapsed: boolean) => void;
  setLoading: (loading: boolean) => void;
}

export const useUIStore = create<UIState>((set) => ({
  sidebarCollapsed: false,
  loading: false,
  
  setSidebarCollapsed: (collapsed: boolean) => {
    set({ sidebarCollapsed: collapsed });
  },
  
  setLoading: (loading: boolean) => {
    set({ loading: loading });
  },
}));
