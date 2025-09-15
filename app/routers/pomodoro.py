from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from datetime import datetime, date, timedelta
from app.database import get_db
from app.models.user import User
from app.models.pomodoro import PomodoroSession
from app.schemas.pomodoro import (
    PomodoroCreate, PomodoroUpdate, Pomodoro,
    PomodoroAnalytics
)
from app.auth.dependencies import get_current_active_user

router = APIRouter(prefix="/pomodoro", tags=["pomodoro"])

@router.post("/", response_model=Pomodoro)
async def create_pomodoro_session(
    pomodoro: PomodoroCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    db_pomodoro = PomodoroSession(**pomodoro.dict(), owner_id=current_user.id)
    db.add(db_pomodoro)
    db.commit()
    db.refresh(db_pomodoro)
    return db_pomodoro

@router.get("/analytics", response_model=PomodoroAnalytics)
async def get_pomodoro_analytics(
    days: int = 30,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get analytics for Pomodoro sessions"""
    # Validate days parameter
    if days <= 0 or days > 365:
        days = 30  # Default to 30 days if invalid
    
    # Calculate date range
    end_date = date.today()
    start_date = end_date - timedelta(days=days-1)
    
    # Get sessions in date range
    sessions = db.query(PomodoroSession).filter(
        PomodoroSession.owner_id == current_user.id,
        func.date(PomodoroSession.created_at) >= start_date,
        func.date(PomodoroSession.created_at) <= end_date
    ).all()
    
    total_sessions = len(sessions)
    completed_sessions = len([s for s in sessions if s.completed_at is not None])
    completion_rate = (completed_sessions / total_sessions * 100) if total_sessions > 0 else 0
    
    # Calculate average duration and total time
    if sessions:
        # Handle None values in duration
        valid_durations = [s.duration or 0 for s in sessions]
        average_duration = sum(valid_durations) / len(valid_durations)
        total_time = sum(valid_durations)
    else:
        average_duration = 0
        total_time = 0
    
    return PomodoroAnalytics(
        total_sessions=total_sessions,
        completed_sessions=completed_sessions,
        completion_rate=round(completion_rate, 2),
        average_duration=round(average_duration, 2),
        total_time=total_time
    )

@router.get("/", response_model=List[Pomodoro])
async def get_pomodoro_sessions(
    skip: int = 0,
    limit: int = 100,
    active_only: bool = True,
    search: Optional[str] = Query(None, description="Search in title or description"),
    created_from: Optional[date] = None,
    created_to: Optional[date] = None,
    sort_by: Optional[str] = Query("created_at", description="Sort by field"),
    sort_order: Optional[str] = Query("desc", description="Sort order (asc or desc)"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    query = db.query(PomodoroSession).filter(PomodoroSession.owner_id == current_user.id)
    
    # Apply filters
    if active_only:
        query = query.filter(PomodoroSession.is_active == True)
    
    if search:
        search_filter = func.concat(PomodoroSession.title, ' ', PomodoroSession.description).ilike(f"%{search}%")
        query = query.filter(search_filter)
    
    if created_from:
        query = query.filter(func.date(PomodoroSession.created_at) >= created_from)
    
    if created_to:
        query = query.filter(func.date(PomodoroSession.created_at) <= created_to)
    
    # Apply sorting
    if sort_order == "desc":
        query = query.order_by(getattr(PomodoroSession, sort_by).desc())
    else:
        query = query.order_by(getattr(PomodoroSession, sort_by).asc())
    
    pomodoros = query.offset(skip).limit(limit).all()
    return pomodoros

@router.get("/{pomodoro_id}", response_model=Pomodoro)
async def get_pomodoro_session(
    pomodoro_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    pomodoro = db.query(PomodoroSession).filter(
        PomodoroSession.id == pomodoro_id,
        PomodoroSession.owner_id == current_user.id
    ).first()
    
    if not pomodoro:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pomodoro session not found"
        )
    
    return pomodoro

@router.put("/{pomodoro_id}", response_model=Pomodoro)
async def update_pomodoro_session(
    pomodoro_id: int,
    pomodoro_update: PomodoroUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    pomodoro = db.query(PomodoroSession).filter(
        PomodoroSession.id == pomodoro_id,
        PomodoroSession.owner_id == current_user.id
    ).first()
    
    if not pomodoro:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pomodoro session not found"
        )
    
    # Update fields
    update_data = pomodoro_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(pomodoro, field, value)
    
    db.commit()
    db.refresh(pomodoro)
    return pomodoro

@router.delete("/{pomodoro_id}")
async def delete_pomodoro_session(
    pomodoro_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    pomodoro = db.query(PomodoroSession).filter(
        PomodoroSession.id == pomodoro_id,
        PomodoroSession.owner_id == current_user.id
    ).first()
    
    if not pomodoro:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pomodoro session not found"
        )
    
    db.delete(pomodoro)
    db.commit()
    return {"message": "Pomodoro session deleted successfully"}

