"""FastAPI application for Todo management."""

from datetime import datetime
from typing import Optional
from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from pathlib import Path

from . import crud
from .database import get_db, init_db
from .models import Priority
from .schemas import (
    TodoCreate,
    TodoUpdate,
    TodoResponse,
    TodoListResponse,
    MessageResponse,
    PriorityResponse
)

# Create FastAPI app
app = FastAPI(
    title="Todo API",
    description="A simple Todo application with REST API for MCP server integration",
    version="0.1.0"
)

# Initialize database on startup
@app.on_event("startup")
def startup_event():
    init_db()


# Mount static files
static_path = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=str(static_path)), name="static")


# Root endpoint - serve the frontend
@app.get("/", include_in_schema=False)
async def read_root():
    """Serve the main HTML page."""
    return FileResponse(str(static_path / "index.html"))


# API Endpoints
@app.post("/api/todos", response_model=TodoResponse, status_code=201)
def create_todo(todo: TodoCreate, db: Session = Depends(get_db)):
    """Create a new todo item."""
    return crud.create_todo(db, todo)


@app.get("/api/todos", response_model=TodoListResponse)
def list_todos(
    skip: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of items to return"),
    priority: Optional[Priority] = Query(None, description="Filter by priority"),
    completed: Optional[bool] = Query(None, description="Filter by completion status"),
    created_after: Optional[datetime] = Query(None, description="Filter by creation date (after)"),
    created_before: Optional[datetime] = Query(None, description="Filter by creation date (before)"),
    db: Session = Depends(get_db)
):
    """List todos with optional filters."""
    todos = crud.get_todos(
        db,
        skip=skip,
        limit=limit,
        priority=priority,
        completed=completed,
        created_after=created_after,
        created_before=created_before
    )
    total = crud.get_todos_count(
        db,
        priority=priority,
        completed=completed,
        created_after=created_after,
        created_before=created_before
    )
    return TodoListResponse(todos=todos, total=total)


@app.get("/api/todos/{todo_id}", response_model=TodoResponse)
def get_todo(todo_id: int, db: Session = Depends(get_db)):
    """Get a specific todo by ID."""
    todo = crud.get_todo(db, todo_id)
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    return todo


@app.put("/api/todos/{todo_id}", response_model=TodoResponse)
def update_todo(todo_id: int, todo_update: TodoUpdate, db: Session = Depends(get_db)):
    """Update a todo item."""
    todo = crud.update_todo(db, todo_id, todo_update)
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    return todo


@app.patch("/api/todos/{todo_id}/complete", response_model=TodoResponse)
def complete_todo(todo_id: int, db: Session = Depends(get_db)):
    """Mark a todo as completed."""
    todo = crud.complete_todo(db, todo_id)
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    return todo


@app.delete("/api/todos/{todo_id}", response_model=MessageResponse)
def delete_todo(todo_id: int, db: Session = Depends(get_db)):
    """Delete a todo item."""
    success = crud.delete_todo(db, todo_id)
    if not success:
        raise HTTPException(status_code=404, detail="Todo not found")
    return MessageResponse(message=f"Todo {todo_id} deleted successfully")


@app.get("/api/priorities", response_model=PriorityResponse)
def get_priorities():
    """Get list of available priority levels."""
    return PriorityResponse(priorities=[p.value for p in Priority])


# Health check endpoint
@app.get("/api/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}
