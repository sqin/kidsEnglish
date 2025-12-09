# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **children's English alphabet learning web application** for ages 3-5, featuring animated interactions and AI voice scoring. It's a full-stack application with a Vue 3 frontend and FastAPI backend.

**Tech Stack:**
- **Frontend**: Vue 3 + Vite + Pinia + Vue Router + GSAP (animations)
- **Backend**: Python FastAPI + SQLAlchemy (async) + PostgreSQL
- **Package Management**: `uv` for Python, `npm` for Node.js

---

## Common Development Commands

### Frontend (Vue 3)

```bash
cd frontend

# Install dependencies
npm install

# Start development server (runs on http://localhost:30002)
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

**Vite Config**: `/frontend/vite.config.js` - Server runs on `0.0.0.0:30002`

### Backend (FastAPI)

```bash
cd backend

# Install/sync dependencies (uses uv)
uv sync

# Start development server (runs on http://localhost:20000)
uv run uvicorn app.main:app --host 0.0.0.0 --port 20000 --reload

# Or use the startup script
./start.sh

# Run specific test
uv run python test_auth_local.py

# Run a Python script
uv run python script.py

# Add new dependency
uv add package-name

# View dependency tree
uv tree
```

**Important**: Backend requires PostgreSQL to be running with a database named `kids_english`.

### Database Setup

```bash
# Create database (in PostgreSQL)
CREATE DATABASE kids_english;

# Or use the provided script
./create_db.sh

# Initialize database tables
uv run python init_db.py
```

### Environment Configuration

Backend uses `.env` file (copy from `.env.example`):
```bash
cp .env.example .env
```

Required environment variables:
- `DATABASE_URL`: PostgreSQL connection string
- `SECRET_KEY`: JWT secret key
- `ALIYUN_ACCESS_KEY_ID` (optional): For real voice scoring
- `ALIYUN_ACCESS_KEY_SECRET` (optional)
- `ALIYUN_APP_KEY` (optional)

---

## High-Level Architecture

### Project Structure

```
kidsEnglish/
├── frontend/                    # Vue 3 Frontend
│   ├── src/
│   │   ├── views/              # Page components
│   │   │   ├── Home.vue        # Alphabet grid (26 letters)
│   │   │   ├── Learn.vue       # Letter learning page
│   │   │   ├── Record.vue      # Voice recording page
│   │   │   ├── Progress.vue    # Achievement/progress page
│   │   │   └── Login.vue       # Login page
│   │   ├── components/         # Reusable components
│   │   │   ├── LetterCard.vue  # Alphabet card component
│   │   │   └── LottieAnimation.vue
│   │   ├── stores/             # Pinia state management
│   │   │   ├── user.js         # User authentication state
│   │   │   └── learning.js     # Learning progress state
│   │   ├── api/                # HTTP client wrappers
│   │   │   ├── auth.js         # Authentication endpoints
│   │   │   ├── progress.js     # Progress tracking
│   │   │   └── speech.js       # Voice scoring
│   │   ├── composables/        # Composition functions
│   │   │   └── useAudio.js     # Audio playback
│   │   ├── router/             # Vue Router config
│   │   │   └── index.js        # Routes + auth guards
│   │   ├── assets/             # Static resources
│   │   │   ├── audio/          # Letter pronunciation files
│   │   │   ├── images/         # Images
│   │   │   └── animations/     # Lottie animation data
│   │   └── utils/              # Utilities
│   │       └── performance.js  # Performance optimizations
│   └── package.json
│
└── backend/                     # FastAPI Backend
    ├── app/
    │   ├── main.py             # Application entry point
    │   ├── config.py           # Settings configuration
    │   ├── db/
    │   │   └── database.py     # Database connection (async)
    │   ├── models/             # SQLAlchemy models
    │   │   └── models.py       # User, Progress, Checkin, Achievement
    │   ├── schemas/            # Pydantic models
    │   │   └── schemas.py      # Request/response schemas
    │   ├── routers/            # API route handlers
    │   │   ├── auth.py         # Authentication (JWT)
    │   │   ├── progress.py     # Learning progress
    │   │   └── speech.py       # Voice scoring
    │   └── services/           # Business logic
    │       └── aliyun_speech.py # Alibaba Cloud NLS integration
    ├── pyproject.toml          # uv project configuration
    ├── .env.example            # Environment variables template
    ├── start.sh                # Development server startup script
    ├── create_db.sh            # Database creation script
    └── test_auth_local.py      # Authentication test
```

### Backend Architecture

**Application Entry**: `backend/app/main.py`
- FastAPI app with CORS middleware
- Lifespan context manager for database initialization
- Routes registered at `/api` prefix
- Hardcoded alphabet data in `/api/letters` endpoint

**Database Models** (`backend/app/models/models.py`):
- **User**: Stores user accounts with JWT authentication
- **Progress**: Tracks learning progress per letter (stage 0-3, score 0-3)
- **Checkin**: Daily check-in records
- **Achievement**: Unlocked badges (beginner, apprentice, master, streak7, etc.)

**Authentication Flow** (`backend/app/routers/auth.py`):
- Uses JWT tokens with `python-jose`
- Password hashing with `passlib` (bcrypt)
- OAuth2PasswordBearer for token extraction
- Dependencies: `get_current_user()` for protected routes

**API Routes**:
- `/api/auth/*` - Register, login, get current user
- `/api/progress/*` - Get/update progress, check-in, stats
- `/api/speech/evaluate` - Voice scoring (mock or Alibaba Cloud NLS)
- `/api/letters` - Get 26 alphabet letters with associated words

### Frontend Architecture

**State Management** (Pinia stores):
- `user.js`: Authentication state, login/logout, token management
- `learning.js`: Learning progress, achievements, check-ins

**Router** (`frontend/src/router/index.js`):
- 5 routes: Home, Learn, Record, Progress, Login
- Route guard checks JWT token in localStorage
- Auto-redirect to login if not authenticated

**Key Components**:
- **Home.vue**: Grid of 26 alphabet cards
- **Learn.vue**: Plays letter pronunciation, transitions to Record
- **Record.vue**: Web Audio API recording, displays score (1-3 stars)
- **Progress.vue**: Shows achievements, statistics, calendar
- **LetterCard.vue**: Reusable alphabet card with GSAP animations

**Audio System** (`frontend/src/composables/useAudio.js`):
- Web Speech API for TTS
- Web Audio API for recording
- Fallback to local audio files in `/assets/audio/`

**Animations**:
- GSAP for transitions (letter pop-in, star fly-in, confetti)
- CSS animations for simpler effects
- Performance optimizations in `utils/performance.js`

---

## Key Features & Implementation

### Learning System
- **26 Letters**: Each letter has 3 stages (认识→发音→练习)
- **Progress Tracking**: Stored in `progress` table (stage 0-3, score 0-3)
- **Stage Progression**: Home → Learn (stage 1) → Record (stage 2-3) → Home

### Voice Scoring
- **Mock Implementation**: Returns random high scores by default
- **Real Integration**: Configurable via Alibaba Cloud NLS SDK
- **Fallback**: Automatically degrades to mock if cloud API unavailable
- **Scoring**: 1-3 stars based on pronunciation quality

### Achievement System
- **Badge Types**: beginner, apprentice, master, streak7, etc.
- **Triggers**: Based on learning progress and consecutive check-ins
- **Visual Feedback**: GSAP animations (confetti, star bursts)

### Authentication
- **JWT-based**: Tokens stored in localStorage
- **Auto-login**: On page refresh, restores user from localStorage
- **Route Protection**: Router guard enforces authentication

---

## API Documentation

FastAPI auto-generates interactive API docs at: `http://localhost:20000/docs`

**Main Endpoints**:
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login (returns JWT)
- `GET /api/auth/me` - Get current user info
- `GET /api/progress/` - Get user's learning progress
- `POST /api/progress/update` - Update letter progress
- `POST /api/progress/checkin` - Daily check-in
- `GET /api/progress/stats` - Achievement statistics
- `POST /api/speech/evaluate` - Score pronunciation
- `GET /api/letters` - Get alphabet data (A-Z with words)

---

## Development Tips

### Adding New Features

1. **Frontend**: Add routes to `/frontend/src/router/index.js`, create views in `/frontend/src/views/`
2. **Backend**: Add routes to appropriate router in `/backend/app/routers/`, update models in `/backend/app/models/models.py`
3. **Database**: Models auto-create on startup via lifespan in `main.py`

### Testing
- **Backend**: `uv run python test_auth_local.py` - Tests password hashing and JWT
- **Database**: Ensure PostgreSQL is running before testing
- **Frontend**: No test framework configured yet

### Performance Optimizations
- Frontend uses `preloadCriticalResources()`, `optimizeScroll()`, `adjustQualityBasedOnDevice()`
- Lazy loading for route components
- Audio preloading for letter pronunciations

### Common Issues
1. **Database Connection**: Ensure PostgreSQL is running and `DATABASE_URL` is correct
2. **CORS**: Configured in `backend/app/main.py` with origin regex
3. **uv not found**: Install from https://docs.astral.sh/uv/
4. **bcrypt errors**: Run `uv sync` in backend directory

---

## Resources

- **Frontend**: Vue 3, Pinia, GSAP, Lottie Web
- **Backend**: FastAPI, SQLAlchemy Async, JWT, Alembic
- **Database**: PostgreSQL 12+
- **Cloud Services**: Alibaba Cloud NLS (optional for voice scoring)

---

## Important Notes

1. **No Test Framework**: Currently uses standalone test scripts, no pytest/unittest configured
2. **No Linting**: No ESLint/Prettier configured for frontend, no Ruff/Black for Python
3. **Mock Voice Scoring**: Real Alibaba Cloud NLS integration is optional and configurable
4. **Auto Database Creation**: Tables are created automatically on backend startup
5. **Hardcoded Alphabet Data**: Letter list is in `backend/app/main.py` (not database)
6. **Performance First**: Designed for low-end devices with automatic quality adjustments
