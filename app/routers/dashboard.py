from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, extract
from datetime import datetime, date, timedelta
from typing import List, Optional
from app.database import get_db
from app.models.user import User
from app.models.todo import Todo
from app.models.habit import Habit, HabitEntry
from app.auth.dependencies import get_current_active_user
from pydantic import BaseModel
from typing import Dict, Any

router = APIRouter(prefix="/dashboard", tags=["dashboard"])

class TodoStats(BaseModel):
    total: int
    completed: int
    pending: int
    completion_rate: float

class HabitStats(BaseModel):
    total: int
    active: int
    completion_rate: float
    average_streak: float

class ProductivityStats(BaseModel):
    date: date
    todos_completed: int
    habits_completed: int

class HabitHeatmapData(BaseModel):
    date: date
    completed_count: int

class DashboardStats(BaseModel):
    todo_stats: TodoStats
    habit_stats: HabitStats
    productivity_trend: List[ProductivityStats]
    category_distribution: Dict[str, int]
    priority_distribution: Dict[str, int]
    habit_heatmap: List[HabitHeatmapData]

class DashboardFilters(BaseModel):
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    category: Optional[str] = None
    priority: Optional[str] = None

@router.get("/stats", response_model=DashboardStats)
async def get_dashboard_stats(
    filters: DashboardFilters = Depends(),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    # Calculate date range
    end_date = filters.end_date or date.today()
    start_date = filters.start_date or (end_date - timedelta(days=30))
    
    # Todo stats
    todo_query = db.query(Todo).filter(
        Todo.owner_id == current_user.id,
        func.date(Todo.created_at) >= start_date,
        func.date(Todo.created_at) <= end_date
    )
    
    # Apply filters
    if filters.category:
        todo_query = todo_query.filter(Todo.category == filters.category)
    
    if filters.priority:
        todo_query = todo_query.filter(Todo.priority == filters.priority)
    
    total_todos = todo_query.count()
    completed_todos = todo_query.filter(Todo.is_completed == True).count()
    pending_todos = total_todos - completed_todos
    completion_rate = (completed_todos / total_todos * 100) if total_todos > 0 else 0
    
    todo_stats = TodoStats(
        total=total_todos,
        completed=completed_todos,
        pending=pending_todos,
        completion_rate=completion_rate
    )
    
    # Habit stats
    habit_query = db.query(Habit).filter(
        Habit.owner_id == current_user.id
    )
    
    total_habits = habit_query.count()
    active_habits = habit_query.filter(Habit.is_active == True).count()
    
    # Calculate habit completion rate
    habit_completion_query = db.query(HabitEntry).join(Habit).filter(
        Habit.owner_id == current_user.id,
        func.date(HabitEntry.date) >= start_date,
        func.date(HabitEntry.date) <= end_date
    )
    
    total_entries = habit_completion_query.count()
    completed_habits = habit_completion_query.filter(HabitEntry.completed_count > 0).count()
    habit_completion_rate = (completed_habits / total_entries * 100) if total_entries > 0 else 0
    
    # Calculate average streak
    avg_streak = db.query(func.avg(Habit.streak_count)).filter(
        Habit.owner_id == current_user.id
    ).scalar() or 0
    
    habit_stats = HabitStats(
        total=total_habits,
        active=active_habits,
        completion_rate=habit_completion_rate,
        average_streak=float(avg_streak)
    )
    
    # Productivity trend (last 7 days)
    productivity_trend = []
    for i in range(7):
        trend_date = end_date - timedelta(days=6-i)
        
        # Todos completed on this date
        todos_completed = db.query(Todo).filter(
            Todo.owner_id == current_user.id,
            Todo.is_completed == True,
            func.date(Todo.completed_at) == trend_date
        ).count()
        
        # Habits completed on this date
        habits_completed = db.query(HabitEntry).join(Habit).filter(
            Habit.owner_id == current_user.id,
            HabitEntry.completed_count > 0,
            func.date(HabitEntry.date) == trend_date
        ).count()
        
        productivity_trend.append(ProductivityStats(
            date=trend_date,
            todos_completed=todos_completed,
            habits_completed=habits_completed
        ))
    
    # Habit heatmap data (last 30 days)
    heatmap_start_date = end_date - timedelta(days=29)
    habit_heatmap_data = db.query(
        HabitEntry.date,
        HabitEntry.completed_count
    ).join(Habit).filter(
        Habit.owner_id == current_user.id,
        func.date(HabitEntry.date) >= heatmap_start_date,
        func.date(HabitEntry.date) <= end_date
    ).all()

    habit_heatmap = [
        HabitHeatmapData(date=row.date, completed_count=row.completed_count)
        for row in habit_heatmap_data
    ]

    # Category distribution
    category_distribution = {}
    category_results = db.query(Todo.category, func.count(Todo.id)).filter(
        Todo.owner_id == current_user.id,
        Todo.category.isnot(None)
    ).group_by(Todo.category).all()
    
    for category, count in category_results:
        category_distribution[category] = count
    
    # Priority distribution
    priority_distribution = {}
    priority_results = db.query(Todo.priority, func.count(Todo.id)).filter(
        Todo.owner_id == current_user.id
    ).group_by(Todo.priority).all()
    
    for priority, count in priority_results:
        priority_distribution[priority] = count
    
    return DashboardStats(
        todo_stats=todo_stats,
        habit_stats=habit_stats,
        productivity_trend=productivity_trend,
        category_distribution=category_distribution,
        priority_distribution=priority_distribution,
        habit_heatmap=habit_heatmap
    )