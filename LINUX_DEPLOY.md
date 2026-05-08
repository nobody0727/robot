# Linux 服务器部署指南

## 一、环境准备

### 1.1 安装必需软件

#### 1.1.1 安装 Docker

**Ubuntu / Debian:**

```bash
# 更新软件源
sudo apt update

# 安装必要组件
sudo apt install -y apt-transport-https ca-certificates curl software-properties-common

# 添加 Docker GPG 密钥
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# 添加 Docker 仓库
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# 安装 Docker
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# 将当前用户加入 docker 用户组（免 sudo）
sudo usermod -aG docker $USER

# 重新登录后生效，或执行：
newgrp docker
```

**CentOS / RHEL:**

```bash
sudo yum install -y yum-utils
sudo yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
sudo yum install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker $USER
```

**验证安装:**

```bash
docker --version
docker compose version
```

#### 1.1.2 安装 Git

```bash
# Ubuntu / Debian
sudo apt install -y git

# CentOS / RHEL
sudo yum install -y git

# 验证
git --version
```

#### 1.1.3 获取 DeepSeek API Key

1. 访问 https://platform.deepseek.com/
2. 注册/登录账号
3. 进入 Console -> API Keys -> 创建 API Key
4. 复制 Key 备用 (格式: sk-xxxxxxxxxx)

#### 1.1.4 获取 Wechaty Token (可选，用于生产环境)

推荐使用 Paimon 协议（个人微信）或 WorkPro 协议（企业微信）：

**Paimon（个人微信）：**
1. 访问 http://120.55.60.194/ 注册获取免费 Token
2. 或访问 https://wechaty.js.org/docs/puppet-services/paimon 了解更多

**WorkPro（企业微信）：**
1. 联系客服获取 Token：https://wechaty.js.org/assets/files/workpro-doc-qrcode-45e1720a5cf2846d7e8a930f2ceda310.webp

**Token 服务平台（购买/续费）：**
- 访问 https://token.rpachat.com/

> ⚠️ 注意：Donut 协议已于 2025 年停止服务，请使用 Paimon 或 WorkPro 替代。

---

## 二、部署步骤

### 2.1 下载项目代码

```bash
# 克隆项目
git clone <项目仓库地址>
cd wechat-bot-admin

# 或者直接下载 ZIP 后解压
# wget <项目ZIP地址>
# unzip main.zip
# cd wechat-bot-admin
```

### 2.2 配置环境变量

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑 .env 文件
nano .env
# 或使用 vim
vim .env
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

# ============ 可选配置 ============

# Wechaty Token (使用Paimon协议)
WECHATY_TOKEN=your_paimon_token

# Wechaty协议类型
WECHATY_PUPPET=wechaty-puppet-paimon

# 服务地址
BACKEND_URL=http://localhost:8000
FRONTEND_URL=http://localhost:3000
```

### 2.3 启动服务

#### 方式一: 使用 Docker Compose (推荐)

```bash
# 在项目根目录执行
docker compose up -d

# 查看服务状态
docker compose ps

# 查看所有服务日志
docker compose logs -f

# 查看特定服务日志
docker compose logs -f backend
```

#### 方式二: 分步启动

```bash
# 1. 启动数据库和缓存
docker compose up -d postgres redis

# 2. 启动后端
docker compose up -d backend

# 3. 启动前端
docker compose up -d frontend

# 4. 启动机器人 (需要微信扫码)
docker compose up -d bot
```

### 2.4 配置防火墙

如果服务器开启了防火墙，需要开放以下端口:

```bash
# Ubuntu (ufw)
sudo ufw allow 3000/tcp  # 前端
sudo ufw allow 8000/tcp  # 后端 API
sudo ufw reload

# CentOS (firewalld)
sudo firewall-cmd --permanent --add-port=3000/tcp
sudo firewall-cmd --permanent --add-port=8000/tcp
sudo firewall-cmd --reload
```

### 2.5 访问服务

启动成功后，通过浏览器访问:

| 服务 | 地址 | 说明 |
|------|------|------|
| 前端管理界面 | http://服务器IP:3000 | Web后台管理 |
| API文档 | http://服务器IP:8000/docs | Swagger API文档 |
| API健康检查 | http://服务器IP:8000/health | 检查后端状态 |

**默认账号:** `admin` / `admin123`

---

## 三、绑定微信账号为机器人

### 3.1 方案一: 使用 Paimon 协议 (推荐，用于个人微信)

#### 步骤1: 获取 Paimon Token

1. 访问 http://120.55.60.194/ 注册获取免费 Token
2. 或联系 Token 服务：https://token.rpachat.com/

#### 步骤2: 配置 Token

编辑 `.env` 文件:

```env
WECHATY_TOKEN=your_paimon_token_here
WECHATY_PUPPET=wechaty-puppet-paimon
```

#### 步骤3: 重新启动机器人

```bash
# 重启 bot 服务
docker compose restart bot

# 查看日志确认登录状态
docker compose logs -f bot
```

#### 步骤4: 扫码登录

首次启动时，机器人需要微信扫码授权:

1. 查看 Docker 日志获取二维码:
```bash
docker compose logs bot
```

2. 会看到类似输出:
```
[Wechaty] 📢 登录二维码:
https://qrlogin.wechat.com/qrcode/xxxxx
```

3. 用微信扫描二维码确认登录

4. 登录成功后，日志显示:
```
[Wechaty] ✅ 已登录，昵称: 你的微信昵称
```

---

### 3.2 方案二: 使用 WorkPro 协议 (企业微信)

适用于企业微信账号:

```env
WECHATY_PUPPET=wechaty-puppet-workpro
WECHATY_TOKEN=your_workpro_token
```

---

### 3.3 使用系统服务管理机器人 (生产环境推荐)

创建 systemd 服务文件，确保机器人开机自启:

```bash
sudo nano /etc/systemd/system/wechat-bot.service
```

写入以下内容:

```ini
[Unit]
Description=Wechaty Bot Service
Requires=docker.service
After=docker.service network.target

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/path/to/wechat-bot-admin
ExecStart=/usr/bin/docker compose up -d bot
ExecStop=/usr/bin/docker compose stop bot
ExecReload=/usr/bin/docker compose restart bot
User=your_user
Group=docker

[Install]
WantedBy=multi-user.target
```

启用服务:

```bash
# 重载 systemd 配置
sudo systemctl daemon-reload

# 启用服务（开机自启）
sudo systemctl enable wechat-bot

# 启动服务
sudo systemctl start wechat-bot

# 查看状态
sudo systemctl status wechat-bot

# 查看日志
sudo journalctl -u wechat-bot -f
```

---

## 四、配置 Nginx 反向代理 (可选，生产环境推荐)

### 4.1 安装 Nginx

```bash
# Ubuntu / Debian
sudo apt install -y nginx

# CentOS / RHEL
sudo yum install -y nginx
```

### 4.2 配置反向代理

```bash
sudo nano /etc/nginx/sites-available/wechat-bot
```

写入以下配置:

```nginx
server {
    listen 80;
    server_name your-domain.com;  # 替换为你的域名

    # 前端
    location / {
        proxy_pass http://127.0.0.1:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # 后端 API
    location /api {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # WebSocket 支持 (如需要)
    location /ws {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
    }
}
```

启用配置:

```bash
# Ubuntu / Debian
sudo ln -s /etc/nginx/sites-available/wechat-bot /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx

# CentOS / RHEL
sudo mv /etc/nginx/conf.d/default.conf /etc/nginx/conf.d/default.conf.bak
sudo mv wechat-bot /etc/nginx/conf.d/
sudo nginx -t
sudo systemctl reload nginx
```

### 4.3 配置 HTTPS (使用 Let's Encrypt)

```bash
# 安装 certbot
sudo apt install -y certbot python3-certbot-nginx

# 获取证书
sudo certbot --nginx -d your-domain.com

# 自动续期测试
sudo certbot renew --dry-run
```

---

## 五、验证机器人功能

### 5.1 私聊测试

1. 在微信中找到机器人 (搜索微信号或扫码)
2. 发送任意消息
3. **白名单用户**: 会收到AI回复
4. **非白名单用户**: 收到权限拒绝提示

### 5.2 群聊测试

1. 让白名单用户邀请机器人加入群聊
2. 在群内 @机器人 + 问题
3. 机器人会回复AI答案

### 5.3 后台验证

1. 访问 http://服务器IP:3000
2. 登录后进入 "群组管理"
3. 应能看到机器人所在的群聊
4. 进入 "消息管理" 应能看到聊天记录

---

## 六、常见问题

### 6.1 Docker 启动失败

**问题:** `Cannot connect to the Docker daemon`

**解决:**
```bash
# 确保 Docker 服务正在运行
sudo systemctl start docker
sudo systemctl enable docker

# 当前用户是否在 docker 组
groups $USER
# 如果没有，执行
sudo usermod -aG docker $USER
# 然后重新登录
```

### 6.2 端口被占用

**问题:** `port is already allocated`

**解决:**
```bash
# 查找占用端口的进程
sudo lsof -i :3000
sudo lsof -i :8000

# 或使用 netstat
sudo netstat -tlnp | grep 3000

# 结束进程或修改 docker-compose.yml 中的端口
```

### 6.3 微信扫码登录失败

**问题:** 二维码无法扫描或扫描后提示登录异常

**解决:**
1. 确保微信账号已实名认证
2. 检查是否被微信限制登录
3. 尝试更换网络环境
4. 确认 Paimon Token 有效
5. 检查服务器时间是否正确: `timedatectl`

### 6.4 AI功能不工作

**问题:** 机器人不回复或回复"AI服务暂不可用"

**解决:**
```bash
# 检查 .env 中 DEEPSEEK_API_KEY 是否正确
grep DEEPSEEK .env

# 检查后端日志
docker compose logs backend

# 测试 API Key 是否有效
curl -X POST https://api.deepseek.com/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -d '{"model": "deepseek-chat", "messages": [{"role": "user", "content": "test"}]}'
```

### 6.5 数据库连接失败

**问题:** 后端启动报错数据库连接失败

**解决:**
```bash
# 确保 postgres 服务运行中
docker compose ps postgres

# 重启数据库
docker compose restart postgres

# 查看数据库日志
docker compose logs postgres
```

---

## 七、停止和清理

### 停止服务

```bash
# 停止所有服务
docker compose down

# 停止并删除数据卷 (会清除所有数据)
docker compose down -v
```

### 完全清理

```bash
# 删除所有容器、网络、镜像
docker compose down --rmi all -v

# 删除未使用的镜像和容器
docker system prune -a

# 完全清理（包括所有未使用的镜像、容器、网络）
docker system prune -a --volumes
```

---

## 八、性能优化 (可选)

### 8.1 修改 AI 响应参数

编辑 `backend/app/services/ai_service.py`:

```python
temperature: 0.7,  # 0-1，越低越稳定
max_tokens: 2000,  # 最大回复长度
```

### 8.2 调整消息缓存时间

编辑 `bot/src/config.py`:

```python
MESSAGE_CACHE_TTL: int = 120  # 缓存秒数，默认2分钟
```

### 8.3 修改上下文轮数

```python
AI_CONTEXT_GROUP: int = 10    # 群聊保留10轮
AI_CONTEXT_PRIVATE: int = 20  # 私聊保留20轮
```

### 8.4 调整 Docker 资源限制

编辑 `docker-compose.yml` 为数据库等服务添加资源限制:

```yaml
services:
  postgres:
    # ... 其他配置
    deploy:
      resources:
        limits:
          memory: 512M
        reservations:
          memory: 256M
```

---

## 九、数据备份

### 9.1 备份数据库

```bash
# 创建备份目录
mkdir -p ~/backups

# 备份 PostgreSQL
docker compose exec -T postgres pg_dump -U bot_admin wechat_bot > ~/backups/wechat_bot_$(date +%Y%m%d_%H%M%S).sql

# 或压缩备份
docker compose exec -T postgres pg_dump -U bot_admin wechat_bot | gzip > ~/backups/wechat_bot_$(date +%Y%m%d).sql.gz
```

### 9.2 恢复数据库

```bash
# 停止服务
docker compose stop backend bot

# 恢复数据
gunzip < ~/backups/wechat_bot_20240101.sql.gz | docker compose exec -T postgres psql -U bot_admin wechat_bot

# 重启服务
docker compose start backend bot
```

### 9.3 自动备份脚本

创建定时备份脚本 `/opt/scripts/backup.sh`:

```bash
#!/bin/bash
BACKUP_DIR="/opt/backups"
DATE=$(date +%Y%m%d_%H%M%S)
CONTAINER_NAME="wechat_bot_postgres"
DB_NAME="wechat_bot"
DB_USER="bot_admin"

mkdir -p $BACKUP_DIR

docker compose exec -T $CONTAINER_NAME pg_dump -U $DB_USER $DB_NAME | gzip > $BACKUP_DIR/wechat_bot_$DATE.sql.gz

# 保留最近 30 天备份
find $BACKUP_DIR -name "wechat_bot_*.sql.gz" -mtime +30 -delete

echo "Backup completed: $DATE"
```

添加定时任务:

```bash
chmod +x /opt/scripts/backup.sh

# 每天凌晨 3 点执行备份
echo "0 3 * * * /opt/scripts/backup.sh" | sudo tee /etc/cron.d/wechat-bot-backup
```

---

## 十、联系与支持

- 项目文档: 查看 `README.md`
- 技术问题: 查看 `SPEC.md`
- API调试: http://localhost:8000/docs

祝部署顺利！
