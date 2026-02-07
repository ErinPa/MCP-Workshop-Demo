"""MCP Client - Interactive client for testing MCP servers with Claude."""

import asyncio
import os
import sys
from contextlib import AsyncExitStack
from pathlib import Path

from anthropic import Anthropic
from dotenv import load_dotenv
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

load_dotenv()  # load environment variables from .env

# Claude model constant
ANTHROPIC_MODEL = "claude-sonnet-4-5"


class MCPClient:
    """Client for interacting with MCP servers through Claude."""
    
    def __init__(self):
        # Initialize session and client objects
        self.session: ClientSession | None = None
        self.exit_stack = AsyncExitStack()
        self._anthropic: Anthropic | None = None

    @property
    def anthropic(self) -> Anthropic:
        """Lazy-initialize Anthropic client when needed."""
        if self._anthropic is None:
            self._anthropic = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        return self._anthropic

    async def connect_to_server(self, server_script_path: str):
        """Connect to an MCP server.

        Args:
            server_script_path: Path to the server script (.py or .js)
        """
        is_python = server_script_path.endswith(".py")
        is_js = server_script_path.endswith(".js")
        if not (is_python or is_js):
            raise ValueError("Server script must be a .py or .js file")

        if is_python:
            path = Path(server_script_path).resolve()
            server_params = StdioServerParameters(
                command="uv",
                args=["--directory", str(path.parent.parent), "run", "python", str(path)],
                env=None,
            )
        else:
            server_params = StdioServerParameters(
                command="node",
                args=[server_script_path],
                env=None
            )

        stdio_transport = await self.exit_stack.enter_async_context(stdio_client(server_params))
        self.stdio, self.write = stdio_transport
        self.session = await self.exit_stack.enter_async_context(ClientSession(self.stdio, self.write))

        await self.session.initialize()

        # List available tools
        response = await self.session.list_tools()
        tools = response.tools
        print("\nConnected to server with tools:", [tool.name for tool in tools])

    async def process_query(self, query: str) -> str:
        """Process a query using Claude and available tools."""
        messages = [{"role": "user", "content": query}]

        response = await self.session.list_tools()
        available_tools = [
            {
                "name": tool.name,
                "description": tool.description,
                "input_schema": tool.inputSchema
            }
            for tool in response.tools
        ]

        # Initial Claude API call
        response = self.anthropic.messages.create(
            model=ANTHROPIC_MODEL,
            max_tokens=4000,
            messages=messages,
            tools=available_tools
        )

        # Process response and handle tool calls in a loop
        final_text = []
        
        # Keep processing until no more tool calls
        while True:
            # Check if response contains tool calls
            tool_uses = [block for block in response.content if block.type == "tool_use"]
            
            if not tool_uses:
                # No more tool calls, extract final text and break
                for content in response.content:
                    if content.type == "text":
                        final_text.append(content.text)
                break
            
            # Add assistant's response with tool calls to conversation
            messages.append({
                "role": "assistant",
                "content": response.content
            })
            
            # Execute all tool calls and collect results
            tool_results = []
            for tool_use in tool_uses:
                tool_name = tool_use.name
                tool_args = tool_use.input
                
                # Execute tool call
                result = await self.session.call_tool(tool_name, tool_args)
                final_text.append(f"[Calling tool {tool_name} with args {tool_args}]")
                
                # Extract content from result - handle both string and list formats
                if isinstance(result.content, list):
                    # If it's a list of content blocks, extract text
                    content_text = ""
                    for item in result.content:
                        if hasattr(item, 'text'):
                            content_text += item.text
                        elif isinstance(item, dict) and 'text' in item:
                            content_text += item['text']
                        else:
                            content_text += str(item)
                    result_content = content_text
                else:
                    result_content = str(result.content)
                
                # Collect tool result
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": tool_use.id,
                    "content": result_content
                })
            
            # Add tool results as user message
            messages.append({
                "role": "user",
                "content": tool_results
            })
            
            # Get Claude's next response after processing tool results
            response = self.anthropic.messages.create(
                model=ANTHROPIC_MODEL,
                max_tokens=4000,
                messages=messages,
                tools=available_tools
            )

        return "\n".join(final_text)

    async def chat_loop(self):
        """Run an interactive chat loop."""
        print("\n" + "="*60)
        print("MCP Todo Client Started!")
        print("="*60)
        print("\nYou can ask Claude to manage your todos using natural language.")
        print("Examples:")
        print("  - 'Create a todo to buy groceries with high priority'")
        print("  - 'List all my active todos'")
        print("  - 'Mark todo 1 as completed'")
        print("  - 'Show me all urgent todos'")
        print("\nType 'quit' to exit.")
        print("="*60)

        while True:
            try:
                query = input("\nQuery: ").strip()

                if query.lower() == "quit":
                    break

                if not query:
                    continue

                response = await self.process_query(query)
                print("\n" + response)

            except KeyboardInterrupt:
                print("\nExiting...")
                break
            except Exception as e:
                print(f"\nError: {str(e)}")

    async def cleanup(self):
        """Clean up resources."""
        await self.exit_stack.aclose()


async def main():
    """Main entry point for the MCP client."""
    if len(sys.argv) < 2:
        print("Usage: python mcp_client/client.py <path_to_server_script>")
        print("\nExample:")
        print("  python mcp_client/client.py mcp_server/server.py")
        sys.exit(1)

    client = MCPClient()
    try:
        await client.connect_to_server(sys.argv[1])

        # Check if we have a valid API key to continue
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            print("\n" + "="*60)
            print("WARNING: No ANTHROPIC_API_KEY found!")
            print("="*60)
            print("\nTo query these tools with Claude, set your API key:")
            print("  export ANTHROPIC_API_KEY=your-api-key-here")
            print("\nOr create a .env file with:")
            print("  ANTHROPIC_API_KEY=your-api-key-here")
            return

        await client.chat_loop()
    finally:
        await client.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
