"""
Example demonstrating SSE (Server-Sent Events) MCP transport.

This example shows how to connect to an MCP server using SSE transport
for web-based MCP servers.
"""

import asyncio
from ai_sdk import (
    MCPClient,
    MCPClientConfig,
    SSEMCPTransport,
    SSEConfig,
    generate_text,
    create_openai
)


async def sse_mcp_example():
    """Example using SSE MCP transport."""
    
    # Create SSE transport configuration
    sse_config = SSEConfig(
        url="https://example.com/mcp/events",  # Replace with actual MCP server URL
        headers={
            "Authorization": "Bearer your-token",  # Add authentication if needed
            "X-Client-Name": "ai-sdk-python"
        }
    )
    
    # Create SSE transport
    transport = SSEMCPTransport(sse_config)
    
    # Create MCP client
    client_config = MCPClientConfig(
        name="ai-sdk-python",
        version="0.2.0"
    )
    
    mcp_client = MCPClient(transport, client_config)
    
    try:
        print("Connecting to MCP server via SSE...")
        await mcp_client.connect()
        print("✅ Connected successfully!")
        
        # List available tools
        tools = await mcp_client.list_tools()
        print(f"📋 Available tools: {[tool.name for tool in tools]}")
        
        if tools:
            # Create OpenAI provider
            openai = create_openai()
            
            # Convert MCP tools for use with generate_text
            mcp_tools = mcp_client.get_tool_set()
            
            # Generate text using the tools
            result = await generate_text(
                model=openai.language_model("gpt-4"),
                messages=[{
                    "role": "user", 
                    "content": "Use the available tools to help me with my task."
                }],
                tools=mcp_tools.tools,
                max_tool_calls=3
            )
            
            print(f"🤖 Response: {result.text}")
            
            if result.tool_calls:
                print("🔧 Tool calls made:")
                for call in result.tool_calls:
                    print(f"  - {call.tool_name}: {call.arguments}")
                    print(f"    Result: {call.result}")
    
    except Exception as e:
        print(f"❌ Error: {e}")
    
    finally:
        # Always disconnect
        await mcp_client.disconnect()
        print("🔌 Disconnected from MCP server")


async def minimal_sse_example():
    """Minimal example with SSE transport."""
    
    sse_config = SSEConfig(url="https://your-mcp-server.com/events")
    transport = SSEMCPTransport(sse_config)
    
    # Set up event handlers
    def on_message(message):
        print(f"📨 Received: {message}")
    
    def on_error(error):
        print(f"❌ Error: {error}")
    
    def on_close():
        print("🔌 Connection closed")
    
    transport.onmessage = on_message
    transport.onerror = on_error
    transport.onclose = on_close
    
    try:
        await transport.start()
        print("✅ SSE transport started")
        
        # Send a test message
        test_message = {
            "jsonrpc": "2.0",
            "method": "test",
            "params": {"message": "Hello from Python!"},
            "id": 1
        }
        
        await transport.send(test_message)
        print("📤 Test message sent")
        
        # Keep connection open for a bit
        await asyncio.sleep(5)
        
    finally:
        await transport.stop()
        print("⏹️ Transport stopped")


if __name__ == "__main__":
    print("🌊 SSE MCP Transport Examples")
    print("=" * 40)
    
    # Run the examples
    print("\n1. Basic SSE Transport Example:")
    asyncio.run(minimal_sse_example())
    
    print("\n2. Full MCP Client with SSE Example:")
    print("   (This would run with a real MCP server)")
    # Uncomment the line below when you have a real MCP server URL
    # asyncio.run(sse_mcp_example())