from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from typing import List, Optional
from datetime import datetime, date
from pydantic import BaseModel
from app.database import get_db
from app.models.user import User
from app.models.habit import Habit, HabitEntry
from app.schemas.habit import (
    HabitCreate, HabitUpdate, Habit as HabitSchema,
    HabitEntryCreate, HabitEntry as HabitEntrySchema
)
from app.schemas.analytics import AggregateHabitAnalytics, AggregateHabitStats, HabitFrequencyDistribution, HabitCompletionTrend
from app.auth.dependencies import get_current_active_user

router = APIRouter(prefix="/habits", tags=["habits"])

@router.post("/", response_model=HabitSchema)
async def create_habit(
    habit: HabitCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    db_habit = Habit(**habit.dict(), owner_id=current_user.id)
    db.add(db_habit)
    db.commit()
    db.refresh(db_habit)
    return db_habit

@router.get("/", response_model=List[HabitSchema])
async def get_habits(
    skip: int = 0,
    limit: int = 100,
    active_only: bool = True,
    frequency: Optional[str] = Query(None, description="Filter by frequency (daily, weekly, monthly)"),
    search: Optional[str] = Query(None, description="Search in name or description"),
    created_from: Optional[date] = None,
    created_to: Optional[date] = None,
    sort_by: Optional[str] = Query("created_at", description="Sort by field"),
    sort_order: Optional[str] = Query("desc", description="Sort order (asc or desc)"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    query = db.query(Habit).filter(Habit.owner_id == current_user.id)
    
    # Apply filters
    if active_only:
        query = query.filter(Habit.is_active == True)
    
    if frequency:
        query = query.filter(Habit.frequency == frequency)
    
    if search:
        search_filter = or_(
            Habit.name.contains(search),
            Habit.description.contains(search)
        )
        query = query.filter(search_filter)
    
    if created_from:
        query = query.filter(func.date(Habit.created_at) >= created_from)
    
    if created_to:
        query = query.filter(func.date(Habit.created_at) <= created_to)
    
    # Apply sorting
    if sort_order == "desc":
        query = query.order_by(getattr(Habit, sort_by).desc())
    else:
        query = query.order_by(getattr(Habit, sort_by).asc())
    
    habits = query.offset(skip).limit(limit).all()
    return habits

@router.get("/{habit_id}", response_model=HabitSchema)
async def get_habit(
    habit_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    habit = db.query(Habit).filter(
        Habit.id == habit_id,
        Habit.owner_id == current_user.id
    ).first()
    
    if not habit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Habit not found"
        )
    
    return habit

@router.put("/{habit_id}", response_model=HabitSchema)
async def update_habit(
    habit_id: int,
    habit_update: HabitUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    habit = db.query(Habit).filter(
        Habit.id == habit_id,
        Habit.owner_id == current_user.id
    ).first()
    
    if not habit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Habit not found"
        )
    
    # Update fields
    update_data = habit_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(habit, field, value)
    
    db.commit()
    db.refresh(habit)
    return habit

@router.delete("/{habit_id}")
async def delete_habit(
    habit_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    habit = db.query(Habit).filter(
        Habit.id == habit_id,
        Habit.owner_id == current_user.id
    ).first()
    
    if not habit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Habit not found"
        )
    
    db.delete(habit)
    db.commit()
    return {"message": "Habit deleted successfully"}
from datetime import date as dt_date, timedelta

# ... existing imports ...

class HabitAnalytics(BaseModel):
    total_entries: int
    completed_entries: int
    completion_rate: float
    current_streak: int
    best_streak: int
    average_completion: float

# ... existing endpoints ...

@router.get("/{habit_id}/analytics", response_model=HabitAnalytics)
async def get_habit_analytics(
    habit_id: int,
    days: int = 30,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    # Verify habit belongs to user
    habit = db.query(Habit).filter(
        Habit.id == habit_id,
        Habit.owner_id == current_user.id
    ).first()
    
    if not habit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Habit not found"
        )
    
    # Calculate date range
    end_date = dt_date.today()
    start_date = end_date - timedelta(days=days-1)
    
    # Get entries in date range
    entries = db.query(HabitEntry).filter(
        HabitEntry.habit_id == habit_id,
        func.date(HabitEntry.date) >= start_date,
        func.date(HabitEntry.date) <= end_date
    ).all()
    
    total_entries = len(entries)
    completed_entries = len([e for e in entries if e.completed_count > 0])
    completion_rate = (completed_entries / total_entries * 100) if total_entries > 0 else 0
    
    # Calculate average completion
    total_completion = sum(e.completed_count for e in entries)
    average_completion = (total_completion / total_entries) if total_entries > 0 else 0
    
    return HabitAnalytics(
        total_entries=total_entries,
        completed_entries=completed_entries,
        completion_rate=completion_rate,
        current_streak=habit.streak_count,
        best_streak=habit.best_streak,
        average_completion=average_completion
    )

@router.post("/{habit_id}/entries", response_model=HabitEntrySchema)
async def create_habit_entry(
    habit_id: int,
    entry: HabitEntryCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    # Verify habit belongs to user
    habit = db.query(Habit).filter(
        Habit.id == habit_id,
        Habit.owner_id == current_user.id
    ).first()
    
    if not habit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Habit not found"
        )
    
    # Pick date (use provided or fallback to today)
    entry_date = entry.date or dt_date.today()

    # Check if entry for that date already exists
    existing_entry = db.query(HabitEntry).filter(
        HabitEntry.habit_id == habit_id,
        func.date(HabitEntry.date) == entry_date
    ).first()
    
    if existing_entry:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Entry for {entry_date} already exists"
        )
    
    # Create entry
    db_entry = HabitEntry(
        completed_count=entry.completed_count,
        notes=entry.notes,
        date=entry_date,
        habit_id=habit_id
    )
    db.add(db_entry)
    
    # Update habit streak
    update_habit_streak(db, habit)
    
    db.commit()
    db.refresh(db_entry)
    return db_entry

@router.get("/{habit_id}/entries", response_model=List[HabitEntrySchema])
async def get_habit_entries(
    habit_id: int,
    skip: int = 0,
    limit: int = 100,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    sort_by: Optional[str] = Query("date", description="Sort by field"),
    sort_order: Optional[str] = Query("desc", description="Sort order (asc or desc)"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    # Verify habit belongs to user
    habit = db.query(Habit).filter(
        Habit.id == habit_id,
        Habit.owner_id == current_user.id
    ).first()
    
    if not habit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Habit not found"
        )
    
    query = db.query(HabitEntry).filter(
        HabitEntry.habit_id == habit_id
    )
    
    # Apply date filters
    if date_from:
        query = query.filter(func.date(HabitEntry.date) >= date_from)
    
    if date_to:
        query = query.filter(func.date(HabitEntry.date) <= date_to)
    
    # Apply sorting
    if sort_order == "desc":
        query = query.order_by(getattr(HabitEntry, sort_by).desc())
    else:
        query = query.order_by(getattr(HabitEntry, sort_by).asc())
    
    entries = query.offset(skip).limit(limit).all()
    
    return entries

def update_habit_streak(db: Session, habit: Habit):
    """Update habit streak count based on recent entries"""
    entries = db.query(HabitEntry).filter(
        HabitEntry.habit_id == habit.id
    ).order_by(HabitEntry.date.desc()).limit(30).all()  # Last 30 entries
    
    if not entries:
        habit.streak_count = 0
        return
    
    # Calculate current streak
    current_streak = 0
    today = date.today()
    
    for entry in entries:
        entry_date = entry.date.date()
        expected_date = today - timedelta(days=current_streak)
        
        if entry_date == expected_date:
            current_streak += 1
        else:
            break
    
    habit.streak_count = current_streak
    if current_streak > habit.best_streak:
        habit.best_streak = current_streak


@router.get("/analytics/aggregate", response_model=AggregateHabitAnalytics)
async def get_aggregate_habit_analytics(
    days: int = 30,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get analytics for all habits combined"""
    # Calculate date range
    end_date = date.today()
    start_date = end_date - timedelta(days=days-1)
    
    # Get all habits for the user
    habits = db.query(Habit).filter(
        Habit.owner_id == current_user.id
    ).all()
    
    total_habits = len(habits)
    active_habits = len([h for h in habits if h.is_active])
    
    # Get entries in date range
    entries = db.query(HabitEntry).join(Habit).filter(
        Habit.owner_id == current_user.id,
        func.date(HabitEntry.date) >= start_date,
        func.date(HabitEntry.date) <= end_date
    ).all()
    
    # Calculate stats
    total_entries = len(entries)
    completed_entries = len([e for e in entries if e.completed_count > 0])
    completion_rate = (completed_entries / total_entries * 100) if total_entries > 0 else 0
    
    # Habits completed today
    today = date.today()
    completed_today = db.query(HabitEntry).join(Habit).filter(
        Habit.owner_id == current_user.id,
        func.date(HabitEntry.date) == today,
        HabitEntry.completed_count > 0
    ).count()
    
    # Average streak and best streak
    if habits:
        average_streak = sum(h.streak_count for h in habits) / len(habits)
        best_streak = max(h.best_streak for h in habits)
    else:
        average_streak = 0
        best_streak = 0
    
    stats = AggregateHabitStats(
        total_habits=total_habits,
        active_habits=active_habits,
        completed_today=completed_today,
        completion_rate=completion_rate,
        average_streak=average_streak,
        best_streak=best_streak
    )
    
    # Frequency distribution
    daily_count = len([h for h in habits if h.frequency == "daily"])
    weekly_count = len([h for h in habits if h.frequency == "weekly"])
    monthly_count = len([h for h in habits if h.frequency == "monthly"])
    
    frequency_distribution = HabitFrequencyDistribution(
        daily=daily_count,
        weekly=weekly_count,
        monthly=monthly_count
    )
    
    # Completion trend (last 7 days)
    completion_trend = []
    for i in range(7):
        trend_date = end_date - timedelta(days=6-i)
        completed_count = db.query(HabitEntry).join(Habit).filter(
            Habit.owner_id == current_user.id,
            func.date(HabitEntry.date) == trend_date,
            HabitEntry.completed_count > 0
        ).count()
        
        completion_trend.append(HabitCompletionTrend(
            date=trend_date,
            completed=completed_count
        ))
    
    # Category completion (by frequency)
    category_completion = {
        "daily": daily_count,
        "weekly": weekly_count,
        "monthly": monthly_count
    }
    
    return AggregateHabitAnalytics(
        stats=stats,
        frequency_distribution=frequency_distribution,
        completion_trend=completion_trend,
        category_completion=category_completion
    )
