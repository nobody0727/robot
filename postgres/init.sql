-- WeChat Bot Admin System - PostgreSQL Initialization Script
-- Requires: PostgreSQL 15+ with pgvector extension

-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Create admin_users table (后台管理员表)
CREATE TABLE IF NOT EXISTS admin_users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL DEFAULT 'operator',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    
    CONSTRAINT role_check CHECK (role IN ('operator', 'admin', 'super_admin'))
);

CREATE INDEX IF NOT EXISTS idx_admin_username ON admin_users(username);
CREATE INDEX IF NOT EXISTS idx_admin_role ON admin_users(role);

-- Create whitelist_users table (白名单用户表)
CREATE TABLE IF NOT EXISTS whitelist_users (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(100) UNIQUE NOT NULL,
    user_name VARCHAR(255),
    added_by INTEGER REFERENCES admin_users(id),
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expire_at TIMESTAMP,
    remark TEXT,
    is_active BOOLEAN DEFAULT TRUE
);

CREATE INDEX IF NOT EXISTS idx_whitelist_user_id ON whitelist_users(user_id);
CREATE INDEX IF NOT EXISTS idx_whitelist_active ON whitelist_users(is_active);
CREATE INDEX IF NOT EXISTS idx_whitelist_expire ON whitelist_users(expire_at);

-- Create bot_groups table (机器人群组表)
CREATE TABLE IF NOT EXISTS bot_groups (
    id SERIAL PRIMARY KEY,
    room_id VARCHAR(100) UNIQUE NOT NULL,
    room_name VARCHAR(255),
    owner_id VARCHAR(100),
    owner_name VARCHAR(255),
    invited_by INTEGER REFERENCES admin_users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    welcome_enabled BOOLEAN DEFAULT TRUE,
    welcome_message TEXT DEFAULT '欢迎 {name} 加入群聊！',
    ai_enabled BOOLEAN DEFAULT TRUE,
    ai_sleep_start TIME DEFAULT '23:00',
    ai_sleep_end TIME DEFAULT '07:00',
    last_active TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_bot_groups_room_id ON bot_groups(room_id);
CREATE INDEX IF NOT EXISTS idx_bot_groups_active ON bot_groups(is_active);

-- Create group_messages table (群消息表)
CREATE TABLE IF NOT EXISTS group_messages (
    id SERIAL PRIMARY KEY,
    group_id INTEGER REFERENCES bot_groups(id) ON DELETE CASCADE,
    sender_id VARCHAR(100) NOT NULL,
    sender_name VARCHAR(255),
    content TEXT NOT NULL,
    content_vector VECTOR(1536),
    msg_type VARCHAR(50) DEFAULT 'text',
    is_recalled BOOLEAN DEFAULT FALSE,
    raw_msg_id VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    extra_data JSONB
);

CREATE INDEX IF NOT EXISTS idx_messages_vector ON group_messages USING hnsw (content_vector vector_cosine_ops);
CREATE INDEX IF NOT EXISTS idx_messages_group_time ON group_messages(group_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_messages_sender ON group_messages(sender_id);
CREATE INDEX IF NOT EXISTS idx_messages_recalled ON group_messages(is_recalled);
CREATE INDEX IF NOT EXISTS idx_messages_created ON group_messages(created_at);

-- Create system_config table (系统配置表)
CREATE TABLE IF NOT EXISTS system_config (
    id SERIAL PRIMARY KEY,
    key VARCHAR(100) UNIQUE NOT NULL,
    value JSONB NOT NULL,
    description TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_by INTEGER REFERENCES admin_users(id)
);

-- Insert default system configs
INSERT INTO system_config (key, value, description) VALUES
('whitelist', '{"enable_whitelist": true, "welcome_msg": "欢迎使用微信机器人！", "reject_msg": "您暂无权限使用此功能，请联系管理员添加白名单。"}', '白名单配置'),
('ai', '{"model": "deepseek-chat", "temperature": 0.7, "max_tokens": 2000}', 'AI模型配置'),
('bot', '{"name": "微信助手", "sleep_enabled": true, "sleep_start": "23:00", "sleep_end": "07:00"}', '机器人基础配置')
ON CONFLICT (key) DO NOTHING;

-- Create cleanup function for old messages (7 days retention)
CREATE OR REPLACE FUNCTION cleanup_old_messages()
RETURNS void AS $$
BEGIN
    DELETE FROM group_messages 
    WHERE created_at < NOW() - INTERVAL '7 days';
END;
$$ LANGUAGE plpgsql;

-- Create trigger for automatic cleanup on message insert
CREATE OR REPLACE FUNCTION auto_cleanup_messages()
RETURNS TRIGGER AS $$
BEGIN
    -- Run cleanup every 1000 inserts to reduce overhead
    IF (SELECT COUNT(*) FROM group_messages) % 1000 = 0 THEN
        PERFORM cleanup_old_messages();
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_auto_cleanup_messages
AFTER INSERT ON group_messages
FOR EACH STATEMENT
EXECUTE FUNCTION auto_cleanup_messages();

-- Create updated_at trigger for system_config
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_system_config_updated_at
BEFORE UPDATE ON system_config
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

-- Insert default admin user (password: admin123)
-- BCrypt hash for 'admin123': $2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYqH5zLO1W2
INSERT INTO admin_users (username, password_hash, role, is_active) VALUES
('admin', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYqH5zLO1W2', 'super_admin', true),
('operator', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYqH5zLO1W2', 'operator', true)
ON CONFLICT (username) DO NOTHING;

-- Grant permissions
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO bot_admin;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO bot_admin;

-- Verify pgvector installation
SELECT * FROM pg_extension WHERE extname = 'vector';
