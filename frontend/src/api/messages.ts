import api from './index';
import type { GroupMessage, PaginatedResponse } from '../types';

export const messagesApi = {
  getList: async (params: {
    page?: number;
    page_size?: number;
    group_id?: number;
    sender_id?: string;
    keyword?: string;
    msg_type?: string;
    start_date?: string;
    end_date?: string;
  }): Promise<PaginatedResponse<GroupMessage>> => {
    const response = await api.get<PaginatedResponse<GroupMessage>>('/messages', { params });
    return response.data;
  },
  
  getById: async (id: number): Promise<GroupMessage> => {
    const response = await api.get<GroupMessage>(`/messages/${id}`);
    return response.data;
  },
  
  getStats: async (params?: { group_id?: number; days?: number }): Promise<{
    total_messages: number;
    total_text_messages: number;
    total_recalls: number;
    unique_senders: number;
    messages_by_day: Array<{date: string; count: number}>;
    top_senders: Array<{sender_id: string; sender_name: string; count: number}>;
  }> => {
    const response = await api.get('/messages/stats/overview', { params });
    return response.data;
  },
};
