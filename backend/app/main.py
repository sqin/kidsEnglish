from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import auth, progress, speech
from app.db.database import engine, Base


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(
    title="儿童英语学习API",
    description="面向3-5岁儿童的字母学习打卡应用",
    version="1.0.0",
    lifespan=lifespan
)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=[],
    allow_origin_regex=r"https?://.*",  # 允许局域网访问
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(auth.router, prefix="/api")
app.include_router(progress.router, prefix="/api")
app.include_router(speech.router, prefix="/api")


@app.get("/")
async def root():
    return {"message": "儿童英语学习API", "version": "1.0.0"}


@app.get("/api/health")
async def health_check():
    return {"status": "healthy"}


@app.get("/api/letters")
async def get_letters():
    """获取26个字母列表"""
    letters = [
        {"id": 1, "letter": "A", "word": "Apple", "image": "🍎"},
        {"id": 2, "letter": "B", "word": "Ball", "image": "⚽"},
        {"id": 3, "letter": "C", "word": "Cat", "image": "🐱"},
        {"id": 4, "letter": "D", "word": "Dog", "image": "🐶"},
        {"id": 5, "letter": "E", "word": "Elephant", "image": "🐘"},
        {"id": 6, "letter": "F", "word": "Fish", "image": "🐟"},
        {"id": 7, "letter": "G", "word": "Grape", "image": "🍇"},
        {"id": 8, "letter": "H", "word": "House", "image": "🏠"},
        {"id": 9, "letter": "I", "word": "Ice cream", "image": "🍦"},
        {"id": 10, "letter": "J", "word": "Juice", "image": "🧃"},
        {"id": 11, "letter": "K", "word": "Kite", "image": "🪁"},
        {"id": 12, "letter": "L", "word": "Lion", "image": "🦁"},
        {"id": 13, "letter": "M", "word": "Moon", "image": "🌙"},
        {"id": 14, "letter": "N", "word": "Nest", "image": "🪺"},
        {"id": 15, "letter": "O", "word": "Orange", "image": "🍊"},
        {"id": 16, "letter": "P", "word": "Panda", "image": "🐼"},
        {"id": 17, "letter": "Q", "word": "Queen", "image": "👸"},
        {"id": 18, "letter": "R", "word": "Rainbow", "image": "🌈"},
        {"id": 19, "letter": "S", "word": "Sun", "image": "☀️"},
        {"id": 20, "letter": "T", "word": "Tiger", "image": "🐯"},
        {"id": 21, "letter": "U", "word": "Umbrella", "image": "☂️"},
        {"id": 22, "letter": "V", "word": "Violin", "image": "🎻"},
        {"id": 23, "letter": "W", "word": "Watermelon", "image": "🍉"},
        {"id": 24, "letter": "X", "word": "Xylophone", "image": "🎵"},
        {"id": 25, "letter": "Y", "word": "Yo-yo", "image": "🪀"},
        {"id": 26, "letter": "Z", "word": "Zebra", "image": "🦓"},
    ]
    return letters
