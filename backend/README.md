# 后端启动指南

## 环境要求

- Python 3.10+
- uv (https://docs.astral.sh/uv/getting-started/installation/)
- PostgreSQL 12+

## 安装uv

### macOS / Linux
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Windows
```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### 使用包管理器 (推荐)
```bash
# Homebrew (macOS)
brew install uv

# Cargo (Rust)
cargo install uv
```

## 快速启动

### 1. 配置环境变量
```bash
cp .env.example .env
```

编辑 `.env` 文件，设置数据库连接和阿里云配置：
```
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/kids_english
SECRET_KEY=your-secret-key-change-in-production

# 阿里云语音评测配置 (可选，未配置将使用本地模拟)
ALIYUN_ACCESS_KEY_ID=your-access-key-id
ALIYUN_ACCESS_KEY_SECRET=your-access-key-secret
ALIYUN_APP_KEY=your-nls-app-key
```

### 2. 创建数据库
在PostgreSQL中执行：
```sql
CREATE DATABASE kids_english;
```

### 3. 启动开发服务器

#### 方式1: 使用启动脚本
```bash
./start.sh
```

#### 方式2: 使用uv run
```bash
uv run uvicorn app.main:app --host 0.0.0.0 --port 20000 --reload
```

#### 方式3: 使用uvicorn (uv环境已激活)
```bash
uvicorn app.main:app --host 0.0.0.0 --port 20000 --reload
```

## uv常用命令

### 安装依赖
```bash
uv sync
```

### 激活虚拟环境
```bash
source .venv/bin/activate
```

### 运行Python脚本
```bash
uv run python script.py
```

### 添加新依赖
```bash
uv add package-name
```

### 查看依赖
```bash
uv tree
```

## API文档

启动后访问：http://localhost:20000/docs

## 项目结构

```
app/
├── main.py          # 应用入口
├── config.py        # 配置管理
├── db/              # 数据库相关
│   └── database.py  # 数据库连接
├── models/          # SQLAlchemy模型
│   └── models.py
├── schemas/         # Pydantic模型
│   └── schemas.py
├── routers/         # API路由
│   ├── auth.py      # 认证
│   ├── progress.py  # 学习进度
│   └── speech.py    # 语音评分
└── services/        # 业务逻辑
    └── aliyun_speech.py  # 阿里云语音评测服务
```

## 环境变量

- `DATABASE_URL`: PostgreSQL连接字符串
- `SECRET_KEY`: JWT密钥
- `ALIYUN_ACCESS_KEY_ID`: 阿里云AccessKey (用于真实语音评测)
- `ALIYUN_ACCESS_KEY_SECRET`: 阿里云Secret
- `ALIYUN_APP_KEY`: 阿里云智能语音交互AppKey

## 语音评测功能

本项目集成了阿里云智能语音交互（NLS）服务进行语音评测。

- **配置**：在 `.env` 中填入阿里云凭证即可启用真实评测。
- **降级**：如果未配置凭证或连接阿里云失败，系统会自动降级使用本地模拟评测（返回随机高分），确保演示环境可用。
- **依赖**：使用 `alibabacloud-nls-python-sdk` 进行 WebSocket 通信。

## 数据库迁移

```bash
# 初始化迁移环境
uv run alembic init migrations

# 创建迁移
uv run alembic revision --autogenerate -m "Description"

# 应用迁移
uv run alembic upgrade head
```

## 注意事项

1. 确保PostgreSQL服务正在运行
2. 生产环境请修改SECRET_KEY为强随机字符串
3. 语音评分API需要配置阿里云凭据才能使用真实评分
4. 如果看到 `error reading bcrypt version` 或 `module 'bcrypt' has no attribute '__about__'`，请在 `backend/` 目录执行 `uv sync` 以安装我们固定的 `bcrypt<4` 版本。
