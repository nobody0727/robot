import api from './index';
import type { WhitelistUser, WhitelistUserCreate, WhitelistStats, PaginatedResponse } from '../types';

export const whitelistApi = {
  getList: async (params: {
    page?: number;
    page_size?: number;
    keyword?: string;
    is_active?: boolean;
    expire_soon?: boolean;
  }): Promise<PaginatedResponse<WhitelistUser>> => {
    const response = await api.get<PaginatedResponse<WhitelistUser>>('/whitelist', { params });
    return response.data;
  },
  
  create: async (data: WhitelistUserCreate): Promise<WhitelistUser> => {
    const response = await api.post<WhitelistUser>('/whitelist', data);
    return response.data;
  },
  
  update: async (id: number, data: Partial<WhitelistUserCreate>): Promise<WhitelistUser> => {
    const response = await api.put<WhitelistUser>(`/whitelist/${id}`, data);
    return response.data;
  },
  
  delete: async (id: number): Promise<void> => {
    await api.delete(`/whitelist/${id}`);
  },
  
  getStats: async (): Promise<WhitelistStats> => {
    const response = await api.get<WhitelistStats>('/whitelist/stats');
    return response.data;
  },
  
  import: async (users: WhitelistUserCreate[], overrideExisting: boolean = false): Promise<{
    message: string;
    imported: number;
    skipped: number;
    errors: any[];
  }> => {
    const response = await api.post('/whitelist/import', {
      users,
      override_existing: overrideExisting,
    });
    return response.data;
  },
  
  export: async (): Promise<{ total: number; items: WhitelistUser[] }> => {
    const response = await api.get('/whitelist/export');
    return response.data;
  },
  
  check: async (userId: string): Promise<{ user_id: string; is_whitelisted: boolean }> => {
    const response = await api.post('/whitelist/check', { user_id: userId });
    return response.data;
  },
};
