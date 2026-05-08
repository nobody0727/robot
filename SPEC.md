# 微信机器人后台管理系统 - 技术架构文档

## 一、项目整体架构

### 1.1 系统架构图

```
┌─────────────────────────────────────────────────────────────────────┐
│                           用户层                                     │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────────┐   │
│  │  微信用户    │  │  微信用户    │  │       后台管理员            │   │
│  │  (私聊/群聊) │  │  (入群邀请)  │  │  (Web管理界面)              │   │
│  └──────┬──────┘  └──────┬──────┘  └─────────────┬───────────────┘   │
└─────────┼────────────────┼──────────────────────┼───────────────────┘
          │                │                      │
          ▼                ▼                      ▼
┌─────────────────────────────────────────────────────────────────────┐
│                          Wechaty 微信机器人层                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────────┐  │
│  │  消息处理模块  │  │  事件监听模块  │  │    AI对话模块             │  │
│  │  - 撤回恢复   │  │  - room-join │  │    - DeepSeek V4-Flash   │  │
│  │  - 消息缓存   │  │  - room-leave│  │    - 语义搜索              │  │
│  │  - 消息持久化 │  │  - 邀请入群   │  │    - 上下文管理            │  │
│  └──────────────┘  └──────────────┘  └──────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
          │                │                      │
          ▼                ▼                      ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         FastAPI 后端服务层                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────────┐  │
│  │   用户认证    │  │   数据API    │  │      WebSocket          │  │
│  │  - JWT Token │  │  - 白名单管理 │  │    - 实时推送            │  │
│  │  - 角色权限   │  │  - 群聊管理   │  │    - 机器人状态         │  │
│  │  - 会话管理   │  │  - 消息查询   │  │                         │  │
│  └──────────────┘  └──────────────┘  └──────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
          │                                    │
          ▼                                    ▼
┌───────────────────────┐        ┌───────────────────────┐
│      PostgreSQL        │        │        Redis          │
│   (pgvector 向量存储)    │        │    (上下文缓存)        │
│   - 群聊消息文本         │        │   - 白名单缓存         │
│   - 白名单数据           │        │   - 会话上下文         │
│   - 群组配置            │        │   - 消息缓存(2分钟)    │
│   - 用户管理            │        │                       │
└───────────────────────┘        └───────────────────────┘
          │
          ▼
┌───────────────────────┐
│     DeepSeek API       │
│    (V4-Flash 免费版)    │
│   - AI对话             │
│   - 语义搜索扩展        │
└───────────────────────┘
```

### 1.2 项目目录结构

```
wechat-bot-admin/
├── backend/                          # FastAPI 后端服务
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                   # FastAPI 入口
│   │   ├── config.py                  # 配置管理
│   │   ├── database.py                # 数据库连接
│   │   ├── redis_client.py            # Redis 连接
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── auth.py                # 认证接口
│   │   │   ├── users.py               # 用户管理
│   │   │   ├── whitelist.py           # 白名单管理
│   │   │   ├── groups.py              # 群组管理
│   │   │   ├── messages.py             # 消息查询
│   │   │   ├── search.py               # 搜索接口
│   │   │   ├── dashboard.py            # 仪表盘
│   │   │   └── config.py              # 配置管理
│   │   ├── models/                    # SQLAlchemy 模型
│   │   │   ├── __init__.py
│   │   │   ├── user.py
│   │   │   ├── whitelist.py
│   │   │   ├── group.py
│   │   │   └── message.py
│   │   ├── schemas/                   # Pydantic schemas
│   │   │   ├── __init__.py
│   │   │   ├── user.py
│   │   │   ├── whitelist.py
│   │   │   ├── group.py
│   │   │   └── message.py
│   │   ├── services/                  # 业务逻辑层
│   │   │   ├── __init__.py
│   │   │   ├── auth_service.py
│   │   │   ├── whitelist_service.py
│   │   │   ├── ai_service.py
│   │   │   └── search_service.py
│   │   ├── core/                      # 核心模块
│   │   │   ├── __init__.py
│   │   │   ├── security.py            # JWT 安全
│   │   │   ├── dependencies.py        # 依赖注入
│   │   │   └── exceptions.py          # 异常处理
│   │   └── utils/                      # 工具函数
│   │       ├── __init__.py
│   │       └── datetime_utils.py
│   ├── requirements.txt
│   └── alembic/                        # 数据库迁移
│       ├── alembic.ini
│       └── versions/
│
├── bot/                               # 微信机器人模块
│   ├── src/
│   │   ├── __init__.py
│   │   ├── main.py                   # 机器人入口
│   │   ├── config.py                  # 机器人配置
│   │   ├── handlers/                  # 消息处理器
│   │   │   ├── __init__.py
│   │   │   ├── message_handler.py
│   │   │   ├── room_handler.py
│   │   │   ├── recall_handler.py
│   │   │   ├── ai_handler.py
│   │   │   └── search_handler.py
│   │   ├── services/                  # 机器人服务
│   │   │   ├── __init__.py
│   │   │   ├── message_cache.py       # 消息缓存(2分钟)
│   │   │   ├── message_store.py        # 消息持久化
│   │   │   ├── ai_service.py          # AI 对话服务
│   │   │   ├── search_service.py      # 语义搜索服务
│   │   │   └── whitelist_checker.py   # 白名单检查
│   │   ├── events/                    # 事件监听
│   │   │   ├── __init__.py
│   │   │   ├── room_events.py
│   │   │   └── message_events.py
│   │   └── utils/                      # 工具函数
│   │       ├── __init__.py
│   │       └── message_parser.py
│   ├── requirements.txt
│   └── docker-entrypoint.sh
│
├── frontend/                          # React 前端
│   ├── src/
│   │   ├── App.tsx
│   │   ├── main.tsx
│   │   ├── api/                       # API 调用
│   │   │   ├── index.ts
│   │   │   ├── auth.ts
│   │   │   ├── whitelist.ts
│   │   │   ├── groups.ts
│   │   │   ├── messages.ts
│   │   │   └── dashboard.ts
│   │   ├── components/                # 通用组件
│   │   │   ├── Layout/
│   │   │   ├── Table/
│   │   │   └── Form/
│   │   ├── pages/                     # 页面
│   │   │   ├── Login/
│   │   │   ├── Dashboard/
│   │   │   ├── Whitelist/
│   │   │   ├── Groups/
│   │   │   ├── Messages/
│   │   │   ├── Search/
│   │   │   └── Settings/
│   │   ├── hooks/                     # 自定义 Hooks
│   │   ├── stores/                    # 状态管理
│   │   ├── styles/                    # 样式
│   │   └── types/                     # TypeScript 类型
│   ├── package.json
│   ├── vite.config.ts
│   └── tsconfig.json
│
├── postgres/                         # PostgreSQL 初始化
│   └── init.sql                       # 初始化脚本(含pgvector)
│
├── redis/                            # Redis 配置
│   └── redis.conf
│
├── nginx/                            # Nginx 配置
│   └── nginx.conf
│
├── docker-compose.yml
├── .env.example
└── README.md
```

## 二、数据库设计

### 2.1 数据库 ER 图

```
┌──────────────────┐       ┌──────────────────┐
│   admin_users    │       │   whitelist_users │
│──────────────────│       │──────────────────│
│ id (PK)          │       │ id (PK)          │
│ username         │       │ user_id          │
│ password_hash    │       │ user_name        │
│ role             │       │ added_by (FK)   │◄────┐
│ created_at       │       │ added_at        │     │
│ last_login       │       │ expire_at       │     │
│ is_active        │       │ remark          │     │
└──────────────────┘       │ is_active       │     │
         │                 └──────────────────┘     │
         │                         ▲               │
         │    ┌─────────────────────┘               │
         │    │ (admin_users.id)                    │
         ▼    ▼                                     │
┌──────────────────┐                                 │
│  bot_groups      │                                 │
│──────────────────│                                 │
│ id (PK)          │                                 │
│ room_id          │                                 │
│ room_name        │                                 │
│ owner_id         │                                 │
│ created_at       │                                 │
│ is_active        │                                 │
│ welcome_enabled  │                                 │
│ welcome_message  │                                 │
│ ai_enabled       │                                 │
│ ai_sleep_start   │                                 │
│ ai_sleep_end     │                                 │
└────────┬─────────┘                                 │
         │                                           │
         │  1:N                                       │
         ▼                                           │
┌──────────────────┐                                 │
│  group_messages  │                                 │
│──────────────────│                                 │
│ id (PK)          │                                 │
│ group_id (FK)   │                                 │
│ sender_id        │                                 │
│ sender_name      │                                 │
│ content          │                                 │
│ content_vector   │ vector(1536)  ◄── pgvector    │
│ msg_type         │                                 │
│ is_recalled      │                                 │
│ created_at       │                                 │
│ extra_data       │ (JSONB - 存储原始消息详情)        │
└──────────────────┘                                 │
```

### 2.2 表结构详解

#### 2.2.1 admin_users - 后台管理员表

```sql
CREATE TABLE admin_users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL DEFAULT 'operator',  -- operator/admin/super_admin
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    
    CONSTRAINT role_check CHECK (role IN ('operator', 'admin', 'super_admin'))
);

CREATE INDEX idx_admin_username ON admin_users(username);
CREATE INDEX idx_admin_role ON admin_users(role);
```

#### 2.2.2 whitelist_users - 白名单用户表

```sql
CREATE TABLE whitelist_users (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(100) UNIQUE NOT NULL,      -- 微信 wxid
    user_name VARCHAR(255),                      -- 微信昵称
    added_by INTEGER REFERENCES admin_users(id),
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expire_at TIMESTAMP,                          -- 可选过期时间
    remark TEXT,
    is_active BOOLEAN DEFAULT TRUE
);

CREATE INDEX idx_whitelist_user_id ON whitelist_users(user_id);
CREATE INDEX idx_whitelist_active ON whitelist_users(is_active);
CREATE INDEX idx_whitelist_expire ON whitelist_users(expire_at);
```

#### 2.2.3 bot_groups - 机器人群组表

```sql
CREATE TABLE bot_groups (
    id SERIAL PRIMARY KEY,
    room_id VARCHAR(100) UNIQUE NOT NULL,        -- 微信群 room_id
    room_name VARCHAR(255),
    owner_id VARCHAR(100),                        -- 群主 wxid
    owner_name VARCHAR(255),                      -- 群主昵称
    invited_by INTEGER REFERENCES admin_users(id), -- 邀请人(白名单用户)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    welcome_enabled BOOLEAN DEFAULT TRUE,
    welcome_message TEXT DEFAULT '欢迎 {name} 加入群聊！',
    ai_enabled BOOLEAN DEFAULT TRUE,
    ai_sleep_start TIME DEFAULT '23:00',         -- AI 休眠开始
    ai_sleep_end TIME DEFAULT '07:00',           -- AI 休眠结束
    last_active TIMESTAMP                        -- 最后活跃时间
);

CREATE INDEX idx_bot_groups_room_id ON bot_groups(room_id);
CREATE INDEX idx_bot_groups_active ON bot_groups(is_active);
```

#### 2.2.4 group_messages - 群消息表

```sql
CREATE TABLE group_messages (
    id SERIAL PRIMARY KEY,
    group_id INTEGER REFERENCES bot_groups(id),
    sender_id VARCHAR(100) NOT NULL,
    sender_name VARCHAR(255),
    content TEXT NOT NULL,
    content_vector VECTOR(1536),                 -- DeepSeek 嵌入向量
    msg_type VARCHAR(50),                         -- text/recall/join/leave
    is_recalled BOOLEAN DEFAULT FALSE,
    raw_msg_id VARCHAR(100),                      -- 微信原始消息ID
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    extra_data JSONB                              -- 存储原始消息详情
);

-- 消息向量索引 (HNSW 算法，高性能近似搜索)
CREATE INDEX idx_messages_vector ON group_messages USING hnsw (content_vector vector_cosine_ops);
CREATE INDEX idx_messages_group_time ON group_messages(group_id, created_at DESC);
CREATE INDEX idx_messages_sender ON group_messages(sender_id);
CREATE INDEX idx_messages_recalled ON group_messages(is_recalled);
CREATE INDEX idx_messages_created ON group_messages(created_at);

-- 7天自动清理任务 (PostgreSQL event scheduler)
CREATE OR REPLACE FUNCTION cleanup_old_messages()
RETURNS void AS $$
BEGIN
    DELETE FROM group_messages 
    WHERE created_at < NOW() - INTERVAL '7 days';
END;
$$ LANGUAGE plpgsql;
```

#### 2.2.5 系统配置表

```sql
CREATE TABLE system_config (
    id SERIAL PRIMARY KEY,
    key VARCHAR(100) UNIQUE NOT NULL,
    value JSONB NOT NULL,
    description TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_by INTEGER REFERENCES admin_users(id)
);

-- 初始化默认配置
INSERT INTO system_config (key, value, description) VALUES
('whitelist', '{"enable_whitelist": true, "welcome_msg": "欢迎使用微信机器人！", "reject_msg": "您暂无权限使用此功能，请联系管理员添加白名单。"}', '白名单配置'),
('ai', '{"model": "deepseek-chat", "temperature": 0.7, "max_tokens": 2000}', 'AI模型配置'),
('bot', '{"name": "微信助手", "sleep_enabled": true}', '机器人基础配置');
```

### 2.3 pgvector 扩展启用

```sql
-- 在 postgres/init.sql 中
CREATE EXTENSION IF NOT EXISTS vector;

-- 验证向量维度
SELECT * FROM pg_extension WHERE extname = 'vector';
```

## 三、API 接口设计

### 3.1 认证接口 `/api/auth`

| 方法 | 路径 | 描述 | 权限 |
|------|------|------|------|
| POST | /login | 登录获取JWT | 公开 |
| POST | /refresh | 刷新Token | 需要Token |
| POST | /logout | 登出 | 需要Token |

#### POST /api/auth/login

Request:
```json
{
  "username": "admin",
  "password": "password123"
}
```

Response:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "Bearer",
  "expires_in": 7200,
  "user": {
    "id": 1,
    "username": "admin",
    "role": "super_admin"
  }
}
```

### 3.2 白名单管理 `/api/whitelist`

| 方法 | 路径 | 描述 | 权限 |
|------|------|------|------|
| GET | / | 获取白名单列表 | admin+ |
| POST | / | 添加白名单用户 | admin+ |
| DELETE | /{id} | 移除白名单用户 | admin+ |
| POST | /import | 批量导入CSV | admin+ |
| GET | /export | 导出CSV | admin+ |
| GET | /stats | 白名单统计 | operator+ |
| POST | /check | 检查用户是否在白名单 | 机器人调用 |

#### GET /api/whitelist

Query Parameters:
- page: 页码 (default: 1)
- page_size: 每页数量 (default: 20)
- keyword: 搜索关键词 (wxid或昵称)
- is_active: 状态筛选
- expire_soon: 即将过期 (24小时内)

Response:
```json
{
  "total": 150,
  "page": 1,
  "page_size": 20,
  "items": [
    {
      "id": 1,
      "user_id": "wxid_abc123",
      "user_name": "张三",
      "added_by": "admin",
      "added_at": "2024-01-15T10:30:00Z",
      "expire_at": "2024-12-31T23:59:59Z",
      "remark": "VIP用户",
      "is_active": true
    }
  ]
}
```

### 3.3 群组管理 `/api/groups`

| 方法 | 路径 | 描述 | 权限 |
|------|------|------|------|
| GET | / | 获取群组列表 | operator+ |
| GET | /{id} | 获取群组详情 | operator+ |
| POST | / | 创建群组配置 | admin+ |
| PUT | /{id} | 更新群组配置 | admin+ |
| DELETE | /{id} | 删除群组 | super_admin |
| PUT | /{id}/welcome | 更新欢迎语 | admin+ |
| PUT | /{id}/ai | 更新AI配置 | admin+ |

### 3.4 消息管理 `/api/messages`

| 方法 | 路径 | 描述 | 权限 |
|------|------|------|------|
| GET | / | 获取消息列表 | operator+ |
| GET | /{id} | 获取消息详情 | operator+ |
| GET | /stats | 消息统计 | operator+ |

#### GET /api/messages

Query Parameters:
- group_id: 群组ID
- sender_id: 发送者ID
- keyword: 关键词搜索
- msg_type: 消息类型
- start_date: 开始日期
- end_date: 结束日期
- page: 页码
- page_size: 每页数量

### 3.5 搜索接口 `/api/search`

| 方法 | 路径 | 描述 | 权限 |
|------|------|------|------|
| POST | /semantic | 语义搜索消息 | operator+ |
| POST | /keyword | 关键词搜索 | operator+ |
| GET | /suggestions | 获取搜索建议 | operator+ |

#### POST /api/search/semantic

Request:
```json
{
  "query": "查找关于项目进度的讨论",
  "group_id": 1,
  "top_k": 10,
  "include_context": true
}
```

Response:
```json
{
  "query": "查找关于项目进度的讨论",
  "expanded_keywords": ["项目", "进度", "计划", "状态", "更新"],
  "results": [
    {
      "id": 123,
      "content": "项目进度已经完成了80%",
      "sender_name": "张三",
      "group_name": "开发群",
      "created_at": "2024-01-15T14:30:00Z",
      "similarity": 0.92
    }
  ],
  "total": 10,
  "search_time_ms": 45
}
```

### 3.6 仪表盘 `/api/dashboard`

| 方法 | 路径 | 描述 | 权限 |
|------|------|------|------|
| GET | /overview | 全局概览 | operator+ |
| GET | /group/{id} | 单群分析 | operator+ |
| GET | /activity | 活跃度趋势 | operator+ |
| GET | /whitelist | 白名单统计 | operator+ |

#### GET /api/dashboard/overview

Response:
```json
{
  "total_groups": 25,
  "total_messages_7d": 15840,
  "total_whitelist_users": 150,
  "active_users_7d": 320,
  "message_trend": [
    {"date": "2024-01-09", "count": 2100},
    {"date": "2024-01-10", "count": 2350}
  ],
  "top_groups": [
    {"id": 1, "name": "开发群", "message_count": 3200}
  ]
}
```

### 3.7 配置管理 `/api/config`

| 方法 | 路径 | 描述 | 权限 |
|------|------|------|------|
| GET | / | 获取所有配置 | operator+ |
| GET | /{key} | 获取指定配置 | operator+ |
| PUT | /{key} | 更新配置 | admin+ |
| GET | /ai/models | 获取可用模型 | operator+ |

## 四、微信机器人设计

### 4.1 消息处理流程

```
┌────────────────────────────────────────────────────────────────────┐
│                        微信消息接收                                 │
│                    (Wechaty onMessage 事件)                          │
└─────────────────────────────┬──────────────────────────────────────┘
                              │
                              ▼
┌────────────────────────────────────────────────────────────────────┐
│                         消息类型判断                                 │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐      │
│  │ 私聊    │ │ 群聊    │ │ 撤回通知 │ │ 入群事件 │ │ 退群事件 │      │
│  │(TEXT)  │ │(@机器人)│ │(10002)  │ │(room-  │ │(room-   │      │
│  │        │ │         │ │         │ │ join)  │ │ leave)  │      │
│  └────┬────┘ └────┬────┘ └────┬────┘ └────┬────┘ └────┬────┘      │
└───────┼───────────┼───────────┼───────────┼───────────┼─────────────┘
        │           │           │           │           │
        ▼           ▼           ▼           ▼           ▼
┌────────────────────────────────────────────────────────────────────┐
│                         权限检查                                    │
│  ┌─────────────────────────┐  ┌─────────────────────────┐        │
│  │ 私聊: 检查白名单         │  │ 群聊: 直接通过           │        │
│  │ 非白名单 → 回复拒绝消息   │  │ 入群邀请 → 检查白名单     │        │
│  └─────────────────────────┘  └─────────────────────────┘        │
└────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌────────────────────────────────────────────────────────────────────┐
│                         业务处理                                    │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐  │
│  │ AI对话      │ │ 消息持久化   │ │ 消息缓存     │ │ 事件处理    │  │
│  │ - 上下文    │ │ - PostgreSQL│ │ - Redis 2分钟│ │ - 欢迎语   │  │
│  │ - DeepSeek │ │ - 仅文本     │ │ - 撤回恢复   │ │ - 退群通知 │  │
│  └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘  │
└────────────────────────────────────────────────────────────────────┘
```

### 4.2 撤回消息恢复流程

```python
# 1. 收到撤回通知 (MsgType=10002)
on_message(msg):
    if msg.type() == MessageType.Recalled:
        # 2. 解析撤回通知，获取原始消息ID
        original_msg_id = parse_recall_info(msg)
        
        # 3. 从Redis缓存获取原始消息
        original_msg = redis.get(f"msg_cache:{original_msg_id}")
        
        # 4. 如果找到，发送恢复消息到群
        if original_msg:
            recovery_text = f"🔔 消息被撤回，已恢复：👤 {original_msg.sender} 说：{original_msg.content}"
            room.say(recovery_text)
        
        # 5. 更新数据库标记
        db.update_message_recalled(original_msg_id)
```

### 4.3 语义搜索流程

```python
async def semantic_search(query: str, room_id: str, top_k: int = 10):
    # 1. AI 扩展查询语义
    expanded = await ai_service.expand_query(query)
    # 返回: {"keywords": ["项目", "进度", "计划"], "synonyms": [...]}
    
    # 2. 获取查询向量
    query_vector = await ai_service.get_embedding(query)
    
    # 3. 混合检索
    # 70% 语义向量相似度
    semantic_results = await db.vector_search(
        query_vector, 
        group_id=room_id,
        limit=top_k
    )
    
    # 30% 关键词匹配
    keyword_results = await db.text_search(
        keywords=expanded["keywords"],
        group_id=room_id,
        limit=top_k
    )
    
    # 4. 加权合并结果
    combined = merge_results(semantic_results, keyword_results, weight=[0.7, 0.3])
    
    # 5. 返回 Top10 按相关性排序
    return sorted(combined, key=lambda x: x.score, reverse=True)[:10]
```

### 4.4 AI 对话上下文管理

```python
# Redis 存储结构
# 群聊上下文: chat:group:{room_id} -> List[Message]
# 私聊上下文: chat:user:{user_id} -> List[Message]
# TTL: 群聊 24小时，私聊 24小时

class ConversationContext:
    MAX_GROUP_MESSAGES = 10  # 群聊保留10轮
    MAX_PRIVATE_MESSAGES = 20  # 私聊保留20轮
    
    async def add_message(self, key: str, role: str, content: str):
        messages = await self.redis.lrange(key, 0, -1)
        messages.append({"role": role, "content": content})
        
        # 截断到最大长度
        if "group:" in key:
            messages = messages[-self.MAX_GROUP_MESSAGES*2:]
        else:
            messages = messages[-self.MAX_PRIVATE_MESSAGES*2:]
        
        await self.redis.setex(key, 86400, json.dumps(messages))
    
    async def get_context(self, key: str) -> List[Dict]:
        messages = await self.redis.get(key)
        return json.loads(messages) if messages else []
```

### 4.5 AI 休眠时段控制

```python
def is_ai_active() -> bool:
    now = datetime.now()
    current_time = now.time()
    
    # 从配置获取休眠时段
    sleep_start = Config.get("ai_sleep_start", "23:00")
    sleep_end = Config.get("ai_sleep_end", "07:00")
    
    if sleep_start <= sleep_end:
        # 同一天: 23:00 - 07:00 (次日)
        if sleep_start <= current_time or current_time < sleep_end:
            return False
    else:
        # 跨天: 23:00 - 07:00
        if sleep_start <= current_time or current_time < sleep_end:
            return False
    
    return True
```

## 五、前端设计

### 5.1 页面结构

```
/                           # 首页仪表盘
├── /login                  # 登录页
├── /dashboard              # 仪表盘概览
├── /whitelist              # 白名单管理
│   ├── /whitelist          # 白名单列表
│   ├── /whitelist/add      # 添加白名单
│   └── /whitelist/import   # 批量导入
├── /groups                 # 群组管理
│   ├── /groups             # 群组列表
│   ├── /groups/:id         # 群组详情
│   └── /groups/:id/edit    # 编辑群组
├── /messages               # 消息管理
│   ├── /messages            # 消息列表
│   └── /messages/:id        # 消息详情
├── /search                 # 智能搜索
│   └── /search              # 搜索页面
├── /settings               # 配置管理
│   └── /settings            # 系统配置
└── /profile                # 个人中心
```

### 5.2 核心组件

| 组件 | 说明 |
|------|------|
| AppLayout | 应用布局容器 (侧边栏+内容区) |
| DataTable | 通用数据表格 (分页/筛选/排序) |
| SearchBar | 搜索栏组件 |
| StatCard | 统计卡片组件 |
| WhitelistTable | 白名单管理表格 |
| GroupCard | 群组卡片组件 |
| MessageList | 消息列表组件 |
| TrendChart | 趋势图表组件 |
| ModalForm | 模态框表单 |

### 5.3 状态管理

```typescript
// 使用 Zustand 进行状态管理
interface AppStore {
  // 认证状态
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  
  // UI 状态
  sidebarCollapsed: boolean;
  loading: boolean;
  
  // 数据缓存
  whitelist: WhitelistUser[];
  groups: Group[];
  
  // Actions
  login: (credentials: LoginCredentials) => Promise<void>;
  logout: () => void;
  fetchWhitelist: () => Promise<void>;
  addWhitelist: (user: WhitelistUser) => Promise<void>;
  removeWhitelist: (id: number) => Promise<void>;
}
```

## 六、部署架构

### 6.1 Docker Compose 架构

```yaml
services:
  # PostgreSQL 数据库
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: wechat_bot
      POSTGRES_USER: bot_admin
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./postgres/init.sql:/docker-entrypoint-initdb.d/init.sql
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U bot_admin"]
      interval: 10s
      timeout: 5s
      retries: 5
  
  # Redis 缓存
  redis:
    image: redis:7-alpine
    command: redis-server /usr/local/etc/redis/redis.conf
    volumes:
      - redis_data:/data
      - ./redis/redis.conf:/usr/local/etc/redis/redis.conf
    ports:
      - "6379:6379"
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5
  
  # FastAPI 后端
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    environment:
      DATABASE_URL: postgresql://bot_admin:${DB_PASSWORD}@postgres:5432/wechat_bot
      REDIS_URL: redis://redis:6379
      JWT_SECRET: ${JWT_SECRET}
      DEEPSEEK_API_KEY: ${DEEPSEEK_API_KEY}
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    ports:
      - "8000:8000"
    restart: unless-stopped
  
  # React 前端
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    environment:
      VITE_API_BASE_URL: http://localhost:8000
    ports:
      - "3000:80"  # Nginx 监听 80
    depends_on:
      - backend
    restart: unless-stopped
  
  # 微信机器人 (需要图形界面环境)
  bot:
    build:
      context: ./bot
      dockerfile: Dockerfile
    environment:
      DATABASE_URL: postgresql://bot_admin:${DB_PASSWORD}@postgres:5432/wechat_bot
      REDIS_URL: redis://redis:6379
      DEEPSEEK_API_KEY: ${DEEPSEEK_API_KEY}
      WECHATY_TOKEN: ${WECHATY_TOKEN}
      BACKEND_URL: http://backend:8000
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
      backend:
        condition: service_started
    restart: unless-stopped
    # 注意: Wechaty 需要图形界面，生产环境建议单独部署

volumes:
  postgres_data:
  redis_data:
```

### 6.2 环境变量配置

```bash
# .env.example

# 数据库
DB_PASSWORD=your_secure_password_here

# JWT
JWT_SECRET=your_jwt_secret_key_min_32_chars
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=120

# DeepSeek API
DEEPSEEK_API_KEY=your_deepseek_api_key
DEEPSEEK_BASE_URL=https://api.deepseek.com

# Wechaty (可选)
WECHATY_TOKEN=your_wechaty_token
WECHATY_PUPPET=wechaty-puppet-donut

# Redis
REDIS_PASSWORD=

# 服务地址
BACKEND_URL=http://localhost:8000
FRONTEND_URL=http://localhost:3000
```

## 七、Redis 数据结构设计

### 7.1 Key 命名规范

| Key Pattern | Type | TTL | 说明 |
|-------------|------|-----|------|
| `msg_cache:{msg_id}` | Hash | 2分钟 | 最近2分钟的消息缓存 |
| `chat:group:{room_id}` | List | 24小时 | 群聊对话上下文 |
| `chat:user:{user_id}` | List | 24小时 | 私聊对话上下文 |
| `whitelist:{user_id}` | String | 5分钟 | 白名单用户缓存 |
| `rate_limit:{user_id}` | String | 1分钟 | API 调用频率限制 |
| `bot:status` | Hash | - | 机器人在线状态 |

### 7.2 消息缓存结构

```python
# msg_cache:{msg_id}
{
    "sender_id": "wxid_xxx",
    "sender_name": "张三",
    "content": "消息内容",
    "room_id": "room_xxx",
    "msg_type": "text",
    "timestamp": 1705312200
}
```

## 八、核心算法

### 8.1 混合搜索权重计算

```python
def calculate_relevance_score(
    semantic_score: float,    # 0-1, 向量相似度
    keyword_score: float       # 0-1, 关键词匹配度
) -> float:
    """
    混合搜索权重:
    - 语义向量相似度: 70%
    - 关键词匹配: 30%
    """
    return semantic_score * 0.7 + keyword_score * 0.3

def keyword_match_score(query_keywords: List[str], content: str) -> float:
    """计算关键词匹配度"""
    content_lower = content.lower()
    matches = sum(1 for kw in query_keywords if kw in content_lower)
    return matches / len(query_keywords) if query_keywords else 0
```

### 8.2 消息去重算法

```python
def deduplicate_messages(messages: List[Message], window_seconds: int = 60) -> List[Message]:
    """
    在时间窗口内对相似消息进行去重
    """
    seen = {}
    result = []
    
    for msg in messages:
        # 生成消息指纹 (发送者 + 内容hash + 时间窗口)
        fingerprint = (
            msg.sender_id,
            hash(msg.content) // window_seconds,
            msg.created_at // window_seconds
        )
        
        if fingerprint not in seen:
            seen[fingerprint] = True
            result.append(msg)
    
    return result
```

## 九、安全设计

### 9.1 JWT 认证流程

```
┌─────────────────────────────────────────────────────────────────────┐
│                         JWT 认证流程                                 │
│                                                                     │
│  1. 登录请求                                                         │
│     Client ──POST /api/auth/login──► Server                         │
│                    {username, password}                             │
│                                                                     │
│  2. 验证并生成 Token                                                  │
│     Server ──验证密码──► 生成 Access Token + Refresh Token           │
│                                                                     │
│  3. 返回 Token                                                        │
│     Server ──► Client                                                │
│     {access_token, refresh_token, expires_in}                       │
│                                                                     │
│  4. 后续请求携带 Token                                                 │
│     Client ──► Server (Authorization: Bearer {token})               │
│                                                                     │
│  5. Token 验证                                                        │
│     Server ──验证签名和过期时间──► 提取用户信息                        │
│                                                                     │
│  6. 返回受保护资源                                                    │
│     Server ──► Client                                                │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### 9.2 权限矩阵

| 功能 | operator | admin | super_admin |
|------|----------|-------|-------------|
| 查看仪表盘 | ✅ | ✅ | ✅ |
| 查看白名单 | ✅ | ✅ | ✅ |
| 添加白名单 | ❌ | ✅ | ✅ |
| 移除白名单 | ❌ | ✅ | ✅ |
| 导入/导出白名单 | ❌ | ✅ | ✅ |
| 查看群组 | ✅ | ✅ | ✅ |
| 管理群组 | ❌ | ✅ | ✅ |
| 删除群组 | ❌ | ❌ | ✅ |
| 查看消息 | ✅ | ✅ | ✅ |
| 智能搜索 | ✅ | ✅ | ✅ |
| 修改系统配置 | ❌ | ✅ | ✅ |
| 管理管理员账户 | ❌ | ❌ | ✅ |

## 十、错误处理

### 10.1 错误码定义

```python
class ErrorCode:
    # 认证错误 (1000-1999)
    AUTH_INVALID_CREDENTIALS = 1001
    AUTH_TOKEN_EXPIRED = 1002
    AUTH_TOKEN_INVALID = 1003
    AUTH_PERMISSION_DENIED = 1004
    
    # 白名单错误 (2000-2999)
    WHITELIST_USER_NOT_FOUND = 2001
    WHITELIST_USER_EXISTS = 2002
    WHITELIST_IMPORT_FAILED = 2003
    
    # 群组错误 (3000-3999)
    GROUP_NOT_FOUND = 3001
    GROUP_ALREADY_EXISTS = 3002
    
    # AI 服务错误 (4000-4999)
    AI_SERVICE_UNAVAILABLE = 4001
    AI_RATE_LIMIT_EXCEEDED = 4002
    AI_INVALID_RESPONSE = 4003
```

### 10.2 统一错误响应格式

```json
{
  "error": {
    "code": 1001,
    "message": "用户名或密码错误",
    "details": {},
    "request_id": "req_abc123"
  }
}
```
