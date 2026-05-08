import api from './index';
import type { BotGroup, PaginatedResponse } from '../types';

export const groupsApi = {
  getList: async (params: {
    page?: number;
    page_size?: number;
    keyword?: string;
    is_active?: boolean;
  }): Promise<PaginatedResponse<BotGroup>> => {
    const response = await api.get<PaginatedResponse<BotGroup>>('/groups', { params });
    return response.data;
  },
  
  getById: async (id: number): Promise<BotGroup> => {
    const response = await api.get<BotGroup>(`/groups/${id}`);
    return response.data;
  },
  
  create: async (data: Partial<BotGroup>): Promise<BotGroup> => {
    const response = await api.post<BotGroup>('/groups', data);
    return response.data;
  },
  
  update: async (id: number, data: Partial<BotGroup>): Promise<BotGroup> => {
    const response = await api.put<BotGroup>(`/groups/${id}`, data);
    return response.data;
  },
  
  delete: async (id: number): Promise<void> => {
    await api.delete(`/groups/${id}`);
  },
  
  updateWelcome: async (id: number, data: { welcome_enabled: boolean; welcome_message: string }): Promise<BotGroup> => {
    const response = await api.put<BotGroup>(`/groups/${id}/welcome`, data);
    return response.data;
  },
  
  updateAI: async (id: number, data: { ai_enabled: boolean; ai_sleep_start?: string; ai_sleep_end?: string }): Promise<BotGroup> => {
    const response = await api.put<BotGroup>(`/groups/${id}/ai`, data);
    return response.data;
  },
};
