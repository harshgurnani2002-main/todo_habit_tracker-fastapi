from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

class HabitBase(BaseModel):
    name: str
    description: Optional[str] = None
    frequency: Optional[str] = "daily"
    target_count: Optional[int] = 1

class HabitCreate(HabitBase):
    pass

class HabitUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    frequency: Optional[str] = None
    target_count: Optional[int] = None
    is_active: Optional[bool] = None

class HabitEntryBase(BaseModel):
    completed_count: Optional[int] = 1
    notes: Optional[str] = None
    date: Optional[datetime] = None

class HabitEntryCreate(HabitEntryBase):
    pass

class HabitEntry(HabitEntryBase):
    id: int
    date: datetime
    habit_id: int
    
    class Config:
        from_attributes = True

class Habit(HabitBase):
    id: int
    is_active: bool
    streak_count: int
    best_streak: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    owner_id: int
    entries: List[HabitEntry] = []
    
    class Config:
        from_attributes = True
