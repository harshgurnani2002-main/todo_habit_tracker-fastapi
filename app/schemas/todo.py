from pydantic import BaseModel
from datetime import datetime 
from typing import Optional

class TodoBase(BaseModel):
    title:str
    description:str
    priority:Optional[str]='medium'
    category:Optional[str]=None
    due_date:Optional[datetime]=None

class TodoCreate(TodoBase):
    pass

class TodoUpdate(BaseModel):
    title:Optional[str]=None
    description:Optional[str]=None
    is_completed:Optional[bool]=None
    priority:Optional[str]=None
    category:Optional[str]=None
    due_date:Optional[datetime]=None


class Todo(TodoBase):
    id:int
    is_completed:bool
    created_at:datetime
    updated_at:Optional[datetime]=None
    completed_at:Optional[datetime]=None
    owner_id:int

    class Config:
        from_attributes=True
