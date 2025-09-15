from fastapi import APIRouter,Depends,HTTPException,status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from typing import List, Optional
from datetime import datetime, date
from app.database import get_db 
from app.models.user import User
from app.models.todo import Todo
from app.schemas.todo import TodoCreate,TodoUpdate, Todo as TodoSchema
from app.auth.dependencies import get_current_active_user
from typing import Optional


router=APIRouter(
    prefix="/todos",
    tags=["todos"]
)


@router.post("/",response_model=TodoSchema)
async def create_todo(todo:TodoCreate,db:Session=Depends(get_db),current_user:User=Depends(get_current_active_user)):
    new_todo=Todo(**todo.dict(),owner_id=current_user.id)
    db.add(new_todo)
    db.commit()
    db.refresh(new_todo)
    return new_todo


@router.get("/",response_model=List[TodoSchema])
async def get_todos(
    skip: int = 0,
    limit: int = 50,
    completed: Optional[bool] = None,
    priority: Optional[str] = Query(None, description="Filter by priority (low, medium, high)"),
    category: Optional[str] = Query(None, description="Filter by category"),
    search: Optional[str] = Query(None, description="Search in title or description"),
    due_date_from: Optional[date] = None,
    due_date_to: Optional[date] = None,
    created_from: Optional[date] = None,
    created_to: Optional[date] = None,
    sort_by: Optional[str] = Query("created_at", description="Sort by field"),
    sort_order: Optional[str] = Query("desc", description="Sort order (asc or desc)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    query = db.query(Todo).filter(Todo.owner_id == current_user.id)
    
    # Apply filters
    if completed is not None:
        query = query.filter(Todo.is_completed == completed)
    
    if priority:
        query = query.filter(Todo.priority == priority)
    
    if category:
        query = query.filter(Todo.category == category)
    
    if search:
        search_filter = or_(
            Todo.title.contains(search),
            Todo.description.contains(search)
        )
        query = query.filter(search_filter)
    
    if due_date_from:
        query = query.filter(Todo.due_date >= due_date_from)
    
    if due_date_to:
        query = query.filter(Todo.due_date <= due_date_to)
    
    if created_from:
        query = query.filter(func.date(Todo.created_at) >= created_from)
    
    if created_to:
        query = query.filter(func.date(Todo.created_at) <= created_to)
    
    # Apply sorting
    if sort_order == "desc":
        query = query.order_by(getattr(Todo, sort_by).desc())
    else:
        query = query.order_by(getattr(Todo, sort_by).asc())
    
    todos = query.offset(skip).limit(limit).all()
    return todos

@router.get("/{todo_id}",response_model=TodoSchema)
async def get_todo(todo_id:int,db:Session=Depends(get_db),current_user:User=Depends(get_current_active_user)):
    todo=db.query(Todo).filter(Todo.id==todo_id,Todo.owner_id==current_user.id).first()
    if todo is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Todo not found")
    return todo


@router.put("/{todo_id}", response_model=TodoSchema)
async def update_todo(
    todo_id: int,
    todo_update: TodoUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    todo = db.query(Todo).filter(
        Todo.id == todo_id,
        Todo.owner_id == current_user.id
    ).first()
    
    if not todo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Todo not found"
        )
    
    # Update fields
    update_data = todo_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(todo, field, value)
    
    # Set completion timestamp
    if todo_update.is_completed is not None:
        if todo_update.is_completed and not todo.is_completed:
            todo.completed_at = datetime.now()
        elif not todo_update.is_completed and todo.is_completed:
            todo.completed_at = None
    
    db.commit()
    db.refresh(todo)
    return todo


@router.delete("/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(
    todo_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    todo = db.query(Todo).filter(
        Todo.id == todo_id,
        Todo.owner_id == current_user.id
    ).first()
    
    if not todo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Todo not found"
        )
    
    db.delete(todo)
    db.commit()