from pydantic import BaseModel
from typing import Optional
from datetime import datetime


# User schemas
class UserCreate(BaseModel):
    nickname: str
    password: str


class UserLogin(BaseModel):
    nickname: str
    password: str


class UserResponse(BaseModel):
    id: int
    nickname: str
    avatar: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str


# Progress schemas
class ProgressUpdate(BaseModel):
    letter_id: int
    stage: int
    score: int


class ProgressResponse(BaseModel):
    letter_id: int
    stage: int
    score: int
    completed: bool

    class Config:
        from_attributes = True


# Speech evaluation
class SpeechEvalRequest(BaseModel):
    letter: str
    audio_data: str  # Base64 encoded


class SpeechEvalResponse(BaseModel):
    score: int  # 1-3 stars
    accuracy: float
    feedback: str


# Checkin
class CheckinResponse(BaseModel):
    date: str
    letters_learned: int

    class Config:
        from_attributes = True
