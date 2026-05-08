import api from './index';
import type { DashboardOverview } from '../types';

export const dashboardApi = {
  getOverview: async (): Promise<DashboardOverview> => {
    const response = await api.get<DashboardOverview>('/dashboard/overview');
    return response.data;
  },
  
  getGroupStats: async (groupId: number, days?: number): Promise<any> => {
    const response = await api.get(`/dashboard/group/${groupId}`, { params: { days } });
    return response.data;
  },
  
  getActivityTrend: async (days?: number): Promise<{
    activity: Array<{
      date: string;
      message_count: number;
      user_count: number;
      group_count: number;
    }>;
    days: number;
  }> => {
    const response = await api.get('/dashboard/activity', { params: { days } });
    return response.data;
  },
  
  getWhitelistStats: async (): Promise<{
    total: number;
    active: number;
    inactive: number;
    added_today: number;
    added_this_month: number;
    expire_soon: number;
    expired: number;
  }> => {
    const response = await api.get('/dashboard/whitelist');
    return response.data;
  },
};
