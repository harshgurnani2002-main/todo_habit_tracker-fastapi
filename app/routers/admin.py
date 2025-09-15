from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from typing import List, Optional
from datetime import datetime, date
from app.database import get_db
from app.models.user import User
from app.models.todo import Todo
from app.models.habit import Habit
from app.schemas.user import User as UserSchema
from app.auth.dependencies import get_current_user
from pydantic import BaseModel

router = APIRouter(prefix="/admin", tags=["admin"])

class UserStats(BaseModel):
    total_users: int
    active_users: int
    admin_users: int

class TodoStats(BaseModel):
    total_todos: int
    completed_todos: int
    pending_todos: int

class HabitStats(BaseModel):
    total_habits: int
    active_habits: int

class AdminDashboardStats(BaseModel):
    user_stats: UserStats
    todo_stats: TodoStats
    habit_stats: HabitStats

class AdminUserUpdate(BaseModel):
    is_active: Optional[bool] = None
    is_admin: Optional[bool] = None
    is_verified: Optional[bool] = None

# Admin dependency
async def get_current_admin_user(current_user: User = Depends(get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user

@router.get("/dashboard", response_model=AdminDashboardStats)
async def get_admin_dashboard(
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_current_admin_user)
):
    # User stats
    total_users = db.query(User).count()
    active_users = db.query(User).filter(User.is_active == True).count()
    admin_users = db.query(User).filter(User.is_admin == True).count()
    
    user_stats = UserStats(
        total_users=total_users,
        active_users=active_users,
        admin_users=admin_users
    )
    
    # Todo stats
    total_todos = db.query(Todo).count()
    completed_todos = db.query(Todo).filter(Todo.is_completed == True).count()
    pending_todos = total_todos - completed_todos
    
    todo_stats = TodoStats(
        total_todos=total_todos,
        completed_todos=completed_todos,
        pending_todos=pending_todos
    )
    
    # Habit stats
    total_habits = db.query(Habit).count()
    active_habits = db.query(Habit).filter(Habit.is_active == True).count()
    
    habit_stats = HabitStats(
        total_habits=total_habits,
        active_habits=active_habits
    )
    
    return AdminDashboardStats(
        user_stats=user_stats,
        todo_stats=todo_stats,
        habit_stats=habit_stats
    )

@router.get("/users", response_model=List[UserSchema])
async def get_users(
    skip: int = 0,
    limit: int = 100,
    is_active: Optional[bool] = None,
    is_admin: Optional[bool] = None,
    is_verified: Optional[bool] = None,
    search: Optional[str] = None,
    sort_by: Optional[str] = "created_at",
    sort_order: Optional[str] = "desc",
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_current_admin_user)
):
    query = db.query(User)
    
    # Apply filters
    if is_active is not None:
        query = query.filter(User.is_active == is_active)
    
    if is_admin is not None:
        query = query.filter(User.is_admin == is_admin)
    
    if is_verified is not None:
        query = query.filter(User.is_verified == is_verified)
    
    if search:
        search_filter = or_(
            User.email.contains(search),
            User.full_name.contains(search),
            User.username.contains(search)
        )
        query = query.filter(search_filter)
    
    # Apply sorting
    if sort_order == "desc":
        query = query.order_by(getattr(User, sort_by).desc())
    else:
        query = query.order_by(getattr(User, sort_by).asc())
    
    users = query.offset(skip).limit(limit).all()
    return users

@router.get("/users/{user_id}", response_model=UserSchema)
async def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_current_admin_user)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user

@router.put("/users/{user_id}", response_model=UserSchema)
async def update_user(
    user_id: int,
    user_update: AdminUserUpdate,
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_current_admin_user)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Update fields
    update_data = user_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(user, field, value)
    
    db.commit()
    db.refresh(user)
    return user

@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_current_admin_user)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Prevent admin from deleting themselves
    if user.id == admin_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete yourself"
        )
    
    db.delete(user)
    db.commit()
    return

@router.get("/todos")
async def get_all_todos(
    skip: int = 0,
    limit: int = 100,
    is_completed: Optional[bool] = None,
    priority: Optional[str] = None,
    category: Optional[str] = None,
    user_id: Optional[int] = None,
    search: Optional[str] = None,
    sort_by: Optional[str] = "created_at",
    sort_order: Optional[str] = "desc",
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_current_admin_user)
):
    query = db.query(Todo)
    
    # Apply filters
    if is_completed is not None:
        query = query.filter(Todo.is_completed == is_completed)
    
    if priority:
        query = query.filter(Todo.priority == priority)
    
    if category:
        query = query.filter(Todo.category == category)
    
    if user_id:
        query = query.filter(Todo.owner_id == user_id)
    
    if search:
        search_filter = or_(
            Todo.title.contains(search),
            Todo.description.contains(search)
        )
        query = query.filter(search_filter)
    
    # Apply sorting
    if sort_order == "desc":
        query = query.order_by(getattr(Todo, sort_by).desc())
    else:
        query = query.order_by(getattr(Todo, sort_by).asc())
    
    todos = query.offset(skip).limit(limit).all()
    return todos

@router.get("/habits")
async def get_all_habits(
    skip: int = 0,
    limit: int = 100,
    is_active: Optional[bool] = None,
    frequency: Optional[str] = None,
    user_id: Optional[int] = None,
    search: Optional[str] = None,
    sort_by: Optional[str] = "created_at",
    sort_order: Optional[str] = "desc",
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_current_admin_user)
):
    query = db.query(Habit)
    
    # Apply filters
    if is_active is not None:
        query = query.filter(Habit.is_active == is_active)
    
    if frequency:
        query = query.filter(Habit.frequency == frequency)
    
    if user_id:
        query = query.filter(Habit.owner_id == user_id)
    
    if search:
        search_filter = or_(
            Habit.name.contains(search),
            Habit.description.contains(search)
        )
        query = query.filter(search_filter)
    
    # Apply sorting
    if sort_order == "desc":
        query = query.order_by(getattr(Habit, sort_by).desc())
    else:
        query = query.order_by(getattr(Habit, sort_by).asc())
    
    habits = query.offset(skip).limit(limit).all()
    return habits