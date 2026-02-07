"""MCP Client Demo - Simplified version focusing on the agentic loop (COMPLETE VERSION)"""

import asyncio
import os
from anthropic import Anthropic
from dotenv import load_dotenv
from mcp import ClientSession

load_dotenv()

# Claude model
ANTHROPIC_MODEL = "claude-sonnet-4-5"


async def process_query(session: ClientSession, anthropic: Anthropic, query: str) -> str:
    """Process a query using Claude and available MCP tools.
    
    This is the core agentic loop that:
    1. Sends the query to Claude with available tools
    2. Executes any tools Claude wants to use
    3. Sends results back to Claude
    4. Repeats until Claude is done (no more tool calls)
    
    Args:
        session: Connected MCP session
        anthropic: Anthropic API client
        query: User's question or request
        
    Returns:
        Claude's final response as a string
    """
    # Start conversation with user's query
    messages = [{"role": "user", "content": query}]
    
    # Get available tools from MCP server
    response = await session.list_tools()
    available_tools = [
        {
            "name": tool.name,
            "description": tool.description,
            "input_schema": tool.inputSchema
        }
        for tool in response.tools
    ]
    
    # Initial Claude API call with tools
    response = anthropic.messages.create(
        model=ANTHROPIC_MODEL,
        max_tokens=4000,
        messages=messages,
        tools=available_tools
    )
    
    # Agentic loop: keep processing until no more tool calls
    final_text = []
    
    while True:
        # Check if Claude wants to use any tools
        tool_uses = [block for block in response.content if block.type == "tool_use"]
        
        if not tool_uses:
            # No more tools to call - extract final answer and exit
            for content in response.content:
                if content.type == "text":
                    final_text.append(content.text)
            break
        
        # Add Claude's response (with tool calls) to conversation
        messages.append({
            "role": "assistant",
            "content": response.content
        })
        
        # Execute all requested tools
        tool_results = []
        for tool_use in tool_uses:
            tool_name = tool_use.name
            tool_args = tool_use.input
            
            print(f"[Executing {tool_name} with {tool_args}]")
            
            # Call the MCP tool
            result = await session.call_tool(tool_name, tool_args)
            
            # Extract text content from result
            result_text = ""
            if isinstance(result.content, list):
                for item in result.content:
                    if hasattr(item, 'text'):
                        result_text += item.text
            else:
                result_text = str(result.content)
            
            # Collect tool result with its ID
            tool_results.append({
                "type": "tool_result",
                "tool_use_id": tool_use.id,
                "content": result_text
            })
        
        # Send tool results back to Claude as a user message
        messages.append({
            "role": "user",
            "content": tool_results
        })
        
        # Get Claude's next response (might have more tool calls or final answer)
        response = anthropic.messages.create(
            model=ANTHROPIC_MODEL,
            max_tokens=4000,
            messages=messages,
            tools=available_tools
        )
    
    return "\n".join(final_text)


async def demo():
    """Demo function - assumes you have a connected MCP session.
    
    In a real implementation, you would:
    1. Connect to the MCP server via stdio
    2. Initialize the session
    3. Run this query processing loop
    
    See client.py for the full implementation with connection setup.
    """
    # This is a simplified demo - in reality you'd connect to your MCP server here
    # For the full version, see client.py
    
    print("This is a simplified demo showing the core agentic loop.")
    print("See client.py for the complete implementation with MCP server connection.")
    print("\nKey concepts demonstrated:")
    print("1. Multi-turn conversation loop")
    print("2. Tool calling and result handling")
    print("3. Building conversation context")


if __name__ == "__main__":
    asyncio.run(demo())
