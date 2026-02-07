"""MCP Server Demo - Workshop Exercise
Complete this simplified MCP server with only a list_todos tool.

GOAL: Learn how to create an MCP server that exposes a tool to list todos
      from the Todo API running on localhost:8000

STEPS:
1. Import required libraries
2. Initialize the MCP server
3. Create a helper function to make API requests
4. Create the list_todos tool with the @mcp.tool() decorator
5. Implement the main() function to run the server
"""

from typing import Any

import httpx
# TODO: Import FastMCP from mcp.server.fastmcp
# HINT: from mcp.server.fastmcp import _____

# TODO: Initialize FastMCP server with the name "todo-demo"
# HINT: mcp = FastMCP(_____)

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
    
    Args:
        method: HTTP method (GET, POST, etc.)
        endpoint: API endpoint path (e.g., "/todos")
        params: Optional query parameters
        
    Returns:
        dict with the API response, or dict with "error" key if request failed
    """
    # TODO: Build the full URL by combining TODO_API_BASE and endpoint
    # HINT: url = f"{_____}{_____}"
    
    # Create an async HTTP client and make the request
    async with httpx.AsyncClient() as client:
        try:
            # TODO: Make the HTTP request using client.request()
            # HINT: Pass method, url, params, and timeout
            # response = await client.request(...)
            
            # TODO: Raise an exception if the response status is an error
            # HINT: response.raise_for_status()
            
            # TODO: Return the JSON response
            # HINT: return response._____()
            
        except httpx.HTTPError as e:
            return {"error": f"API request failed: {str(e)}"}
        except Exception as e:
            return {"error": f"Unexpected error: {str(e)}"}


# TODO: Add the @mcp.tool() decorator to register this function as an MCP tool
# HINT: @mcp._____()
async def list_todos(
    priority: str | None = None,
    completed: bool | None = None,
    limit: int = 50
) -> str:
    """List todos with optional filters.
    
    This is an MCP tool that AI agents can call. The docstring is important
    because it tells the AI what this tool does and how to use it.

    Args:
        priority: Filter by priority (low, medium, high, urgent). Leave empty for all priorities
        completed: Filter by completion status (true for completed, false for active). Leave empty for all
        limit: Maximum number of todos to return (default: 50, max: 1000)
        
    Returns:
        A formatted string with the list of todos, or an error message
    """
    # Build query parameters dictionary
    # TODO: Create params dict with limit (capped at 1000)
    # HINT: params = {"limit": min(_____, _____)}
    
    # Add optional filters to params
    if priority:
        # Validate priority value
        if priority not in ["low", "medium", "high", "urgent"]:
            return f"Error: Invalid priority '{priority}'. Must be one of: low, medium, high, urgent"
        # TODO: Add priority to params dict
        # HINT: params["_____"] = priority
    
    if completed is not None:
        # TODO: Add completed to params as a lowercase string
        # HINT: params["completed"] = str(completed)._____()
    
    # Make API request to get todos
    # TODO: Call make_api_request with method "GET", endpoint "/todos", and params
    # HINT: result = await make_api_request(_____, _____, params=_____)
    
    # Handle response
    if result and "error" not in result:
        # TODO: Extract the "todos" list from result (default to empty list)
        # HINT: todos = result.get(_____, [])
        
        # TODO: Extract the "total" count from result (default to 0)
        # HINT: total = result.get(_____, 0)
        
        if not todos:
            return "No todos found matching the criteria."
        
        # Format todos for display
        output = [f"Found {total} todo(s):\n" + "=" * 50]
        
        for todo in todos:
            # TODO: Set status to "✓ Completed" if completed, else "○ Active"
            # HINT: status = "✓ Completed" if todo.get(_____) else "○ Active"
            
            # Format each todo with its details
            output.append(f"""
ID: {todo['id']}
Title: {todo['title']}
Status: {status}
Priority: {todo['priority'].upper()}
""".strip())
        
        # TODO: Join all output strings with separator "\n---\n"
        # HINT: return "\n---\n"._____(output)
    
    # Return error message if request failed
    return f"Failed to list todos: {result.get('error', 'Unknown error')}"


def main():
    """Initialize and run the MCP server.
    
    The server runs using stdio transport, which means it communicates
    via standard input/output. This is how MCP clients connect to it.
    MCP clients (like Claude Desktop or our custom client) will start
    this script and communicate with it through stdin/stdout.
    """
    # TODO: Run the MCP server with stdio transport
    # HINT: mcp.run(transport=_____)


if __name__ == "__main__":
    main()


"""
TESTING YOUR MCP SERVER:

1. Make sure the Todo API is running:
   Terminal 1: uv run uvicorn todoapp.main:app --reload

2. Test with the MCP Inspector:
   Terminal 2: npx @modelcontextprotocol/inspector uv run python mcp_server/demo.py

3. Or test with the MCP client:
   Terminal 2: uv run python mcp_client/client.py mcp_server/demo.py

BONUS CHALLENGES:
- Add error handling for network timeouts
- Add a max_retries parameter to retry failed requests
- Format the output differently (e.g., as a table or JSON)
- Add additional filters (created_after, created_before)
"""
