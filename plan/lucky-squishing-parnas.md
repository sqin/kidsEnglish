# 儿童英语字母学习 Web 应用

## 项目概述
- **目标用户**：3-5岁学龄前儿童
- **核心功能**：字母学习打卡 + 动画互动 + AI语音评分
- **技术栈**：Vue 3 + Vite

---

## 一、产品设计

### 1.1 UI/UX 设计原则（针对3-5岁）
- **大尺寸触控区域**：按钮最小 60px，方便小手操作
- **鲜艳色彩**：使用高饱和度、对比强烈的色彩
- **简化导航**：最多2层页面深度，无复杂菜单
- **即时反馈**：每次操作都有动画/声音反馈
- **家长辅助入口**：设置页面需家长验证（简单数学题）

### 1.2 学习流程设计（三阶段）

```
阶段1: 认识 → 阶段2: 发音 → 阶段3: 练习
```

| 阶段 | 内容 | 交互方式 |
|------|------|---------|
| **认识** | 字母形状 + 动画演示 + 标准发音 | 点击播放，跟随动画 |
| **发音** | 录音跟读 + AI评分 | 按住录音，松开评分 |
| **练习** | 字母匹配游戏 | 拖拽配对 |

### 1.3 激励机制
- **星星奖励**：完成每个字母获得1-3颗星（根据评分）
- **每日打卡**：连续打卡显示火焰图标
- **成就徽章**：完成里程碑解锁徽章（如"字母新手"、"发音达人"）
- **角色成长**：可选的虚拟宠物/角色随学习进度成长

### 1.4 动画设计
- **字母出场动画**：弹跳、旋转进入
- **发音口型动画**：卡通嘴巴示范
- **奖励动画**：星星飞入、撒花、角色跳舞
- **引导动画**：手指图标指引操作

---

## 二、内容设计

### 2.1 字母学习结构
每个字母包含：
1. **字母展示**：大写 + 小写
2. **标准发音**：音频 + 口型动画
3. **关联单词**：2-3个简单单词配图
4. **趣味记忆**：字母联想图（如 A = Apple 苹果形状）

### 2.2 学习顺序
采用**高频字母优先**策略，而非 A-Z 顺序：
```
第一周: A, E, I, O, U (元音)
第二周: S, T, N, R (高频辅音)
第三周: L, C, D, P
第四周: M, B, F, G
第五周: H, W, K, V
第六周: J, Q, X, Y, Z
```

### 2.3 每日学习量
- **推荐时长**：10-15分钟/天
- **每次学习**：1-2个新字母 + 复习1-2个旧字母

---

## 三、技术方案

### 3.1 技术栈总览
- **前端**：Vue 3 + Vite + Pinia + Vue Router
- **后端**：Python FastAPI + SQLAlchemy
- **数据库**：PostgreSQL
- **动画**：GSAP + Lottie（免费素材）
- **语音评分**：阿里云/讯飞 语音评测API

### 3.2 项目结构
```
kids-english/
├── frontend/                # Vue 前端
│   ├── src/
│   │   ├── views/           # 页面组件
│   │   │   ├── Home.vue     # 首页（字母列表）
│   │   │   ├── Learn.vue    # 学习页面
│   │   │   ├── Record.vue   # 录音评分页
│   │   │   └── Progress.vue # 进度/成就页
│   │   ├── components/      # 通用组件
│   │   │   ├── LetterCard.vue
│   │   │   ├── AudioRecorder.vue
│   │   │   ├── StarRating.vue
│   │   │   └── RewardAnimation.vue
│   │   ├── composables/     # 组合式函数
│   │   │   ├── useAudio.js
│   │   │   ├── useRecorder.js
│   │   │   └── useProgress.js
│   │   ├── stores/          # Pinia 状态管理
│   │   │   ├── user.js
│   │   │   └── learning.js
│   │   ├── assets/          # 静态资源
│   │   │   ├── audio/
│   │   │   ├── images/
│   │   │   └── animations/
│   │   └── api/             # API调用
│   │       ├── auth.js
│   │       ├── progress.js
│   │       └── speech.js
│   └── package.json
│
├── backend/                 # FastAPI 后端
│   ├── app/
│   │   ├── main.py          # 应用入口
│   │   ├── config.py        # 配置
│   │   ├── models/          # 数据库模型
│   │   │   ├── user.py
│   │   │   ├── progress.py
│   │   │   └── achievement.py
│   │   ├── schemas/         # Pydantic 模型
│   │   ├── routers/         # API 路由
│   │   │   ├── auth.py
│   │   │   ├── letters.py
│   │   │   ├── progress.py
│   │   │   └── speech.py
│   │   ├── services/        # 业务逻辑
│   │   │   └── speech_eval.py  # 语音评分服务
│   │   └── db/
│   │       └── database.py
│   ├── requirements.txt
│   └── alembic/             # 数据库迁移
│
└── docker-compose.yml       # 本地开发环境
```

### 3.2 动画方案
**推荐：GSAP + Lottie**
- **GSAP**：处理交互动画（按钮反馈、页面过渡）
- **Lottie**：播放预制的复杂动画（角色、奖励特效）

```bash
npm install gsap lottie-web
```

### 3.3 语音录制
使用 Web Audio API + MediaRecorder：
```javascript
// 核心流程
1. navigator.mediaDevices.getUserMedia() 获取麦克风权限
2. MediaRecorder 录制音频
3. 转换为 Blob/Base64 发送到后端
```

### 3.4 AI语音评分方案

| 服务商 | 优势 | 价格 |
|--------|------|------|
| **讯飞** | 中文支持好，有儿童语音优化 | ~¥0.005/次 |
| **阿里云** | 价格便宜，集成简单 | ~¥0.004/次 |
| **Azure** | 评分维度丰富，英语效果好 | ~$0.001/次 |

**推荐**：先用阿里云快速验证，后期可切换讯飞获得更好的儿童语音支持

### 3.5 后端API设计

```
POST /api/auth/register      # 用户注册
POST /api/auth/login         # 登录
GET  /api/letters            # 获取字母列表
GET  /api/letters/{id}       # 获取字母详情
POST /api/speech/evaluate    # 语音评分（上传音频）
GET  /api/progress           # 获取学习进度
POST /api/progress/checkin   # 打卡
GET  /api/achievements       # 获取成就列表
```

### 3.6 数据库模型

```sql
-- 用户表
users(id, nickname, avatar, created_at)

-- 学习进度
progress(id, user_id, letter_id, stage, score, completed_at)

-- 打卡记录
checkins(id, user_id, date, letters_learned)

-- 成就
achievements(id, user_id, badge_type, unlocked_at)
```

---

## 四、实施步骤

### Phase 1: 环境搭建
- [ ] 前端：Vue 3 + Vite + Pinia + Vue Router
- [ ] 后端：FastAPI 项目结构
- [ ] 数据库：PostgreSQL + SQLAlchemy
- [ ] Docker Compose 本地开发环境

### Phase 2: 用户系统
- [ ] 简单注册/登录（可用手机号或昵称）
- [ ] JWT 认证
- [ ] 用户状态管理

### Phase 3: 核心学习功能
- [ ] 字母列表页面
- [ ] 字母学习详情页（认识阶段）
- [ ] 音频播放功能
- [ ] 基础动画效果（GSAP + Lottie免费素材）

### Phase 4: 语音打卡
- [ ] 前端录音组件（Web Audio API）
- [ ] 后端语音评分服务（阿里云API）
- [ ] 评分结果展示 + 星星奖励

### Phase 5: 激励系统
- [ ] 打卡日历组件
- [ ] 星星/积分系统
- [ ] 成就徽章
- [ ] 奖励动画

### Phase 6: 内容与优化
- [ ] 26个字母的音频资源（可用TTS生成）
- [ ] 配套图片/动画素材
- [ ] 关联单词内容
- [ ] 性能优化

---

## 五、动画资源来源

免费素材网站推荐：
- **LottieFiles**: https://lottiefiles.com/free-animations
- **Lordicon**: https://lordicon.com/
- **Freepik**: https://freepik.com (部分免费)

需要的动画类型：
1. 字母出场动画
2. 星星飞入动画
3. 撒花庆祝动画
4. 引导手指动画
5. 卡通角色反馈动画
