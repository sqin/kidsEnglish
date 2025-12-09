from datetime import date, timedelta
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.models.models import Checkin, Progress, User
from app.routers.auth import get_current_user
from app.schemas.schemas import CheckinResponse, ProgressResponse, ProgressUpdate

router = APIRouter(prefix="/progress", tags=["学习进度"])


@router.get("/", response_model=List[ProgressResponse])
async def get_all_progress(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取用户所有字母的学习进度"""
    result = await db.execute(select(Progress).where(Progress.user_id == current_user.id))
    progress_list = result.scalars().all()

    progress_dict = {p.letter_id: p for p in progress_list}
    response: List[ProgressResponse] = []
    for i in range(1, 27):
        if i in progress_dict:
            response.append(progress_dict[i])
        else:
            response.append(ProgressResponse(
                letter_id=i,
                stage=0,
                score=0,
                completed=False
            ))
    return response


@router.post("/update", response_model=ProgressResponse)
async def update_progress(
    progress_data: ProgressUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """更新字母学习进度"""
    if progress_data.letter_id < 1 or progress_data.letter_id > 26:
        raise HTTPException(status_code=400, detail="无效的字母ID")

    result = await db.execute(
        select(Progress).where(
            Progress.user_id == current_user.id,
            Progress.letter_id == progress_data.letter_id
        )
    )
    progress = result.scalar_one_or_none()

    if progress:
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

    await db.commit()
    await db.refresh(progress)
    return progress


@router.post("/checkin", response_model=CheckinResponse)
async def checkin(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """每日打卡"""
    today = date.today().isoformat()

    result = await db.execute(
        select(Checkin).where(
            Checkin.user_id == current_user.id,
            Checkin.date == today
        )
    )
    existing = result.scalar_one_or_none()

    if existing:
        existing.letters_learned += 1
        await db.commit()
        await db.refresh(existing)
        return existing

    record = Checkin(
        user_id=current_user.id,
        date=today,
        letters_learned=1
    )
    db.add(record)
    await db.commit()
    await db.refresh(record)
    return record


@router.get("/checkins", response_model=List[CheckinResponse])
async def get_checkins(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取打卡记录"""
    result = await db.execute(
        select(Checkin)
        .where(Checkin.user_id == current_user.id)
        .order_by(desc(Checkin.date))
        .limit(30)
    )
    return result.scalars().all()


@router.get("/stats")
async def get_stats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取学习统计"""
    stars_result = await db.execute(
        select(func.coalesce(func.sum(Progress.score), 0)).where(
            Progress.user_id == current_user.id
        )
    )
    stars = stars_result.scalar_one()

    completed_result = await db.execute(
        select(func.count()).select_from(Progress).where(
            Progress.user_id == current_user.id,
            Progress.completed.is_(True)
        )
    )
    completed = completed_result.scalar_one()

    checkins_result = await db.execute(
        select(Checkin)
        .where(Checkin.user_id == current_user.id)
        .order_by(desc(Checkin.date))
    )
    checkins = checkins_result.scalars().all()

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
        "total_stars": int(stars),
        "completed_letters": int(completed),
        "streak_days": streak
    }
