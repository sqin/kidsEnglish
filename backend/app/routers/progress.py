from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import date

from app.db.database import get_db
from app.models.models import User, Progress, Checkin
from app.schemas.schemas import ProgressUpdate, ProgressResponse, CheckinResponse
from app.routers.auth import get_current_user

router = APIRouter(prefix="/progress", tags=["学习进度"])


@router.get("/", response_model=List[ProgressResponse])
async def get_all_progress(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取用户所有字母的学习进度"""
    progress_list = db.query(Progress).filter(Progress.user_id == current_user.id).all()

    # 补全26个字母的进度（未学习的返回默认值）
    progress_dict = {p.letter_id: p for p in progress_list}
    result = []
    for i in range(1, 27):
        if i in progress_dict:
            result.append(progress_dict[i])
        else:
            result.append(ProgressResponse(
                letter_id=i,
                stage=0,
                score=0,
                completed=False
            ))
    return result


@router.post("/update", response_model=ProgressResponse)
async def update_progress(
    progress_data: ProgressUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """更新字母学习进度"""
    if progress_data.letter_id < 1 or progress_data.letter_id > 26:
        raise HTTPException(status_code=400, detail="无效的字母ID")

    # 查找或创建进度记录
    progress = db.query(Progress).filter(
        Progress.user_id == current_user.id,
        Progress.letter_id == progress_data.letter_id
    ).first()

    if progress:
        # 只更新更高的分数
        if progress_data.score > progress.score:
            progress.score = progress_data.score
        if progress_data.stage > progress.stage:
            progress.stage = progress_data.stage
        progress.completed = progress.stage >= 3
    else:
        progress = Progress(
            user_id=current_user.id,
            letter_id=progress_data.letter_id,
            stage=progress_data.stage,
            score=progress_data.score,
            completed=progress_data.stage >= 3
        )
        db.add(progress)

    db.commit()
    db.refresh(progress)
    return progress


@router.post("/checkin", response_model=CheckinResponse)
async def checkin(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """每日打卡"""
    today = date.today().isoformat()

    # 检查今日是否已打卡
    existing = db.query(Checkin).filter(
        Checkin.user_id == current_user.id,
        Checkin.date == today
    ).first()

    if existing:
        # 更新今日学习数量
        existing.letters_learned += 1
        db.commit()
        db.refresh(existing)
        return existing

    # 创建新打卡记录
    checkin = Checkin(
        user_id=current_user.id,
        date=today,
        letters_learned=1
    )
    db.add(checkin)
    db.commit()
    db.refresh(checkin)
    return checkin


@router.get("/checkins", response_model=List[CheckinResponse])
async def get_checkins(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取打卡记录"""
    checkins = db.query(Checkin).filter(
        Checkin.user_id == current_user.id
    ).order_by(Checkin.date.desc()).limit(30).all()
    return checkins


@router.get("/stats")
async def get_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取学习统计"""
    # 总星星数
    total_stars = db.query(Progress).filter(
        Progress.user_id == current_user.id
    ).with_entities(Progress.score).all()
    stars = sum(p.score for p in total_stars)

    # 已完成字母数
    completed = db.query(Progress).filter(
        Progress.user_id == current_user.id,
        Progress.completed == True
    ).count()

    # 连续打卡天数
    checkins = db.query(Checkin).filter(
        Checkin.user_id == current_user.id
    ).order_by(Checkin.date.desc()).all()

    streak = 0
    today = date.today()
    for i, c in enumerate(checkins):
        check_date = date.fromisoformat(c.date)
        expected_date = today - timedelta(days=i)
        if check_date == expected_date:
            streak += 1
        else:
            break

    return {
        "total_stars": stars,
        "completed_letters": completed,
        "streak_days": streak
    }


from datetime import timedelta
