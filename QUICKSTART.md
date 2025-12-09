# 快速启动指南

## 当前状态
✅ **前端**: http://localhost:30002 (运行中)
✅ **后端**: http://localhost:20000 (需手动启动)
✅ **数据库**: PostgreSQL (需本地安装)

## 启动步骤

### 1. 启动后端
```bash
cd backend

# 确保已安装uv (https://docs.astral.sh/uv/getting-started/installation/)

# 配置数据库连接
cp .env.example .env
# 编辑 .env 文件，设置 DATABASE_URL（使用 postgresql+asyncpg:// 前缀）

# 创建数据库
# 在PostgreSQL中执行: CREATE DATABASE kids_english;

# 启动开发服务器 (两种方式)
# 方式1: 使用启动脚本
./start.sh

# 方式2: 直接使用uv运行
uv run uvicorn app.main:app --host 0.0.0.0 --port 20000 --reload
```

### 2. 访问应用
- **前端**: http://localhost:30002
- **API文档**: http://localhost:20000/docs

## 功能流程

### 注册/登录
1. 首次访问会自动跳转到登录页
2. 点击"注册"创建新账户
3. 登录后进入首页

### 学习流程
1. **首页**: 点击字母卡片开始学习
2. **学习页**: 点击"听发音"听标准读音，然后点击"跟读"
3. **录音页**: 按住麦克风按钮录音，松开后自动评分
4. **获得星星**: 根据评分获得1-3颗星
5. **成就页**: 查看学习统计和成就徽章

## 技术实现

### 前端 (Vue 3)
- 状态管理: Pinia
- 路由: Vue Router (含登录守卫)
- 动画: GSAP
- HTTP: Axios (自动携带JWT token)

### 后端 (FastAPI)
- 认证: JWT
- 数据库: PostgreSQL + SQLAlchemy
- API文档: 自动生成 (/docs)
- 语音评分: 模拟实现 (预留阿里云接口)

## API接口

### 认证
- `POST /api/auth/register` - 用户注册
- `POST /api/auth/login` - 用户登录
- `GET /api/auth/me` - 获取当前用户

### 学习进度
- `GET /api/progress/` - 获取进度
- `POST /api/progress/update` - 更新进度
- `POST /api/progress/checkin` - 打卡
- `GET /api/progress/stats` - 统计信息

### 语音评分
- `POST /api/speech/evaluate` - 语音评分

## 待完善

1. **语音评分API**: 接入阿里云或讯飞的真实API
2. **动画素材**: 添加更多Lottie动画
3. **音频资源**: 准备26个字母的标准发音
4. **练习游戏**: 添加字母匹配等互动游戏
5. **进度同步**: 学习进度实时同步到后端
