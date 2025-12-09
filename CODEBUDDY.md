# CODEBUDDY.md

This file provides guidance to CodeBuddy Code when working with code in this repository.

## 项目概览
- 本仓库是一个面向 3-5 岁儿童的字母学习打卡应用，包含动画交互与 AI 语音评分，采用前后端分离结构：前端使用 Vue 3 + Vite + Pinia，后端使用 FastAPI + SQLAlchemy + PostgreSQL。（README.md:1-74）
- 所有对外沟通遵循 `linus.md` 中的 Linus 风格：保持好品味（少特例、控制缩进层级）、永远不要破坏已有用户体验、务必聚焦真实问题、批评指向技术，不针对个人。（linus.md:3-141）

## 目录速览
```
frontend/   Vue 3 客户端（视图、Pinia stores、路由、API 封装）
backend/    FastAPI 服务（入口、配置、数据库、模型、路由、服务）
plan/       产品/技术规划文档
```
（README.md:55-74, backend/README.md:97-114）

## 环境与常用命令
### 后端（FastAPI + uv）
1. 依赖：Python 3.10+、PostgreSQL 12+、uv 包管理器。（backend/README.md:5-28）
2. 配置：在 `backend/` 目录复制 `.env.example` 后填写数据库与阿里云凭据，默认示例连接 `postgresql+asyncpg://sql:123456@localhost:5432/kids_english`。（backend/.env.example:1-11）
3. 创建数据库：`psql -U postgres -c "CREATE DATABASE kids_english;"`。（README.md:20-24）
4. 安装依赖/虚拟环境：`uv sync`，如需激活虚拟环境执行 `source .venv/bin/activate`。（backend/README.md:66-76）
5. 启动服务：
   - `./start.sh`（封装了 uvicorn 启动）。（backend/README.md:51-54）
   - 或 `uv run uvicorn app.main:app --host 0.0.0.0 --port 20000 --reload`（热重载开发模式）。（backend/README.md:56-64）
6. 迁移（尚未初始化）：`uv run alembic init migrations` → `uv run alembic revision --autogenerate -m "desc"` → `uv run alembic upgrade head`。（backend/README.md:125-135）
7. 常用 uv 操作：`uv add <pkg>`、`uv tree`、`uv run python script.py`。（backend/README.md:78-91）
8. bcrypt 兼容性：`pyproject.toml` 固定 `bcrypt<4` 以避免 `error reading bcrypt version`，每次拉取依赖变动后在 `backend/` 运行 `uv sync` 确保虚拟环境遵守该约束。（backend/README.md:138-143）
9. 测试/静态检查：未配置任何 Python 测试或 lint 命令，需要自建流程。

### 前端（Vue 3 + Vite）
1. 依赖：Node.js 16+ 与 npm。（README.md:13-16）
2. 安装：`cd frontend && npm install`。（README.md:41-44）
3. 开发服务器：`npm run dev`（Vite，默认 http://localhost:30002）。（README.md:41-50, frontend/package.json:6-9）
4. 生产构建：`npm run build`；本地预览构建：`npm run preview`。（frontend/package.json:6-10）
5. 测试/静态检查：package.json 仅包含 dev/build/preview，尚未配置 Jest/Vitest、ESLint 或 Prettier。

## 架构与关键模块
### 后端
- **应用入口与中间件**：`app/main.py` 在导入时立即建表（`Base.metadata.create_all`），注册 CORS 允许来自 `http://localhost:30002` 的请求，并挂载 `/api` 下的 auth/progress/speech 路由。（backend/app/main.py:7-29）
- **配置管理**：Pydantic Settings 通过 `.env` 注入数据库、JWT、阿里云凭据；`get_settings()` 使用 `lru_cache` 复用实例。（backend/app/config.py:5-25）
- **数据库层**：`app/db/database.py` 使用 `create_async_engine` + `async_sessionmaker`（驱动 `postgresql+asyncpg`）并通过 `get_db()` 提供 `AsyncSession` 依赖。（backend/app/db/database.py:1-18）
- **模型**：`app/models/models.py` 定义用户、进度、打卡、成就表，使用关系映射保证一对多数据访问。（backend/app/models/models.py:7-55）
- **认证路由**：JWT 登录流程位于 `app/routers/auth.py`，`OAuth2PasswordBearer` 保护受限接口，`create_access_token` 使用 `.env` 中的 secret，`/api/auth/register|login|me` 提供注册、登录、用户信息。密码哈希使用 `bcrypt_sha256`（消除 72 字节限制）。（backend/app/routers/auth.py:13-99）
- **进度路由**：`app/routers/progress.py` 负责获取 26 个字母的完整进度、按更高星级/阶段更新进度、每日打卡、统计 streak。（backend/app/routers/progress.py:11-159）
- **语音评分路由**：`app/routers/speech.py` 校验单字母、限制音频 5MB，并将请求委托给服务层。（backend/app/routers/speech.py:12-57）
- **语音服务**：`app/services/aliyun_speech.py` 会在缺失阿里云凭据时抛错并自动回退为本地 mock 评估；mock 根据音频大小与随机数生成 1-3 星及反馈，务必在交付前替换为真实实现。（backend/app/services/aliyun_speech.py:25-190）

### 前端
- **应用初始化**：`src/main.js` 创建 Vue 应用、注册 Pinia/Router，启动前执行 `useUserStore().initUser()` 与性能优化钩子，如资源预加载、滚动优化。（frontend/src/main.js:1-23）
- **路由与守卫**：`src/router/index.js` 定义 Home/Learn/Record/Progress/Login 五条路由，并在 `beforeEach` 中基于 localStorage token 做登录重定向。（frontend/src/router/index.js:1-49）
- **状态管理**：
  - `src/stores/user.js` 管理 JWT token 与用户信息，封装 login/register/logout 流程并在登录后调用 `/api/auth/me`。（frontend/src/stores/user.js:5-68）
  - `src/stores/learning.js` 持有 26 个字母元数据、学习进度、打卡记录，并落地到 localStorage；`updateProgress()` 以 stage>=3 标记完成。（frontend/src/stores/learning.js:5-100）
- **HTTP 层**：`src/api/http.js` 预设 `baseURL` 指向 `http://localhost:20000`，请求拦截器自动拼接 `Authorization: Bearer <token>`，401 时清空本地状态并跳转登录。（frontend/src/api/http.js:1-38）
- **API 模块**：`src/api/auth.js`, `progress.js`, `speech.js` 将后端 REST 接口以函数形式暴露，Speech 调用通过 FormData 上传音频并设置 multipart 头。（frontend/src/api/auth.js:3-25, frontend/src/api/progress.js:3-32, frontend/src/api/speech.js:3-16）
- **端到端学习流程**：Home（字母网格）→ Learn（听发音）→ Record（录音上传）→ Progress（星星/成就），与 README/QUICKSTART 描述一致，API 对应 `/api/letters`, `/api/progress/*`, `/api/speech/evaluate`。（README.md:42-96, QUICKSTART.md:42-78）

### 典型数据/交互流
1. **认证**：用户登录后，`userStore.login()` 保存 token 与用户信息；axios 拦截器在每次请求中注入 JWT，路由守卫依 token 决定访问权限。（frontend/src/stores/user.js:18-44, frontend/src/api/http.js:12-38, frontend/src/router/index.js:36-49）
2. **进度同步**：前端立即写本地 `learningProgress`，同时可调用 `progressAPI.updateProgress()` 将结果持久化到后端；后端仅接受更高分数/阶段避免降级。（frontend/src/stores/learning.js:47-55, backend/app/routers/progress.py:48-73）
3. **语音评分**：Record 页将 Blob 传给 `speechAPI.evaluate()`，FastAPI 限制文件大小与字母合法性，再由 `evaluate_speech()` 返回星级、准确度与反馈。（frontend/src/api/speech.js:3-16, backend/app/routers/speech.py:17-56, backend/app/services/aliyun_speech.py:162-189）

## 资源与注意事项
- `learning` store 期待在 `public/audio/`（Vite 静态目录）存在 `a.mp3` 至 `z.mp3`，缺失时播放/学习体验受影响，提交前务必放置或提供站位音频。（frontend/src/stores/learning.js:6-33）
- 语音评分默认走随机 mock，仅在 `.env` 配置完整阿里云凭据时才会启用真实评估；部署生产前需要完成 SDK 集成与凭据加固。（backend/app/services/aliyun_speech.py:25-190）
- 当前无自动化测试与 lint 流程，任何新增功能都需要手动验证前后端交互、JWT 授权和数据库兼容性。
- README 待办列出了接入真实语音 API、添加 Lottie 动画、写字练习、音效与移动端适配等未完成事项，不要误以为已上线。（README.md:97-104）

## API 参考速览
- `/api/auth/register|login|me`, `/api/letters`, `/api/progress/(,update,checkin,stats,checkins)`, `/api/speech/evaluate`。详见 README 的接口表格与 FastAPI `routers` 实现。（README.md:85-95, backend/app/routers/*.py）

保持 Linus 风格（少废话、关注数据结构、禁止破坏既有行为），并在提交前亲自跑通前后端启动命令，确保儿童学习流程与语音评估仍可完成。