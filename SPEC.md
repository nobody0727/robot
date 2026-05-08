# QQ 机器人后台管理系统 - 技术架构文档

## 一、项目整体架构

### 1.1 系统架构图

```
┌─────────────────────────────────────────────────────────────────────┐
│                           用户层                                     │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────────┐   │
│  │  QQ用户      │  │  QQ用户     │  │       后台管理员            │   │
│  │  (私聊/群聊) │  │  (入群邀请)  │  │  (Web管理界面)              │   │
│  └──────┬──────┘  └──────┬──────┘  └─────────────┬───────────────┘   │
└─────────┼────────────────┼──────────────────────┼───────────────────┘
          │                │                      │
          ▼                ▼                      ▼
┌─────────────────────────────────────────────────────────────────────┐
│                          QQ 机器人层                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────────┐  │
│  │ NoneBot2     │  │ NapCatQQ     │  │    AI对话模块             │  │
│  │ 消息处理      │  │ 协议适配     │  │    - DeepSeek V4-Flash   │  │
│  │ 插件系统      │  │ (OneBot11)  │  │    - 语义搜索              │  │
│  │ 权限控制      │  │              │  │    - 上下文管理            │  │
│  └──────────────┘  └──────────────┘  └──────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
          │                                    │
          ▼                                    ▼
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
qq-bot-admin/
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
│   │   │   ├── messages.py            # 消息查询
│   │   │   ├── search.py              # 搜索接口
│   │   │   ├── dashboard.py           # 仪表盘
│   │   │   └── config.py              # 配置管理
│   │   ├── models/                    # SQLAlchemy 模型
│   │   ├── schemas/                   # Pydantic schemas
│   │   ├── services/                  # 业务逻辑层
│   │   ├── core/                      # 核心模块
│   │   └── utils/                     # 工具函数
│   └── requirements.txt
│
├── bot/                              # QQ 机器人模块 (NoneBot2)
│   ├── nonebot.ini                   # NoneBot2 配置
│   ├── pyproject.toml                # Python 项目配置
│   ├── src/
│   │   ├── plugins/                  # NoneBot2 插件
│   │   │   ├── __init__.py
│   │   │   ├── ai_chat.py            # AI 对话插件
│   │   │   ├── message_recall.py     # 消息撤回插件
│   │   │   ├── group_welcome.py     # 入群欢迎插件
│   │   │   ├── search_plugin.py      # 搜索插件
│   │   │   └── admin_plugin.py       # 管理插件
│   │   ├── services/                 # 服务层
│   │   │   ├── ai_service.py         # AI 服务
│   │   │   ├── message_service.py    # 消息服务
│   │   │   ├── whitelist_service.py   # 白名单服务
│   │   │   └── api_client.py         # 后端 API 客户端
│   │   └── utils/                    # 工具函数
│   │       ├── config.py             # 机器人配置
│   │       └── helpers.py            # 辅助函数
│   ├── .env                          # 环境变量
│   └── requirements.txt
│
├── napcat/                           # NapCatQQ 配置
│   └── config.sh                     # NapCat 启动配置
│
├── frontend/                         # React 前端
│   ├── src/
│   │   ├── App.tsx
│   │   ├── main.tsx
│   │   ├── api/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── stores/
│   │   └── types/
│   └── package.json
│
├── postgres/                         # PostgreSQL 初始化
│   └── init.sql
│
├── redis/                            # Redis 配置
│   └── redis.conf
│
├── docker-compose.yml
├── .env.example
├── README.md
├── LINUX_DEPLOY.md
├── WINDOWS_DEPLOY.md
└── SPEC.md
```

## 二、数据库设计

### 2.1 数据库 ER 图

```
┌──────────────────┐       ┌──────────────────┐
│   admin_users    │       │   whitelist_users │
│──────────────────│       │──────────────────│
│ id (PK)          │       │ id (PK)          │
│ username         │       │ user_id (QQ号)   │
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
│ group_id (QQ群号)│                                 │
│ group_name       │                                 │
│ owner_id (群主)  │                                 │
│ created_at       │                                 │
│ is_active        │                                 │
│ welcome_enabled  │                                 │
│ welcome_message  │                                 │
│ ai_enabled       │                                 │
│ ai_sleep_start  │                                 │
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
│ sender_id (QQ号) │                                 │
│ sender_name      │                                 │
│ content          │                                 │
│ content_vector   │ vector(1536)  ◄── pgvector    │
│ msg_type         │                                 │
│ is_recalled      │                                 │
│ raw_msg_id       │                                 │
│ created_at       │                                 │
│ extra_data       │ (JSONB)                        │
└──────────────────┘                                 │
```

### 2.2 表结构详解

#### 2.2.1 admin_users - 后台管理员表

```sql
CREATE TABLE admin_users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL DEFAULT 'operator',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);
```

#### 2.2.2 whitelist_users - 白名单用户表

```sql
CREATE TABLE whitelist_users (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(20) UNIQUE NOT NULL,      -- QQ号
    user_name VARCHAR(255),                    -- QQ昵称
    added_by INTEGER REFERENCES admin_users(id),
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expire_at TIMESTAMP,
    remark TEXT,
    is_active BOOLEAN DEFAULT TRUE
);
```

#### 2.2.3 bot_groups - 机器人群组表

```sql
CREATE TABLE bot_groups (
    id SERIAL PRIMARY KEY,
    group_id VARCHAR(20) UNIQUE NOT NULL,      -- QQ群号
    group_name VARCHAR(255),
    owner_id VARCHAR(20),                       -- 群主QQ号
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
```

#### 2.2.4 group_messages - 群消息表

```sql
CREATE TABLE group_messages (
    id SERIAL PRIMARY KEY,
    group_id INTEGER REFERENCES bot_groups(id),
    sender_id VARCHAR(20) NOT NULL,             -- 发送者QQ号
    sender_name VARCHAR(255),
    content TEXT NOT NULL,
    content_vector VECTOR(1536),
    msg_type VARCHAR(50),                       -- text/recall/join/leave
    is_recalled BOOLEAN DEFAULT FALSE,
    raw_msg_id VARCHAR(50),                     -- 原始消息ID
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    extra_data JSONB
);

CREATE INDEX idx_messages_vector ON group_messages USING hnsw (content_vector vector_cosine_ops);
CREATE INDEX idx_messages_group_time ON group_messages(group_id, created_at DESC);
CREATE INDEX idx_messages_sender ON group_messages(sender_id);
```

## 三、QQ 机器人设计

### 3.1 技术选型

| 组件 | 技术选型 | 说明 |
|------|---------|------|
| 机器人框架 | NoneBot2 | 异步 Python 机器人框架 |
| 协议适配 | NapCatQQ | 基于 NTQQ 的 OneBot11 协议实现 |
| 通信方式 | HTTP POST + WebSocket | NapCat 通过正向 WS 或 HTTP 推送事件 |

### 3.2 NapCatQQ 配置

```json
{
  "NapCat": {
    "port": 3000,
    "httpPort": 3001,
    "wsPort": 3002,
    "autoDeleteFile": false,
    "enablePerRequestAgent": false,
    "enableQrcode": true
  },
  "account": {
    "uin": 123456789,
    "password": "your_password",
    "protocol": "mac"
  }
}
```

### 3.3 NoneBot2 配置

```toml
# nonebot2.toml
[driver]
ws_driver = true
http_driver = true

[plugin]
store_dir = "src/plugins"

[nonebot]
app = "nonebot.web.app:app"
host = "0.0.0.0"
port = 8080
```

### 3.4 消息处理流程

```
┌────────────────────────────────────────────────────────────────────┐
│                       QQ 消息接收 (NapCat -> NoneBot2)              │
│                    (OneBot11 API: 接收消息事件)                       │
└─────────────────────────────┬──────────────────────────────────────┘
                              │
                              ▼
┌────────────────────────────────────────────────────────────────────┐
│                         消息类型判断                                 │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐     │
│  │ 私聊    │ │ 群聊    │ │ 撤回通知 │ │ 入群事件 │ │ 退群事件 │     │
│  │(private)│ │(group)  │ │(recall) │ │(notify) │ │(notify) │     │
│  └────┬────┘ └────┬────┘ └────┬────┘ └────┬────┘ └────┬────┘     │
└───────┼───────────┼───────────┼───────────┼───────────┼─────────────┘
        │           │           │           │           │
        ▼           ▼           ▼           ▼           ▼
┌────────────────────────────────────────────────────────────────────┐
│                         权限检查                                    │
│  ┌─────────────────────────┐  ┌─────────────────────────┐          │
│  │ 私聊: 检查白名单         │  │ 群聊: @机器人 或命令     │          │
│  │ 非白名单 → 回复拒绝消息   │  │ 直接通过                  │          │
│  └─────────────────────────┘  └─────────────────────────┘          │
└────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌────────────────────────────────────────────────────────────────────┐
│                         业务处理                                    │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ │
│  │ AI对话      │ │ 消息持久化   │ │ 消息缓存     │ │ 事件处理    │ │
│  │ - 上下文    │ │ - PostgreSQL│ │ - Redis 2分钟│ │ - 欢迎语   │ │
│  │ - DeepSeek │ │ - 仅文本     │ │ - 撤回恢复   │ │ - 退群通知 │ │
│  └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘ │
└────────────────────────────────────────────────────────────────────┘
```

### 3.5 插件设计

#### AI 对话插件

```python
# src/plugins/ai_chat.py
from nonebot import on_message, on_command
from nonebot.adapters.onebot.v11 import GroupMessageEvent, PrivateMessageEvent
from nonebot.typing import T_State
import httpx

ai_chat = on_message(rule=...)
ai_help = on_command("帮助", "help")

@ai_chat.handle()
async def handle_ai(event: GroupMessageEvent):
    user_id = event.user_id
    group_id = event.group_id
    content = event.message.extract_plain_text()

    # 检查白名单
    if not await check_whitelist(user_id):
        await ai_chat.finish("您暂无权限使用AI功能")

    # 检查AI是否启用
    if not await is_ai_enabled(group_id):
        return

    # 获取上下文
    context = await get_conversation_context(group_id, user_id)

    # 调用 DeepSeek API
    response = await call_deepseek(content, context)

    # 保存上下文
    await save_conversation_context(group_id, user_id, content, response)

    await ai_chat.finish(response)
```

#### 入群欢迎插件

```python
# src/plugins/group_welcome.py
from nonebot import on_notice
from nonebot.adapters.onebot.v11 import GroupIncreaseNoticeEvent

group_join = on_notice("group_increase")

@group_join.handle()
async def handle_join(event: GroupIncreaseNoticeEvent):
    if event.user_id == event.self_id:
        return  # 机器人自己加入群

    group_id = event.group_id
    user_id = event.user_id

    # 检查白名单
    if not await check_whitelist(user_id):
        await group_join.finish()

    # 获取欢迎语
    welcome_msg = await get_welcome_message(group_id)
    if welcome_msg:
        user_info = await get_user_info(user_id)
        msg = welcome_msg.format(name=user_info.nickname)
        await group_join.finish(msg)
```

## 四、环境变量配置

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

# NapCatQQ
NAPCAT_HTTP_PORT=3001
NAPCAT_WS_PORT=3002

# NoneBot2
NB_HOST=0.0.0.0
NB_PORT=8080

# 机器人配置
BOT_QQ_NUMBER=123456789
BOT_ADMIN_QQS=10001,10002

# 服务地址
BACKEND_URL=http://localhost:8000
FRONTEND_URL=http://localhost:3000
```

## 五、Docker Compose 部署

```yaml
services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: qq_bot
      POSTGRES_USER: bot_admin
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./postgres/init.sql:/docker-entrypoint-initdb.d/init.sql
    ports:
      - "5432:5432"

  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data
    ports:
      - "6379:6379"

  napcat:
    image: cr放在了/netease/netease-napcat:latest
    ports:
      - "3001:3001"
      - "3002:3002"
    environment:
      - NAPCAT_QQ=123456789
      - NAPCAT_PASSWORD=your_password
    volumes:
      - ./napcat/config:/opt/napcat/config
      - napcat_data:/data

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    environment:
      DATABASE_URL: postgresql://bot_admin:${DB_PASSWORD}@postgres:5432/qq_bot
      REDIS_URL: redis://redis:6379
      JWT_SECRET: ${JWT_SECRET}
      DEEPSEEK_API_KEY: ${DEEPSEEK_API_KEY}
    ports:
      - "8000:8000"
    depends_on:
      - postgres
      - redis

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    ports:
      - "3000:80"
    depends_on:
      - backend

  bot:
    build:
      context: ./bot
      dockerfile: Dockerfile
    environment:
      DATABASE_URL: postgresql://bot_admin:${DB_PASSWORD}@postgres:5432/qq_bot
      REDIS_URL: redis://redis:6379
      DEEPSEEK_API_KEY: ${DEEPSEEK_API_KEY}
      NAPCAT_HTTP_URL: http://napcat:3001
      NAPCAT_WS_URL: ws://napcat:3002
      BACKEND_URL: http://backend:8000
    depends_on:
      - napcat
      - backend
    ports:
      - "8080:8080"
```
