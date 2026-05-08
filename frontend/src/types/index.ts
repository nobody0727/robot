export interface User {
  id: number;
  username: string;
  role: 'operator' | 'admin' | 'super_admin';
  is_active: boolean;
}

export interface LoginRequest {
  username: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
  user: User;
}

export interface WhitelistUser {
  id: number;
  user_id: string;
  user_name: string | null;
  added_by: number | null;
  added_at: string;
  expire_at: string | null;
  remark: string | null;
  is_active: boolean;
  added_by_name: string | null;
}

export interface WhitelistUserCreate {
  user_id: string;
  user_name?: string;
  remark?: string;
  expire_at?: string;
}

export interface WhitelistStats {
  total: number;
  active: number;
  inactive: number;
  added_today: number;
  expire_soon: number;
}

export interface BotGroup {
  id: number;
  room_id: string;
  room_name: string | null;
  owner_id: string | null;
  owner_name: string | null;
  invited_by: number | null;
  created_at: string;
  is_active: boolean;
  welcome_enabled: boolean;
  welcome_message: string;
  ai_enabled: boolean;
  ai_sleep_start: string;
  ai_sleep_end: string;
  last_active: string | null;
  message_count?: number;
}

export interface GroupMessage {
  id: number;
  group_id: number;
  sender_id: string;
  sender_name: string | null;
  content: string;
  msg_type: string;
  is_recalled: boolean;
  raw_msg_id: string | null;
  created_at: string;
  extra_data: any;
  group_name: string | null;
}

export interface SystemConfig {
  key: string;
  value: any;
  description: string | null;
  updated_at: string | null;
  updated_by: number | null;
}

export interface DashboardOverview {
  total_groups: number;
  total_messages_7d: number;
  total_whitelist_users: number;
  active_users_7d: number;
  message_trend: Array<{date: string; count: number}>;
  top_groups: Array<{id: number; name: string; message_count: number}>;
}

export interface PaginatedResponse<T> {
  total: number;
  page: number;
  page_size: number;
  items: T[];
}

export interface SearchResult {
  id: number;
  content: string;
  sender_name: string | null;
  sender_id: string;
  group_id: number;
  group_name: string | null;
  created_at: string | null;
  similarity: number;
  semantic_score?: number;
  keyword_score?: number;
}

export interface SemanticSearchResponse {
  query: string;
  expanded_keywords: string[];
  synonyms: string[];
  results: SearchResult[];
  total: number;
  search_time_ms: number;
}
