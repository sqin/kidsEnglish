# 儿童英语学习应用部署教程

## 🚀 方案一：Vercel（前端）+ Railway（后端）- 最简单

### 前置准备
- GitHub账号：https://github.com
- Vercel账号：https://vercel.com（可用GitHub登录）
- Railway账号：https://railway.app（可用GitHub登录）

---

## 第一步：准备代码仓库

### 1.1 推送代码到GitHub

```bash
# 在项目根目录
cd /Users/linshengqin/Documents/Code/kidsEnglish

# 初始化Git（如果尚未初始化）
git init

# 添加所有文件
git add .

# 提交
git commit -m "Initial commit"

# 创建GitHub仓库（https://github.com/new）
# 然后关联远程仓库
git remote add origin https://github.com/YOUR_USERNAME/kids-english-app.git

# 推送
git push -u origin main
```

### 1.2 配置后端环境变量

创建 `backend/.env` 文件：
```bash
# 复制示例文件
cd backend
cp .env.example .env

# 编辑.env文件
nano .env
```

内容：
```env
DATABASE_URL=postgresql://postgres:password@localhost:5432/kids_english
SECRET_KEY=your-super-secret-jwt-key-change-this-in-production
# 可选：阿里云语音服务
ALIYUN_ACCESS_KEY_ID=your_key_id
ALIYUN_ACCESS_KEY_SECRET=your_key_secret
ALIYUN_APP_KEY=your_app_key
```

---

## 第二步：部署后端（Railway）

### 2.1 创建Railway项目

1. 访问 https://railway.app
2. 点击 "New Project"
3. 选择 "Deploy from GitHub repo"
4. 选择您的 `kids-english-app` 仓库
5. 选择backend文件夹

### 2.2 配置Railway

**2.2.1 添加PostgreSQL插件**
- 在Railway项目控制台，点击 "New" → "Database" → "Add PostgreSQL"
- 复制生成的 `DATABASE_URL`

**2.2.2 设置环境变量**
在Railway控制台 → Variables页面，添加：
```
DATABASE_URL=postgresql://postgres:xxxxx@xxxxx:xxxx/railway
SECRET_KEY=your-super-secret-jwt-key-$(openssl rand -hex 32)
NODE_ENV=production
PORT=20000
```

**2.2.3 配置构建设置**
Railway会自动检测到是Python项目，确保：
- Build Command: `pip install -r requirements.txt`
- Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

**2.2.4 创建requirements.txt**
在backend目录创建 `requirements.txt`：
```txt
fastapi==0.104.1
uvicorn[standard]==0.24.0
sqlalchemy[asyncio]==2.0.23
asyncpg==0.29.0
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6
pydantic==2.5.0
python-dotenv==1.0.0
```

### 2.3 部署并获取API地址

1. 点击 "Deploy" 按钮
2. 等待构建完成（5-10分钟）
3. 在Settings → Domains 获取您的API地址：
   - 例如：`https://kids-english-backend-production.up.railway.app`
4. 测试API：`https://kids-english-backend-production.up.railway.app/api/letters`

---

## 第三步：部署前端（Vercel）

### 3.1 创建Vercel项目

1. 访问 https://vercel.com
2. 点击 "New Project"
3. 从GitHub导入 `kids-english-app` 仓库
4. 选择frontend文件夹

### 3.2 配置构建设置

**3.2.1 基本配置**
- Framework Preset: `Vite`
- Root Directory: `frontend`
- Build Command: `npm run build`
- Output Directory: `dist`
- Install Command: `npm install`

**3.2.2 环境变量**
在Vercel控制台 → Settings → Environment Variables，添加：
```
VITE_API_URL=https://kids-english-backend-production.up.railway.app/api
VITE_APP_TITLE=儿童英语学习
NODE_ENV=production
```

### 3.3 配置API地址

**3.3.1 修改前端API配置**
检查并修改 `frontend/src/api/` 下的文件：

例如 `frontend/src/api/auth.js`：
```javascript
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:20000/api';

export const authAPI = {
  login: (data) => http.post('/auth/login', data),
  register: (data) => http.post('/auth/register', data),
  getCurrentUser: () => http.get('/auth/me'),
};

// 修改http配置
const http = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});
```

**3.3.2 更新CORS设置**
在Railway后端，添加Vercel域名到CORS允许列表：

创建 `backend/app/main.py` 调整：
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# 获取允许的域名（从环境变量）
ALLOWED_ORIGINS = [
    "http://localhost:30002",
    "https://your-app.vercel.app",  # 替换为实际Vercel域名
    "https://kids-english-backend-production.up.railway.app",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 3.4 部署前端

1. 点击 "Deploy" 按钮
2. 等待构建完成（3-5分钟）
3. 获取部署URL，例如：`https://kids-english-app-abc123.vercel.app`
4. 访问该URL测试应用

---

## 第四步：配置自定义域名（可选）

### 4.1 在Vercel添加自定义域名

1. Vercel控制台 → Settings → Domains
2. 添加您的域名（如：`kids.yourdomain.com`）
3. 按提示配置DNS记录：
   ```
   类型: CNAME
   名称: kids
   值: cname.vercel-dns.com
   ```

### 4.2 在Railway添加自定义域名

1. Railway控制台 → Settings → Domains
2. 添加域名（如：`api.yourdomain.com`）
3. 配置DNS：
   ```
   类型: CNAME
   名称: api
   值: your-app.railway.app
   ```

### 4.3 更新环境变量

部署完成后，更新：
- Vercel环境变量：`VITE_API_URL=https://api.yourdomain.com/api`
- Railway CORS设置：添加 `https://kids.yourdomain.com`

---

## 🎯 方案二：VPS完整部署

### 服务器要求
- **配置**：1核1GB内存（最低）
- **系统**：Ubuntu 22.04 LTS
- **服务商**：DigitalOcean、Linode、Vultr等

### 部署步骤

#### 1. 服务器初始化

```bash
# 连接到服务器
ssh root@YOUR_SERVER_IP

# 更新系统
apt update && apt upgrade -y

# 安装必要工具
apt install -y nginx certbot python3-certbot-nginx git

# 安装Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# 安装Docker Compose
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose
```

#### 2. 配置防火墙

```bash
# 启用ufw
ufw enable

# 开放必要端口
ufw allow 22
ufw allow 80
ufw allow 443

# 检查状态
ufw status
```

#### 3. 部署应用

**3.1 创建项目目录**
```bash
mkdir -p /var/www/kids-english
cd /var/www/kids-english

# 克隆代码
git clone https://github.com/YOUR_USERNAME/kids-english-app.git .
```

**3.2 创建docker-compose.yml**
```yaml
version: '3.8'

services:
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    ports:
      - "3000:80"
    depends_on:
      - backend

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    ports:
      - "20000:20000"
    environment:
      - DATABASE_URL=postgresql://postgres:password@db:5432/kids_english
      - SECRET_KEY=${SECRET_KEY}
    depends_on:
      - db

  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=kids_english
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

volumes:
  postgres_data:
```

**3.3 创建Dockerfile**

前端 `frontend/Dockerfile`：
```dockerfile
FROM node:18-alpine as build
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

前端 `frontend/nginx.conf`：
```nginx
server {
    listen 80;
    server_name _;
    root /usr/share/nginx/html;
    index index.html;

    location /api {
        proxy_pass http://backend:20000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location / {
        try_files $uri $uri/ /index.html;
    }
}
```

后端 `backend/Dockerfile`：
```dockerfile
FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 20000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "20000"]
```

#### 4. 启动服务

```bash
# 创建.env文件
cp backend/.env.example backend/.env
nano backend/.env

# 启动所有服务
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

#### 5. 配置Nginx反向代理

创建 `/etc/nginx/sites-available/kids-english`：
```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

    location /api {
        proxy_pass http://localhost:20000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

启用配置：
```bash
ln -s /etc/nginx/sites-available/kids-english /etc/nginx/sites-enabled/
nginx -t
systemctl reload nginx
```

#### 6. 申请SSL证书

```bash
# 使用Let's Encrypt
certbot --nginx -d yourdomain.com -d www.yourdomain.com

# 自动续期
echo "0 12 * * * /usr/bin/certbot renew --quiet" | crontab -
```

---

## 📊 监控与维护

### 检查服务状态

```bash
# 检查Docker容器
docker-compose ps

# 查看日志
docker-compose logs backend
docker-compose logs frontend

# 重启服务
docker-compose restart
```

### 备份数据库

```bash
# 备份
docker-compose exec db pg_dump -U postgres kids_english > backup.sql

# 恢复
docker-compose exec -T db psql -U postgres kids_english < backup.sql
```

### 更新代码

```bash
# 拉取最新代码
git pull origin main

# 重新构建并启动
docker-compose down
docker-compose up -d --build
```

---

## ✅ 部署检查清单

- [ ] 代码推送到GitHub
- [ ] 后端部署到Railway
- [ ] PostgreSQL数据库创建
- [ ] 环境变量配置正确
- [ ] 前端部署到Vercel
- [ ] API地址配置正确
- [ ] CORS设置正确
- [ ] 应用可以正常注册/登录
- [ ] 学习功能正常工作
- [ ] 语音录制功能测试通过
- [ ] （可选）自定义域名配置
- [ ] （可选）SSL证书配置

---

## 🆘 常见问题解决

### 问题1：前端API请求失败
**解决方案**：
```bash
# 检查环境变量是否正确
echo $VITE_API_URL

# 确认CORS设置包含前端域名
# 在backend/main.py中添加：
"https://your-frontend-domain.vercel.app"
```

### 问题2：数据库连接失败
**解决方案**：
```bash
# 检查Railway数据库状态
# 确认DATABASE_URL格式正确
postgresql://user:password@host:port/database
```

### 问题3：构建失败
**解决方案**：
```bash
# 检查Node.js版本（Vercel默认18）
node --version

# 检查Python版本（Railway默认3.11）
python --version

# 清除缓存重新部署
```

---

## 💰 成本对比

| 方案 | 月成本 | 优势 | 劣势 |
|------|--------|------|------|
| Vercel + Railway | $0 | 免费额度，自动扩展 | 有冷启动 |
| VPS | $5-10 | 完全控制，无冷启动 | 需要维护 |
| 云服务商全托管 | $20+ | 稳定可靠 | 成本较高 |

---

## 🎉 完成！

恭喜！您的儿童英语学习应用已经部署上线。

**访问地址**：
- 前端：https://your-app.vercel.app
- 后端API：https://your-backend.railway.app
- API文档：https://your-backend.railway.app/docs

您现在可以：
1. 分享给朋友测试
2. 添加更多功能
3. 推广给目标用户

如有问题，请检查：
1. 浏览器控制台错误信息
2. 后端日志：`railway logs`
3. 前端构建日志：Vercel部署页面

祝您使用愉快！🎈
