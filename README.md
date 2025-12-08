# 儿童英语字母学习 Web 应用

面向3-5岁学龄前儿童的英语字母学习打卡应用，包含动画互动和AI语音评分功能。

## 技术栈

- **前端**: Vue 3 + Vite + Pinia + Vue Router + GSAP
- **后端**: Python FastAPI + SQLAlchemy
- **数据库**: PostgreSQL

## 快速开始

### 前置要求
- Node.js 16+ 和 npm
- Python 3.9+
- PostgreSQL 12+（本地安装）

### 开发流程

#### 1. 启动数据库
确保本地PostgreSQL正在运行，并创建数据库：
```sql
CREATE DATABASE kids_english;
```

#### 2. 启动后端
```bash
cd backend

# 确保已安装uv (https://docs.astral.sh/uv/getting-started/installation/)

# 配置数据库连接
cp .env.example .env
# 编辑 .env 文件，配置数据库连接

# 启动开发服务器
uv run uvicorn app.main:app --host 0.0.0.0 --port 20000 --reload
```

#### 3. 启动前端
```bash
cd frontend
npm install
npm run dev
```

## 访问地址

- **前端**: http://localhost:30002
- **后端API**: http://localhost:20000
- **API文档**: http://localhost:20000/docs

## 项目结构

```
kidsEnglish/
├── frontend/           # Vue 3 前端
│   ├── src/
│   │   ├── views/      # 页面组件
│   │   ├── components/ # 通用组件
│   │   ├── stores/     # Pinia状态管理
│   │   └── router/     # 路由配置
│   └── package.json
│
└── backend/            # FastAPI 后端 (使用uv管理)
    ├── app/
    │   ├── main.py     # 应用入口
    │   ├── models/     # 数据库模型
    │   ├── schemas/    # Pydantic模型
    │   └── routers/    # API路由
    ├── pyproject.toml  # uv项目配置
    ├── uv.lock         # 依赖锁定文件
    └── start.sh        # 启动脚本
```

## 功能特点

- 🎨 针对3-5岁儿童优化的UI设计（大按钮、鲜艳色彩）
- 📚 26个字母的三阶段学习（认识→发音→练习）
- 🎤 语音录制和AI评分
- ⭐ 星星奖励和成就徽章系统
- 🔥 每日打卡和连续打卡统计
- 🎬 丰富的动画效果（GSAP）

## API接口

| 方法 | 路径 | 描述 |
|------|------|------|
| POST | /api/auth/register | 用户注册 |
| POST | /api/auth/login | 用户登录 |
| GET | /api/letters | 获取字母列表 |
| GET | /api/progress | 获取学习进度 |
| POST | /api/progress/update | 更新进度 |
| POST | /api/progress/checkin | 打卡 |
| POST | /api/speech/evaluate | 语音评分 |

## 待办事项

- [ ] 接入阿里云/讯飞语音评测API
- [ ] 添加更多Lottie动画素材
- [ ] 实现字母书写练习功能
- [ ] 添加背景音乐和音效
- [ ] 移动端适配优化
