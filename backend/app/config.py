from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # 数据库配置
    database_url: str = "postgresql://postgres:postgres@localhost:5432/kids_english"

    # JWT配置
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24 * 7  # 7天

    # 语音评分API配置（阿里云）
    aliyun_access_key_id: str = ""
    aliyun_access_key_secret: str = ""
    aliyun_app_key: str = ""

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings():
    return Settings()
