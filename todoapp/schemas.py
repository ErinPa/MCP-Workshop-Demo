"""Pydantic schemas for request/response validation."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from .models import Priority


class TodoBase(BaseModel):
    """Base schema for Todo items."""
    title: str = Field(..., min_length=1, max_length=200, description="Todo title")
    description: Optional[str] = Field(None, max_length=1000, description="Detailed description")
    priority: Priority = Field(default=Priority.MEDIUM, description="Priority level")


class TodoCreate(TodoBase):
    """Schema for creating a new todo."""
    pass


class TodoUpdate(BaseModel):
    """Schema for updating a todo (all fields optional)."""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    priority: Optional[Priority] = None
    completed: Optional[bool] = None


class TodoResponse(TodoBase):
    """Schema for todo responses."""
    id: int
    completed: bool
    created_at: datetime
    completed_at: Optional[datetime]
    updated_at: datetime
    
    class Config:
        from_attributes = True


class TodoListResponse(BaseModel):
    """Schema for list of todos."""
    todos: list[TodoResponse]
    total: int


class MessageResponse(BaseModel):
    """Generic message response."""
    message: str


class PriorityResponse(BaseModel):
    """Schema for priority list."""
    priorities: list[str]
