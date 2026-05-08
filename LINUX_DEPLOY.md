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

#### 1.1.4 准备 QQ 账号

1. 准备一个 QQ 账号作为机器人账号
2. 建议使用新注册的账号，避免影响主账号
3. 确保账号已绑定手机和邮箱

---

## 二、部署步骤

### 2.1 下载项目代码

```bash
# 克隆项目
git clone <项目仓库地址>
cd qq-bot-admin

# 或者直接下载 ZIP 后解压
# wget <项目ZIP地址>
# unzip main.zip
# cd qq-bot-admin
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

# ============ QQ 机器人配置 ============

# 机器人 QQ 号
BOT_QQ_NUMBER=123456789

# 机器人 QQ 密码
BOT_QQ_PASSWORD=your_qq_password

# NapCatQQ 配置 (通常不需要修改)
NAPCAT_HTTP_URL=http://napcat:3001
NAPCAT_WS_URL=ws://napcat:3002
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
docker compose logs -f napcat
```

#### 方式二: 分步启动

```bash
# 1. 启动数据库和缓存
docker compose up -d postgres redis

# 2. 启动 NapCatQQ
docker compose up -d napcat

# 3. 启动后端
docker compose up -d backend

# 4. 启动前端
docker compose up -d frontend

# 5. 启动 NoneBot2 机器人
docker compose up -d bot
```

### 2.4 首次登录 NapCatQQ

1. 等待 NapCatQQ 服务启动
2. 访问 NapCat WebUI: http://服务器IP:3003
3. 使用机器人 QQ 账号扫码或密码登录
4. 登录成功后即可开始使用

### 2.5 配置防火墙

如果服务器开启了防火墙，需要开放以下端口:

```bash
# Ubuntu (ufw)
sudo ufw allow 3000/tcp  # NapCat WebUI
sudo ufw allow 3001/tcp  # NapCat HTTP
sudo ufw allow 3002/tcp  # NapCat WebSocket
sudo ufw allow 3003/tcp  # NapCat WebUI (可选)
sudo ufw allow 3000/tcp  # 前端
sudo ufw allow 8000/tcp  # 后端 API
sudo ufw reload

# CentOS (firewalld)
sudo firewall-cmd --permanent --add-port=3000-3003/tcp
sudo firewall-cmd --permanent --add-port=3000/tcp
sudo firewall-cmd --permanent --add-port=8000/tcp
sudo firewall-cmd --reload
```

### 2.6 访问服务

启动成功后，通过浏览器访问:

| 服务 | 地址 | 说明 |
|------|------|------|
| 前端管理界面 | http://服务器IP:3000 | Web后台管理 |
| API文档 | http://服务器IP:8000/docs | Swagger API文档 |
| API健康检查 | http://服务器IP:8000/health | 检查后端状态 |
| NapCat WebUI | http://服务器IP:3003 | QQ 登录管理 |

**默认账号:** `admin` / `admin123`

---

## 三、配置 NoneBot2 与 NapCatQQ 连接

### 3.1 配置 NoneBot2

编辑 `bot/.env` 文件:

```env
# NoneBot2 配置
DRIVER=~httpx+~websockets
COMMAND_START=[""]

# NapCatQQ 连接配置
NAPCAT_HTTP_URL=http://napcat:3001
NAPCAT_WS_URL=ws://napcat:3002
NAPCAT_ACCESS_TOKEN=
```

### 3.2 配置 NapCatQQ

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

### 3.3 验证连接

```bash
# 查看 NapCat 日志
docker compose logs -f napcat

# 查看 NoneBot2 日志
docker compose logs -f bot
```

---

## 四、使用系统服务管理机器人 (生产环境推荐)

创建 systemd 服务文件，确保机器人开机自启:

```bash
sudo nano /etc/systemd/system/qq-bot.service
```

写入以下内容:

```ini
[Unit]
Description=QQ Bot Service
Requires=docker.service
After=docker.service network.target

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/path/to/qq-bot-admin
ExecStart=/usr/bin/docker compose up -d
ExecStop=/usr/bin/docker compose stop
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
sudo systemctl enable qq-bot

# 启动服务
sudo systemctl start qq-bot

# 查看状态
sudo systemctl status qq-bot

# 查看日志
sudo journalctl -u qq-bot -f
```

---

## 五、配置 Nginx 反向代理 (可选，生产环境推荐)

### 5.1 安装 Nginx

```bash
# Ubuntu / Debian
sudo apt install -y nginx

# CentOS / RHEL
sudo yum install -y nginx
```

### 5.2 配置反向代理

```bash
sudo nano /etc/nginx/sites-available/qq-bot
```

写入以下配置:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    # 前端
    location / {
        proxy_pass http://127.0.0.1:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # 后端 API
    location /api {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # NapCat WebUI
    location /napcat {
        proxy_pass http://127.0.0.1:3003;
        proxy_set_header Host $host;
    }
}
```

启用配置:

```bash
# Ubuntu / Debian
sudo ln -s /etc/nginx/sites-available/qq-bot /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx

# CentOS / RHEL
sudo mv qq-bot /etc/nginx/conf.d/
sudo nginx -t
sudo systemctl reload nginx
```

### 5.3 配置 HTTPS (使用 Let's Encrypt)

```bash
# 安装 certbot
sudo apt install -y certbot python3-certbot-nginx

# 获取证书
sudo certbot --nginx -d your-domain.com

# 自动续期测试
sudo certbot renew --dry-run
```

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
sudo lsof -i :3001
sudo lsof -i :8000

# 结束进程或修改 docker-compose.yml 中的端口
```

### 6.3 QQ 登录失败

**问题:** NapCatQQ 无法登录

**解决:**
1. 确保 QQ 账号密码正确
2. 检查是否需要验证（扫码登录更稳定）
3. 确保账号没有异常封禁
4. 尝试使用不同的协议（mac/windows）
5. 查看 NapCat 日志: `docker compose logs napcat`

### 6.4 AI 功能不工作

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

# 完全清理
docker system prune -a --volumes
```

---

## 八、数据备份

### 8.1 备份数据库

```bash
# 创建备份目录
mkdir -p ~/backups

# 备份 PostgreSQL
docker compose exec -T postgres pg_dump -U bot_admin qq_bot > ~/backups/qq_bot_$(date +%Y%m%d_%H%M%S).sql

# 或压缩备份
docker compose exec -T postgres pg_dump -U bot_admin qq_bot | gzip > ~/backups/qq_bot_$(date +%Y%m%d).sql.gz
```

### 8.2 恢复数据库

```bash
# 停止服务
docker compose stop backend bot

# 恢复数据
gunzip < ~/backups/qq_bot_20240101.sql.gz | docker compose exec -T postgres psql -U bot_admin qq_bot

# 重启服务
docker compose start backend bot
```

### 8.3 自动备份脚本

创建定时备份脚本 `/opt/scripts/backup.sh`:

```bash
#!/bin/bash
BACKUP_DIR="/opt/backups"
DATE=$(date +%Y%m%d_%H%M%S)
CONTAINER_NAME="qq_bot_postgres"
DB_NAME="qq_bot"
DB_USER="bot_admin"

mkdir -p $BACKUP_DIR

docker compose exec -T $CONTAINER_NAME pg_dump -U $DB_USER $DB_NAME | gzip > $BACKUP_DIR/qq_bot_$DATE.sql.gz

# 保留最近 30 天备份
find $BACKUP_DIR -name "qq_bot_*.sql.gz" -mtime +30 -delete

echo "Backup completed: $DATE"
```

添加定时任务:

```bash
chmod +x /opt/scripts/backup.sh
echo "0 3 * * * /opt/scripts/backup.sh" | sudo tee /etc/cron.d/qq-bot-backup
```

---

## 九、联系与支持

- 项目文档: 查看 `README.md`
- 技术问题: 查看 `SPEC.md`
- API调试: http://localhost:8000/docs

祝部署顺利！
