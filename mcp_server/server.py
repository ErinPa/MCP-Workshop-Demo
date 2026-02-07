"""MCP Server for Todo Application - provides tools for AI agents to manage todos."""

from typing import Any
from datetime import datetime

import httpx
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP("todo-manager")

# Constants
TODO_API_BASE = "http://localhost:8000/api"
DEFAULT_TIMEOUT = 30.0


async def make_api_request(
    method: str, 
    endpoint: str, 
    json_data: dict[str, Any] | None = None,
    params: dict[str, Any] | None = None
) -> dict[str, Any] | None:
    """Make a request to the Todo API with proper error handling."""
    url = f"{TODO_API_BASE}{endpoint}"
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.request(
                method=method,
                url=url,
                json=json_data,
                params=params,
                timeout=DEFAULT_TIMEOUT
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            return {"error": f"API request failed: {str(e)}"}
        except Exception as e:
            return {"error": f"Unexpected error: {str(e)}"}


def format_todo(todo: dict) -> str:
    """Format a todo item into a readable string."""
    completed_status = "✓ Completed" if todo.get("completed") else "○ Active"
    created = datetime.fromisoformat(todo["created_at"].replace("Z", "+00:00"))
    
    result = f"""
ID: {todo["id"]}
Title: {todo["title"]}
Status: {completed_status}
Priority: {todo["priority"].upper()}
Created: {created.strftime("%Y-%m-%d %H:%M")}
"""
    
    if todo.get("description"):
        result += f"Description: {todo['description']}\n"
    
    if todo.get("completed_at"):
        completed = datetime.fromisoformat(todo["completed_at"].replace("Z", "+00:00"))
        result += f"Completed: {completed.strftime('%Y-%m-%d %H:%M')}\n"
    
    return result.strip()


@mcp.tool()
async def create_todo(
    title: str,
    description: str | None = None,
    priority: str = "medium"
) -> str:
    """Create a new todo item.

    Args:
        title: The title of the todo (required)
        description: Optional detailed description
        priority: Priority level - must be one of: low, medium, high, urgent (default: medium)
    """
    if priority not in ["low", "medium", "high", "urgent"]:
        return f"Error: Invalid priority '{priority}'. Must be one of: low, medium, high, urgent"
    
    todo_data = {
        "title": title,
        "description": description,
        "priority": priority
    }
    
    result = await make_api_request("POST", "/todos", json_data=todo_data)
    
    if result and "error" not in result:
        return f"✓ Todo created successfully!\n{format_todo(result)}"
    
    return f"Failed to create todo: {result.get('error', 'Unknown error')}"


@mcp.tool()
async def list_todos(
    priority: str | None = None,
    completed: bool | None = None,
    limit: int = 50
) -> str:
    """List todos with optional filters.

    Args:
        priority: Filter by priority (low, medium, high, urgent). Leave empty for all priorities
        completed: Filter by completion status (true for completed, false for active). Leave empty for all
        limit: Maximum number of todos to return (default: 50, max: 1000)
    """
    params = {"limit": min(limit, 1000)}
    
    if priority:
        if priority not in ["low", "medium", "high", "urgent"]:
            return f"Error: Invalid priority '{priority}'. Must be one of: low, medium, high, urgent"
        params["priority"] = priority
    
    if completed is not None:
        params["completed"] = str(completed).lower()
    
    result = await make_api_request("GET", "/todos", params=params)
    
    if result and "error" not in result:
        todos = result.get("todos", [])
        total = result.get("total", 0)
        
        if not todos:
            return "No todos found matching the criteria."
        
        formatted_todos = [format_todo(todo) for todo in todos]
        header = f"Found {total} todo(s):\n" + "=" * 50 + "\n"
        return header + "\n---\n".join(formatted_todos)
    
    return f"Failed to list todos: {result.get('error', 'Unknown error')}"


@mcp.tool()
async def get_todo(todo_id: int) -> str:
    """Get details of a specific todo by ID.

    Args:
        todo_id: The ID of the todo to retrieve
    """
    result = await make_api_request("GET", f"/todos/{todo_id}")
    
    if result and "error" not in result:
        return format_todo(result)
    
    return f"Failed to get todo: {result.get('error', 'Todo not found')}"


@mcp.tool()
async def update_todo(
    todo_id: int,
    title: str | None = None,
    description: str | None = None,
    priority: str | None = None
) -> str:
    """Update an existing todo item.

    Args:
        todo_id: The ID of the todo to update
        title: New title (optional)
        description: New description (optional)
        priority: New priority level - low, medium, high, or urgent (optional)
    """
    if priority and priority not in ["low", "medium", "high", "urgent"]:
        return f"Error: Invalid priority '{priority}'. Must be one of: low, medium, high, urgent"
    
    # Build update data with only provided fields
    update_data = {}
    if title is not None:
        update_data["title"] = title
    if description is not None:
        update_data["description"] = description
    if priority is not None:
        update_data["priority"] = priority
    
    if not update_data:
        return "Error: No fields provided to update. Please specify at least one field."
    
    result = await make_api_request("PUT", f"/todos/{todo_id}", json_data=update_data)
    
    if result and "error" not in result:
        return f"✓ Todo updated successfully!\n{format_todo(result)}"
    
    return f"Failed to update todo: {result.get('error', 'Todo not found')}"


@mcp.tool()
async def complete_todo(todo_id: int) -> str:
    """Mark a todo as completed.

    Args:
        todo_id: The ID of the todo to mark as completed
    """
    result = await make_api_request("PATCH", f"/todos/{todo_id}/complete")
    
    if result and "error" not in result:
        return f"✓ Todo marked as completed!\n{format_todo(result)}"
    
    return f"Failed to complete todo: {result.get('error', 'Todo not found')}"


@mcp.tool()
async def delete_todo(todo_id: int) -> str:
    """Delete a todo item permanently.

    Args:
        todo_id: The ID of the todo to delete
    """
    result = await make_api_request("DELETE", f"/todos/{todo_id}")
    
    if result and "error" not in result:
        return f"✓ Todo {todo_id} deleted successfully!"
    
    return f"Failed to delete todo: {result.get('error', 'Todo not found')}"


@mcp.tool()
async def get_priorities() -> str:
    """Get the list of available priority levels for todos."""
    result = await make_api_request("GET", "/priorities")
    
    if result and "error" not in result:
        priorities = result.get("priorities", [])
        return f"Available priority levels: {', '.join(priorities)}"
    
    return f"Failed to get priorities: {result.get('error', 'Unknown error')}"


def main():
    """Initialize and run the MCP server."""
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
