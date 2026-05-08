# Windows 本地部署指南

## 一、环境准备

### 1.1 安装必需软件

#### 1.1.1 安装 Docker Desktop (Windows)

1. 下载 Docker Desktop: https://www.docker.com/products/docker-desktop
2. 双击安装包 `Docker Desktop Installer.exe`
3. 勾选 "Use WSL 2 instead of Hyper-V" (推荐)
4. 安装完成后重启电脑
5. 启动 Docker Desktop，等待托盘图标显示绿色

**验证安装:**
```powershell
docker --version
docker-compose --version
```

#### 1.1.2 安装 Git (可选)

下载地址: https://git-scm.com/download/win

#### 1.1.3 获取 DeepSeek API Key

1. 访问 https://platform.deepseek.com/
2. 注册/登录账号
3. 进入 Console -> API Keys -> 创建 API Key
4. 复制 Key 备用 (格式: sk-xxxxxxxxxx)

#### 1.1.4 准备 QQ 账号

1. 准备一个 QQ 账号作为机器人账号
2. 建议使用新注册的账号，避免影响主账号
3. 确保账号已绑定手机和邮箱

---

## 二、部署步骤

### 2.1 下载项目代码

打开 PowerShell 或 Git Bash:

```powershell
# 方式1: 如果已安装Git
git clone <项目仓库地址>
cd qq-bot-admin

# 方式2: 直接下载ZIP后解压
# 下载项目ZIP后解压到任意目录
```

### 2.2 配置环境变量

在项目根目录创建 `.env` 文件:

```powershell
# 进入项目目录
cd qq-bot-admin

# 创建.env文件
copy .env.example .env
```

编辑 `.env` 文件，填写以下配置:

```env
# ============ 必填配置 ============

# 数据库密码 (自定义，推荐复杂密码)
DB_PASSWORD=YourSecurePassword123!

# JWT密钥 (自定义，至少32位)
JWT_SECRET=your_jwt_secret_key_at_least_32_characters_long

# DeepSeek API Key (从 https://platform.deepseek.com 获取)
DEEPSEEK_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxx

# ============ QQ 机器人配置 ============

# 机器人 QQ 号
BOT_QQ_NUMBER=123456789

# 机器人 QQ 密码
BOT_QQ_PASSWORD=your_qq_password
```

### 2.3 启动服务

#### 方式一: 使用 Docker Compose (推荐)

```powershell
# 确保Docker Desktop已启动

# 在项目根目录执行
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f
```

#### 方式二: 分步启动

```powershell
# 1. 启动数据库和缓存
docker-compose up -d postgres redis

# 2. 启动 NapCatQQ
docker-compose up -d napcat

# 3. 启动后端
docker-compose up -d backend

# 4. 启动前端
docker-compose up -d frontend

# 5. 启动机器人
docker-compose up -d bot
```

### 2.4 首次登录 NapCatQQ

1. 等待 NapCatQQ 服务启动
2. 访问 NapCat WebUI: http://localhost:3003
3. 使用机器人 QQ 账号扫码或密码登录
4. 登录成功后即可开始使用

### 2.5 访问服务

启动成功后，浏览器访问:

| 服务 | 地址 | 说明 |
|------|------|------|
| 前端管理界面 | http://localhost:3000 | Web后台管理 |
| API文档 | http://localhost:8000/docs | Swagger API文档 |
| API健康检查 | http://localhost:8000/health | 检查后端状态 |
| NapCat WebUI | http://localhost:3003 | QQ 登录管理 |

**默认账号:** `admin` / `admin123`

---

## 三、配置说明

### 3.1 NapCatQQ 配置

编辑 `napcat/config/napcat.json`:

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
    "uin": "你的QQ号",
    "password": "你的QQ密码",
    "protocol": "mac"
  }
}
```

### 3.2 NoneBot2 配置

编辑 `bot/.env`:

```env
DRIVER=~httpx+~websockets
COMMAND_START=[""]
NAPCAT_HTTP_URL=http://napcat:3001
NAPCAT_WS_URL=ws://napcat:3002
```

### 3.3 重新启动机器人

```powershell
# 重启bot服务
docker-compose restart bot

# 查看日志确认登录状态
docker-compose logs -f bot
```

---

## 四、验证机器人功能

### 4.1 私聊测试

1. 在 QQ 中找到机器人账号
2. 发送任意消息
3. **白名单用户**: 会收到AI回复
4. **非白名单用户**: 收到权限拒绝提示

### 4.2 群聊测试

1. 让白名单用户邀请机器人加入群聊
2. 在群内 @机器人 + 问题
3. 机器人会回复AI答案

### 4.3 后台验证

1. 访问 http://localhost:3000
2. 登录后进入 "群组管理"
3. 应能看到机器人所在的群聊
4. 进入 "消息管理" 应能看到聊天记录

---

## 五、常见问题

### 5.1 Docker 启动失败

**问题:** `Docker Desktop is not running`

**解决:**
1. 启动 Docker Desktop 应用
2. 等待托盘图标变绿色
3. 重试命令

### 5.2 端口被占用

**问题:** `port is already allocated`

**解决:**
```powershell
# 查找占用端口的进程
netstat -ano | findstr ":3001"
netstat -ano | findstr ":8000"

# 结束进程或修改docker-compose.yml中的端口
```

### 5.3 QQ 登录失败

**问题:** NapCatQQ 无法登录

**解决:**
1. 确保 QQ 账号密码正确
2. 检查是否需要验证（扫码登录更稳定）
3. 确保账号没有异常封禁
4. 尝试使用不同的协议（mac/windows）
5. 查看 NapCat 日志: `docker-compose logs napcat`

### 5.4 AI 功能不工作

**问题:** 机器人不回复或回复"AI服务暂不可用"

**解决:**
1. 检查 `.env` 中 `DEEPSEEK_API_KEY` 是否正确
2. 检查 DeepSeek 账户余额/配额
3. 查看后端日志: `docker-compose logs backend`

### 5.5 数据库连接失败

**问题:** 后端启动报错数据库连接失败

**解决:**
```powershell
# 确保postgres服务运行中
docker-compose ps postgres

# 重启数据库
docker-compose restart postgres

# 查看数据库日志
docker-compose logs postgres
```

---

## 六、停止和清理

### 停止服务

```powershell
# 停止所有服务
docker-compose down

# 停止并删除数据卷 (会清除所有数据)
docker-compose down -v
```

### 完全清理

```powershell
# 删除所有容器、网络、镜像
docker-compose down --rmi all -v

# 删除下载的镜像
docker system prune -a
```

---

## 七、性能优化 (可选)

### 7.1 修改 AI 响应参数

编辑 `backend/app/services/ai_service.py`:

```python
temperature: 0.7,  # 0-1，越低越稳定
max_tokens: 2000,  # 最大回复长度
```

### 7.2 调整消息缓存时间

编辑 `bot/src/utils/config.py`:

```python
MESSAGE_CACHE_TTL: int = 120  # 缓存秒数，默认2分钟
```

### 7.3 修改上下文轮数

```python
AI_CONTEXT_GROUP: int = 10    # 群聊保留10轮
AI_CONTEXT_PRIVATE: int = 20  # 私聊保留20轮
```

---

## 八、联系与支持

- 项目文档: 查看 `README.md`
- 技术问题: 查看 `SPEC.md`
- API调试: http://localhost:8000/docs

祝部署顺利！
