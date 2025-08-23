"""Example demonstrating MCP (Model Context Protocol) integration with AI SDK Python.

This example shows how to:
1. Connect to an MCP server
2. Dynamically load tools from the server
3. Use MCP tools in AI SDK workflows

Prerequisites:
- An MCP server running (e.g., a file system server)
- The server command available in your PATH
"""

import asyncio
import os
from ai_sdk import (
    generate_text,
    create_openai,
    create_mcp_client,
    MCPClientConfig,
    StdioConfig,
)

async def main():
    """Main example function."""
    print("🔧 MCP Integration Example")
    print("=" * 40)
    
    # Create OpenAI provider
    openai = create_openai(api_key=os.getenv("OPENAI_API_KEY"))
    
    try:
        # Example 1: File system MCP server
        print("\n1. Connecting to MCP File System Server...")
        
        # Configure MCP client for a hypothetical file system server
        mcp_config = MCPClientConfig(
            transport=StdioConfig(
                command="mcp-server-filesystem",  # Example MCP server
                args=["--root", "/tmp/mcp-demo"],
                env={"MCP_LOG_LEVEL": "info"}
            ),
            name="ai-sdk-python-client",
            on_uncaught_error=lambda error: print(f"MCP Error: {error}")
        )
        
        # Create and connect to MCP client
        mcp_client = await create_mcp_client(mcp_config)
        print("✅ Connected to MCP server")
        
        # Get available tools from MCP server
        print("\n2. Loading tools from MCP server...")
        mcp_tools = await mcp_client.tools()
        
        print(f"📦 Loaded {len(mcp_tools)} tools:")
        for tool_name, tool in mcp_tools.items():
            print(f"  - {tool_name}: {tool.description}")
        
        # Example 3: Use MCP tools with AI SDK
        print("\n3. Using MCP tools in AI workflow...")
        
        response = await generate_text(
            model=openai.chat("gpt-4o-mini"),
            messages=[
                {
                    "role": "user",
                    "content": "Please list the files in the current directory and then read one of them."
                }
            ],
            tools=list(mcp_tools.values()),  # Use all MCP tools
            max_tool_roundtrips=3,
        )
        
        print("\n📄 AI Response:")
        print(response.text)
        
        # Show tool calls that were made
        if response.tool_calls:
            print(f"\n🔧 Tool calls made: {len(response.tool_calls)}")
            for i, tool_call in enumerate(response.tool_calls, 1):
                print(f"  {i}. {tool_call.tool_name}({tool_call.args})")
                print(f"     Result: {tool_call.result}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("Note: This example requires an MCP server to be available.")
        print("You can install one with: pip install mcp-server-filesystem")
        
    finally:
        # Clean up MCP connection
        try:
            await mcp_client.close()
            print("\n🔌 Disconnected from MCP server")
        except:
            pass

async def demo_mock_mcp():
    """Demo with a mock MCP server setup (for testing)."""
    print("\n" + "=" * 40)
    print("🧪 Mock MCP Server Demo")
    print("=" * 40)
    
    print("This would demonstrate MCP with a mock server...")
    print("In a real scenario, you would:")
    print("1. Start an MCP server (e.g., file system, database, API)")
    print("2. Connect using StdioConfig with the server command")
    print("3. The AI model gets access to all server tools automatically")
    print("4. Tools are called dynamically based on user requests")

if __name__ == "__main__":
    # Check for OpenAI API key
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  Please set OPENAI_API_KEY environment variable")
        print("   export OPENAI_API_KEY='your-api-key'")
        exit(1)
    
    # Run the example
    asyncio.run(main())
    
    # Run mock demo
    asyncio.run(demo_mock_mcp())