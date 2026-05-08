import api from './index';
import type { SemanticSearchResponse, SearchResult } from '../types';

export const searchApi = {
  semantic: async (data: {
    query: string;
    group_id?: number;
    top_k?: number;
    include_context?: boolean;
  }): Promise<SemanticSearchResponse> => {
    const response = await api.post<SemanticSearchResponse>('/search/semantic', data);
    return response.data;
  },
  
  keyword: async (data: {
    keyword: string;
    group_id?: number;
    page?: number;
    page_size?: number;
  }): Promise<{
    keyword: string;
    results: SearchResult[];
    total: number;
    page: number;
    page_size: number;
  }> => {
    const response = await api.post('/search/keyword', data);
    return response.data;
  },
};
