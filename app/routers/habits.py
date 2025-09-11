from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from datetime import datetime, date
from app.database import get_db
from app.models.user import User
from app.models.habit import Habit, HabitEntry
from app.schemas.habit import (
    HabitCreate, HabitUpdate, Habit as HabitSchema,
    HabitEntryCreate, HabitEntry as HabitEntrySchema
)
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
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    query = db.query(Habit).filter(Habit.owner_id == current_user.id)
    
    if active_only:
        query = query.filter(Habit.is_active == True)
    
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
from datetime import date as dt_date

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
    
    entries = db.query(HabitEntry).filter(
        HabitEntry.habit_id == habit_id
    ).order_by(HabitEntry.date.desc()).offset(skip).limit(limit).all()
    
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
