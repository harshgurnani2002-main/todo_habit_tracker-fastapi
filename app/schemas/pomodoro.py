from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

class PomodoroBase(BaseModel):
    title: str
    description: Optional[str] = None
    duration: Optional[int] = 25  # in minutes
    break_duration: Optional[int] = 5  # in minutes

class PomodoroCreate(PomodoroBase):
    pass

class PomodoroUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    duration: Optional[int] = None
    break_duration: Optional[int] = None
    is_active: Optional[bool] = None
    completed_at: Optional[datetime] = None

class Pomodoro(PomodoroBase):
    id: int
    is_active: bool
    completed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    owner_id: int
    
    class Config:
        from_attributes = True

class PomodoroAnalytics(BaseModel):
    total_sessions: int
    completed_sessions: int
    completion_rate: float
    average_duration: float
    total_time: int  # in minutes