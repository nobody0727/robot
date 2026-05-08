# 微信机器人后台管理系统

一套低成本的微信机器人系统，支持文本消息处理、免费大模型AI对话、白名单权限控制，以及完整的Web后台管理界面。

## 功能特性

### 微信机器人功能

- **撤回消息恢复** - 监听群聊撤回消息，自动从缓存恢复并发送
- **AI语义搜索** - 智能扩展查询，结合向量相似度和关键词匹配
- **消息持久化** - 7天滚动保存，仅文本消息
- **入群欢迎** - 自动发送欢迎语
- **退群提醒** - 通知群主/管理员
- **AI对话** - 群聊@机器人、私聊对话（需白名单）
- **上下文记忆** - 多轮对话支持

### 白名单机制

| 场景 | 权限要求 |
|------|---------|
| 私聊机器人 | 必须白名单 |
| 邀请入群 | 必须白名单 |
| 群聊@机器人 | 无需白名单 |

### 后台管理功能

- JWT Token认证 + 三级权限控制
- 白名单管理（添加/移除/导入/导出）
- 群组管理（配置欢迎语、AI参数）
- 消息查询与统计
- 语义搜索
- 数据分析仪表盘
- 系统配置

## 技术栈

| 组件 | 技术选型 |
|------|---------|
| 微信接入 | Wechaty + Paimon协议 |
| 后端API | FastAPI (Python 3.11) |
| 前端 | React 18 + Ant Design 5 |
| 数据库 | PostgreSQL 15 + pgvector |
| 缓存 | Redis 7 |
| AI接口 | DeepSeek V4-Flash (免费版) |
| 部署 | Docker + Docker Compose |

## 快速开始

### 环境要求

- Docker & Docker Compose
- DeepSeek API Key（免费获取）

### 1. 克隆项目

```bash
git clone <repository-url>
cd wechat-bot-admin
```

### 2. 配置环境变量

```bash
cp .env.example .env
```

编辑 `.env` 文件，填写以下必填项：

```env
DB_PASSWORD=your_secure_password
JWT_SECRET=your_jwt_secret_min_32_chars
DEEPSEEK_API_KEY=your_deepseek_api_key
WECHATY_TOKEN=your_wechaty_token
```

### 3. 启动服务

```bash
docker-compose up -d
```

### 4. 访问后台

- 前端地址：http://localhost:3000
- API文档：http://localhost:8000/docs
- 默认账号：`admin` / `admin123`

## 项目结构

```
wechat-bot-admin/
├── backend/              # FastAPI 后端服务
│   ├── app/
│   │   ├── api/         # API 路由
│   │   ├── core/        # 核心模块 (JWT、异常处理)
│   │   ├── models/       # SQLAlchemy 模型
│   │   ├── schemas/      # Pydantic schemas
│   │   ├── services/      # 业务逻辑
│   │   └── main.py        # 入口文件
│   └── requirements.txt
│
├── bot/                 # 微信机器人
│   ├── src/
│   │   ├── handlers/    # 消息处理器
│   │   ├── services/     # 服务层
│   │   └── main.py       # 入口文件
│   └── requirements.txt
│
├── frontend/            # React 前端
│   ├── src/
│   │   ├── api/         # API 调用
│   │   ├── components/   # 组件
│   │   ├── pages/        # 页面
│   │   ├── stores/       # 状态管理
│   │   └── types/        # TypeScript 类型
│   └── package.json
│
├── postgres/            # PostgreSQL 初始化脚本
├── redis/               # Redis 配置
├── docker-compose.yml   # Docker Compose 配置
└── SPEC.md             # 技术架构文档
```

## API 文档

启动服务后访问：http://localhost:8000/docs

### 认证

```
POST /api/auth/login
{
  "username": "admin",
  "password": "admin123"
}
```

### 白名单管理

```
GET  /api/whitelist          # 获取白名单列表
POST /api/whitelist          # 添加白名单用户
DELETE /api/whitelist/{id}   # 移除白名单
GET  /api/whitelist/stats    # 白名单统计
```

### 群组管理

```
GET  /api/groups             # 获取群组列表
POST /api/groups             # 创建群组
PUT  /api/groups/{id}        # 更新群组
```

### 消息查询

```
GET /api/messages             # 获取消息列表
GET /api/messages/stats       # 消息统计
```

### 搜索

```
POST /api/search/semantic     # 语义搜索
POST /api/search/keyword      # 关键词搜索
```

## 权限说明

| 角色 | 权限 |
|------|------|
| operator | 查看数据、搜索 |
| admin | operator + 修改配置、管理白名单 |
| super_admin | admin + 删除数据、管理账户 |

## 配置说明

### AI休眠时段

默认 23:00 - 07:00 AI自动休眠，不响应群聊消息。

### 消息缓存

- Redis缓存最近2分钟的消息
- 用于撤回消息恢复
- 过期自动清理

### 上下文记忆

- 群聊：保留最近10轮对话
- 私聊：保留最近20轮对话
- TTL：24小时

## 开发指南

### 后端开发

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### 前端开发

```bash
cd frontend
npm install
npm run dev
```

### 机器人开发

```bash
cd bot
pip install -r requirements.txt
python -m bot.src.main
```

## 生产部署

1. 配置生产环境变量
2. 使用 Nginx 反向代理
3. 配置 HTTPS
4. 定期备份数据库
5. 监控服务状态

## 注意事项

1. **安全**：修改默认密码和JWT密钥
2. **微信协议**：遵守微信使用规范
3. **AI成本**：DeepSeek V4-Flash免费，但有调用限制
4. **数据备份**：定期备份PostgreSQL数据

## License

MIT License
