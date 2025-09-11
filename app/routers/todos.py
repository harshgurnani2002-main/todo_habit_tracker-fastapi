from fastapi import APIRouter,Depends,HTTPException,status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime 
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
async def get_todos(skip:int=0,limit:int=50,completed: Optional[bool] = None,db:Session=Depends(get_db),current_user:User=Depends(get_current_active_user)):
    query=db.query(Todo).filter(Todo.owner_id==current_user.id)
    if completed is not None:
        query=query.filter(Todo.completed==completed)
    todos=query.offset(skip).limit(limit).all()
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