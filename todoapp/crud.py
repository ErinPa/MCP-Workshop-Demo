"""CRUD operations for Todo items."""

from datetime import datetime
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import and_
from .models import Todo, Priority
from .schemas import TodoCreate, TodoUpdate


def create_todo(db: Session, todo: TodoCreate) -> Todo:
    """Create a new todo item."""
    db_todo = Todo(
        title=todo.title,
        description=todo.description,
        priority=todo.priority
    )
    db.add(db_todo)
    db.commit()
    db.refresh(db_todo)
    return db_todo


def get_todo(db: Session, todo_id: int) -> Optional[Todo]:
    """Get a single todo by ID."""
    return db.query(Todo).filter(Todo.id == todo_id).first()


def get_todos(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    priority: Optional[Priority] = None,
    completed: Optional[bool] = None,
    created_after: Optional[datetime] = None,
    created_before: Optional[datetime] = None
) -> List[Todo]:
    """Get todos with optional filters."""
    query = db.query(Todo)
    
    # Apply filters
    filters = []
    if priority is not None:
        filters.append(Todo.priority == priority)
    if completed is not None:
        filters.append(Todo.completed == completed)
    if created_after is not None:
        filters.append(Todo.created_at >= created_after)
    if created_before is not None:
        filters.append(Todo.created_at <= created_before)
    
    if filters:
        query = query.filter(and_(*filters))
    
    # Order by created_at descending (newest first)
    query = query.order_by(Todo.created_at.desc())
    
    return query.offset(skip).limit(limit).all()


def get_todos_count(
    db: Session,
    priority: Optional[Priority] = None,
    completed: Optional[bool] = None,
    created_after: Optional[datetime] = None,
    created_before: Optional[datetime] = None
) -> int:
    """Count todos with optional filters."""
    query = db.query(Todo)
    
    # Apply same filters as get_todos
    filters = []
    if priority is not None:
        filters.append(Todo.priority == priority)
    if completed is not None:
        filters.append(Todo.completed == completed)
    if created_after is not None:
        filters.append(Todo.created_at >= created_after)
    if created_before is not None:
        filters.append(Todo.created_at <= created_before)
    
    if filters:
        query = query.filter(and_(*filters))
    
    return query.count()


def update_todo(db: Session, todo_id: int, todo_update: TodoUpdate) -> Optional[Todo]:
    """Update a todo item."""
    db_todo = get_todo(db, todo_id)
    if not db_todo:
        return None
    
    # Update only provided fields
    update_data = todo_update.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(db_todo, field, value)
    
    db_todo.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_todo)
    return db_todo


def complete_todo(db: Session, todo_id: int) -> Optional[Todo]:
    """Mark a todo as completed."""
    db_todo = get_todo(db, todo_id)
    if not db_todo:
        return None
    
    db_todo.completed = True
    db_todo.completed_at = datetime.utcnow()
    db_todo.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(db_todo)
    return db_todo


def delete_todo(db: Session, todo_id: int) -> bool:
    """Delete a todo item."""
    db_todo = get_todo(db, todo_id)
    if not db_todo:
        return False
    
    db.delete(db_todo)
    db.commit()
    return True
