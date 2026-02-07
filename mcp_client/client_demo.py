"""MCP Client Demo - Workshop Exercise
Focus on understanding the agentic loop that orchestrates Claude with MCP tools.

GOAL: Complete the core function that makes Claude interact with MCP tools
      in a multi-turn conversation loop.

KEY CONCEPTS:
1. Messages list - Keeps track of the conversation (user, assistant, tool results)
2. Agentic loop - Claude decides → tools execute → results back → repeat
3. Tool use blocks - How Claude requests tool calls
4. Tool results - How we send execution results back to Claude

SIMPLIFIED: This skips connection setup and focuses on the orchestration logic.
"""

import asyncio
from anthropic import Anthropic
from mcp import ClientSession

ANTHROPIC_MODEL = "claude-sonnet-4-5"


async def process_query(session: ClientSession, anthropic: Anthropic, query: str) -> str:
    """Process a query using Claude and available MCP tools.
    
    This is the CORE agentic loop. It orchestrates:
    - Claude making decisions about which tools to use
    - Executing those tools via MCP
    - Feeding results back to Claude
    - Repeating until Claude gives a final answer
    
    Args:
        session: Connected MCP session (can call tools)
        anthropic: Anthropic API client (can call Claude)
        query: User's question or request
        
    Returns:
        Claude's final response as a string
    """
    # TODO: Initialize messages list with the user's query
    # HINT: messages = [{"role": _____, "content": _____}]
    
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
    
    # TODO: Make initial Claude API call
    # HINT: Pass model, max_tokens=4000, messages, and tools=available_tools
    # response = anthropic.messages.create(...)
    
    final_text = []
    
    # Agentic loop - keeps going until Claude stops requesting tools
    # TODO: Add while True loop
    while _____:
        # TODO: Extract all tool_use blocks from response.content
        # HINT: tool_uses = [block for block in response.content if block.type == _____]
        
        # Check if Claude is done (no more tools to call)
        if not tool_uses:
            # TODO: Extract text content from response and add to final_text
            # HINT: Loop through response.content, check if content.type == "text"
            for content in response.content:
                if _____:
                    final_text.append(_____)
            break
        
        # Claude wants to use tools - add its response to conversation
        # TODO: Append assistant message with response.content to messages
        # HINT: messages.append({"role": _____, "content": _____})
        
        # Execute all tools Claude requested
        tool_results = []
        for tool_use in tool_uses:
            tool_name = tool_use.name
            tool_args = tool_use.input
            
            print(f"[Executing {tool_name} with {tool_args}]")
            
            # TODO: Call the MCP tool using session.call_tool()
            # HINT: result = await session.call_tool(_____, _____)
            
            # Extract text from result (MCP returns content blocks)
            result_text = ""
            if isinstance(result.content, list):
                for item in result.content:
                    if hasattr(item, 'text'):
                        result_text += item.text
            else:
                result_text = str(result.content)
            
            # TODO: Build tool result dictionary with type, tool_use_id, and content
            # HINT: The tool_use_id links this result to Claude's request (tool_use.id)
            # tool_results.append({
            #     "type": _____,
            #     "tool_use_id": _____,
            #     "content": _____
            # })
        
        # TODO: Send tool results back to Claude as a user message
        # HINT: messages.append({"role": _____, "content": _____})
        
        # TODO: Get Claude's next response (might call more tools or give final answer)
        # HINT: Same API call as before - Claude will see the tool results in messages
        # response = anthropic.messages.create(...)
    
    return "\n".join(final_text)


async def demo():
    """Demo function showing what this code does."""
    print("""
MCP CLIENT AGENTIC LOOP DEMO
============================

This demonstrates the core orchestration pattern:

1. USER QUERY → Claude
   User: "Create a high priority todo"
   
2. CLAUDE DECIDES → Tool call
   Claude: "I'll use create_todo(title='...', priority='high')"
   
3. EXECUTE TOOL → MCP Server → Todo API
   Result: "✓ Todo created successfully! ID: 1"
   
4. RESULT → Claude
   Claude sees the result and can:
   - Call more tools (multi-turn)
   - Give final answer
   
5. REPEAT until Claude gives final text response

KEY PATTERN:
- Messages list grows: user → assistant → user → assistant → ...
- Assistant messages can contain tool_use blocks
- User messages can contain tool_result blocks
- Loop continues until assistant returns pure text

Fill in the TODOs above to complete the agentic loop!
""")


if __name__ == "__main__":
    asyncio.run(demo())


"""
TESTING:
This is a simplified version. To test the real implementation:
    uv run python mcp_client/client.py mcp_server/server.py

WHAT YOU LEARNED:
✓ How Claude decides which tools to call
✓ How tool results flow back into the conversation
✓ Why we need a loop (multi-turn tool usage)
✓ Message structure (role + content)
✓ Tool result format (type, tool_use_id, content)

NEXT STEPS:
Look at client.py to see:
- How to connect to an MCP server
- How to handle user input in a chat loop
- Full error handling
"""
