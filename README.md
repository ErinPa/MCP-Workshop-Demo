# Todo Application

A simple todo application built with FastAPI and SQLite, designed for MCP (Model Context Protocol) server integration demos.

## Features

- ✅ Create, edit, complete, and delete todos
- 🎯 Set priorities (Low, Medium, High, Urgent)
- 🔍 Filter by priority, completion status, and creation date
- 🌐 Web interface for manual management
- 🔌 REST API for programmatic access (perfect for MCP server integration)

## Quick Start

```bash
# Install dependencies
uv sync

# Terminal 1: Start the todo API
uv run uvicorn todoapp.main:app --reload

# Terminal 2: Test with MCP client (requires ANTHROPIC_API_KEY)
export ANTHROPIC_API_KEY=your-api-key-here
uv run python mcp_client/client.py mcp_server/server.py
```

Access the web interface at http://localhost:8000 or API docs at http://localhost:8000/docs

## Installation

1. **Install dependencies with uv:**
   ```bash
   uv sync
   ```

2. **Run the todo application:**
   ```bash
   uv run uvicorn todoapp.main:app --reload
   ```

3. **Run the MCP server (in a separate terminal):**
   ```bash
   uv run python mcp_server/server.py
   ```

4. **Access the application:**
   - Web Interface: http://localhost:8000
   - API Documentation: http://localhost:8000/docs
   - Alternative API Docs: http://localhost:8000/redoc

## Project Structure

```
todoapp/
├── __init__.py          # Package initialization
├── main.py              # FastAPI application and routes
├── models.py            # SQLAlchemy database models
├── schemas.py           # Pydantic request/response schemas
├── database.py          # Database connection and session management
├── crud.py              # Database operations (CRUD)
├── static/              # Frontend files
│   ├── index.html       # Web interface
│   ├── style.css        # Styles
│   └── app.js           # Frontend JavaScript
└── todos.db             # SQLite database (auto-created)
```

## API Endpoints

### Todo Operations

- **POST /api/todos** - Create a new todo
  ```json
  {
    "title": "Buy groceries",
    "description": "Milk, eggs, bread",
    "priority": "medium"
  }
  ```

- **GET /api/todos** - List all todos (with optional filters)
  - Query params: `priority`, `completed`, `created_after`, `created_before`, `skip`, `limit`

- **GET /api/todos/{id}** - Get specific todo

- **PUT /api/todos/{id}** - Update a todo
  ```json
  {
    "title": "Updated title",
    "priority": "high"
  }
  ```

- **PATCH /api/todos/{id}/complete** - Mark todo as complete

- **DELETE /api/todos/{id}** - Delete a todo

### Utility Endpoints

- **GET /api/priorities** - Get list of available priorities
- **GET /api/health** - Health check endpoint

## Database Schema

```sql
Todo:
- id: Integer (Primary Key)
- title: String (required)
- description: String (optional)
- priority: Enum (low, medium, high, urgent)
- completed: Boolean
- created_at: DateTime
- completed_at: DateTime (nullable)
- updated_at: DateTime
```

## MCP Server Integration

This application is designed to be integrated with an MCP server. The MCP server would expose tools that make HTTP requests to these API endpoints:

### MCP Server

The MCP server is located in the `mcp_server/` directory and provides the following tools for AI agents:

1. **create_todo(title, description?, priority?)** - Create a new todo
2. **list_todos(priority?, completed?, limit?)** - List todos with optional filters
3. **get_todo(todo_id)** - Get details of a specific todo
4. **update_todo(todo_id, title?, description?, priority?)** - Update a todo
5. **complete_todo(todo_id)** - Mark a todo as completed
6. **delete_todo(todo_id)** - Delete a todo
7. **get_priorities()** - Get available priority levels

### Running the MCP Server

The MCP server connects to the todo API (which must be running) and exposes these operations through the Model Context Protocol:

```bash
# Terminal 1: Start the todo API
uv run uvicorn todoapp.main:app --reload

# Terminal 2: Run the MCP server
uv run python mcp_server/server.py
```

The MCP server acts as a bridge between AI agents and the todo application, allowing agents to manage todos through natural language commands.

### Using with MCP Clients

#### Claude Desktop

Add this to your Claude Desktop configuration:

**macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`  
**Windows:** `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "todo-manager": {
      "command": "uv",
      "args": ["run", "--directory", "your/path/to/the/repository", "python", "mcp_server/server.py"]
    }
  }
}
```

Restart Claude Desktop, and your todo tools will be available in the tool picker.

#### Cursor

Cursor's MCP configuration location varies. Try these options:

**Option 1: Using uv (Recommended)**

Create `.cursor/mcp_settings.json` in your project root:

```json
{
  "mcpServers": {
    "todo-manager": {
      "command": "/opt/homebrew/bin/uv",
      "args": ["run", "--directory", "your/path/to/the/repository", "python", "mcp_server/server.py"]
    }
  }
}
```

**Option 2: Using shell wrapper**

```json
{
  "mcpServers": {
    "todo-manager": {
      "command": "/bin/sh",
      "args": ["-c", "cd your/path/to/the/repository && uv run python mcp_server/server.py"]
    }
  }
}
```

**Troubleshooting:**
- Replace the path with your actual project path
- Make sure `uv sync` has been run in the project directory to install dependencies
- Check Cursor's output panel for MCP connection errors
- Restart Cursor after changing configuration

## MCP Client (Interactive Testing)

An interactive MCP client is provided to test the server with Claude AI.

### Setup

1. **Set your Anthropic API key:**
   ```bash
   export ANTHROPIC_API_KEY=your-api-key-here
   ```
   
   Or create a `.env` file in the project root:
   ```
   ANTHROPIC_API_KEY=your-api-key-here
   ```

2. **Run the client:**
   ```bash
   # Make sure the todo API is running first
   uv run uvicorn todoapp.main:app --reload
   
   # In another terminal, run the client
   uv run python mcp_client/client.py mcp_server/server.py
   ```

### Usage Examples

Once connected, you can use natural language to manage todos:

```
Query: Create a todo to buy groceries with high priority

Query: List all my active todos

Query: Mark todo 1 as completed

Query: Show me all urgent priority todos

Query: Update todo 2 to have a description "Need to finish by Friday"
```

The client uses Claude to interpret your requests and call the appropriate MCP tools.

## Workshop & Learning Materials

This project includes simplified demo versions to learn and understand MCP concepts:

### MCP Server Workshop Files

- **[mcp_server/server_demo.py](mcp_server/server_demo.py)** - Exercise version with TODO markers and hints
- **[mcp_server/server_demo_filled.py](mcp_server/server_demo_filled.py)** - Complete reference implementation

Focus: Learn how to create an MCP server with a single `list_todos` tool. Covers:
- Initializing FastMCP server
- Making async HTTP requests
- Creating MCP tools with the `@mcp.tool()` decorator
- Handling API responses and formatting output

### MCP Client Workshop Files

- **[mcp_client/client_demo.py](mcp_client/client_demo.py)** - Exercise version focusing on the agentic loop
- **[mcp_client/client_demo_filled.py](mcp_client/client_demo_filled.py)** - Complete reference implementation

Focus: Learn the core orchestration pattern. Covers:
- Multi-turn conversation loop
- Tool calling and result handling
- Building conversation context with messages
- Understanding tool_use and tool_result blocks

These simplified versions skip setup boilerplate and focus on the key concepts, making them ideal for workshops and learning.

### Testing the Demo Files

**Test the MCP server demo with MCP Inspector:**
```bash
# Make sure the Todo API is running first
uv run uvicorn todoapp.main:app --reload

# In another terminal, test the server demo
npx @modelcontextprotocol/inspector uv run python mcp_server/server_demo_filled.py
```

**Test the server demo with the full MCP client:**
```bash
# Make sure the Todo API is running and ANTHROPIC_API_KEY is set
export ANTHROPIC_API_KEY=your-api-key-here
uv run python mcp_client/client.py mcp_server/server_demo_filled.py
```

Then try queries like: `list all todos` or `show me urgent todos`

**Note:** The `client_demo*.py` files are educational code showing the core agentic loop - they don't run standalone. Use the full `client.py` to test with any server.

## Development

### Running in Development Mode

```bash
# With auto-reload
uv run uvicorn todoapp.main:app --reload

# On a different port
uv run uvicorn todoapp.main:app --reload --port 8080

# With specific host
uv run uvicorn todoapp.main:app --reload --host 0.0.0.0
```

### Testing the API

You can test the API using:

1. **Interactive API docs**: http://localhost:8000/docs
2. **curl**:
   ```bash
   # Create a todo
   curl -X POST http://localhost:8000/api/todos \
     -H "Content-Type: application/json" \
     -d '{"title":"Test todo","priority":"high"}'
   
   # List todos
   curl http://localhost:8000/api/todos
   ```

3. **Python requests**:
   ```python
   import requests
   
   # Create todo
   response = requests.post('http://localhost:8000/api/todos', json={
       'title': 'Test todo',
       'priority': 'high'
   })
   print(response.json())
   ```

## Tech Stack

- **FastAPI** - Modern Python web framework
- **SQLAlchemy** - SQL toolkit and ORM
- **SQLite** - Lightweight database
- **Pydantic** - Data validation
- **Uvicorn** - ASGI server
- **Vanilla JavaScript** - Frontend (no framework needed)

## License

MIT
