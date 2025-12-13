from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    nickname = Column(String(50), unique=True, index=True)
    avatar = Column(String(200), nullable=True)
    hashed_password = Column(String(100))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    progress = relationship("Progress", back_populates="user")
    checkins = relationship("Checkin", back_populates="user")
    achievements = relationship("Achievement", back_populates="user")
    recordings = relationship("Recording", back_populates="user")


class Progress(Base):
    __tablename__ = "progress"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    letter_id = Column(Integer, index=True)  # 1-26 对应 A-Z
    stage = Column(Integer, default=0)  # 0:未开始, 1:认识, 2:发音, 3:练习完成
    score = Column(Integer, default=0)  # 0-3 星
    completed = Column(Boolean, default=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    user = relationship("User", back_populates="progress")


class Checkin(Base):
    __tablename__ = "checkins"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    date = Column(String(10), index=True)  # YYYY-MM-DD
    letters_learned = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="checkins")


class Achievement(Base):
    __tablename__ = "achievements"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    badge_type = Column(String(50))  # beginner, apprentice, master, streak7, etc.
    unlocked_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="achievements")


class Recording(Base):
    __tablename__ = "recordings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    letter_id = Column(Integer, index=True)  # 1-26 对应 A-Z
    letter = Column(String(1))  # 字母 A-Z
    file_path = Column(String(500))  # 音频文件路径
    file_url = Column(String(500))  # 音频文件URL
    score = Column(Integer, default=0)  # 评分 0-3
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="recordings")
