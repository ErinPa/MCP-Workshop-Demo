"""MCP Server Demo - Simplified version with only list_todos tool (COMPLETE VERSION)"""

from typing import Any

import httpx
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP server with a name
mcp = FastMCP("todo-demo")

# API endpoint configuration
TODO_API_BASE = "http://localhost:8000/api"
DEFAULT_TIMEOUT = 30.0


async def make_api_request(
    method: str, 
    endpoint: str, 
    params: dict[str, Any] | None = None
) -> dict[str, Any] | None:
    """Make a request to the Todo API with proper error handling.
    
    This helper function handles all HTTP communication with the Todo API.
    It uses httpx for async HTTP requests and includes error handling.
    """
    url = f"{TODO_API_BASE}{endpoint}"
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.request(
                method=method,
                url=url,
                params=params,
                timeout=DEFAULT_TIMEOUT
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            return {"error": f"API request failed: {str(e)}"}
        except Exception as e:
            return {"error": f"Unexpected error: {str(e)}"}


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
    # Build query parameters
    params = {"limit": min(limit, 1000)}
    
    if priority:
        if priority not in ["low", "medium", "high", "urgent"]:
            return f"Error: Invalid priority '{priority}'. Must be one of: low, medium, high, urgent"
        params["priority"] = priority
    
    if completed is not None:
        params["completed"] = str(completed).lower()
    
    # Make API request
    result = await make_api_request("GET", "/todos", params=params)
    
    # Handle response
    if result and "error" not in result:
        todos = result.get("todos", [])
        total = result.get("total", 0)
        
        if not todos:
            return "No todos found matching the criteria."
        
        # Format todos for display
        output = [f"Found {total} todo(s):\n" + "=" * 50]
        
        for todo in todos:
            status = "✓ Completed" if todo.get("completed") else "○ Active"
            output.append(f"""
ID: {todo['id']}
Title: {todo['title']}
Status: {status}
Priority: {todo['priority'].upper()}
""".strip())
        
        return "\n---\n".join(output)
    
    return f"Failed to list todos: {result.get('error', 'Unknown error')}"


def main():
    """Initialize and run the MCP server.
    
    The server runs using stdio transport, which means it communicates
    via standard input/output. This is how MCP clients connect to it.
    """
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
