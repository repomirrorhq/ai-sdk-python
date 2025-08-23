# Model Context Protocol (MCP) Integration Guide

The AI SDK Python now includes full support for the Model Context Protocol (MCP), enabling dynamic tool integration with external MCP servers.

## What is MCP?

Model Context Protocol (MCP) is an open standard for AI tool integration that allows language models to securely connect to external data sources and services. MCP servers provide tools that AI models can use dynamically during conversations.

## Key Features

- **Dynamic Tool Loading**: Automatically discover and load tools from MCP servers
- **Secure Communication**: JSON-RPC over STDIO with proper error handling
- **Type Safety**: Full type checking for tool schemas and responses
- **Async Support**: Native async/await integration
- **Easy Integration**: Works seamlessly with existing AI SDK workflows

## Quick Start

### 1. Install an MCP Server

First, install an MCP server. For example, a file system server:

```bash
pip install mcp-server-filesystem
```

### 2. Connect to MCP Server

```python
import asyncio
from ai_sdk import (
    create_mcp_client,
    MCPClientConfig,
    StdioConfig,
)

async def main():
    # Configure MCP client
    config = MCPClientConfig(
        transport=StdioConfig(
            command="mcp-server-filesystem",
            args=["--root", "/path/to/directory"]
        ),
        name="my-ai-app"
    )
    
    # Connect to server
    mcp_client = await create_mcp_client(config)
    
    # Get available tools
    tools = await mcp_client.tools()
    print(f"Available tools: {list(tools.keys())}")
    
    # Close connection
    await mcp_client.close()

asyncio.run(main())
```

### 3. Use MCP Tools with AI Models

```python
from ai_sdk import generate_text, create_openai

async def chat_with_mcp_tools():
    # Setup AI model
    openai = create_openai(api_key="your-key")
    
    # Setup MCP client
    mcp_config = MCPClientConfig(
        transport=StdioConfig(
            command="mcp-server-filesystem",
            args=["--root", "/tmp"]
        )
    )
    mcp_client = await create_mcp_client(mcp_config)
    
    # Get MCP tools
    mcp_tools = await mcp_client.tools()
    
    # Use in AI generation
    response = await generate_text(
        model=openai.chat("gpt-4o-mini"),
        messages=[
            {"role": "user", "content": "List files and read one of them"}
        ],
        tools=list(mcp_tools.values()),
        max_tool_roundtrips=3
    )
    
    print(response.text)
    await mcp_client.close()
```

## Configuration Options

### StdioConfig

Configure connection to STDIO-based MCP servers:

```python
StdioConfig(
    command="mcp-server-command",     # Server command
    args=["--option", "value"],       # Command arguments
    env={"VAR": "value"},             # Environment variables
    cwd="/working/directory"          # Working directory
)
```

### MCPClientConfig

Configure the MCP client:

```python
MCPClientConfig(
    transport=StdioConfig(...),           # Transport configuration
    name="my-client",                     # Client name
    on_uncaught_error=error_handler       # Error callback
)
```

## Available MCP Servers

Popular MCP servers you can use:

### File System Server
```bash
pip install mcp-server-filesystem
```
- **Tools**: read_file, write_file, list_files, create_directory
- **Use Case**: File operations and document processing

### Database Server
```bash
pip install mcp-server-sqlite
```
- **Tools**: query_database, list_tables, describe_table
- **Use Case**: Database queries and data analysis

### Web Search Server
```bash
pip install mcp-server-web-search
```
- **Tools**: search_web, get_page_content
- **Use Case**: Real-time information retrieval

### Custom Server
You can create your own MCP server following the MCP specification.

## Error Handling

```python
from ai_sdk import MCPClientError

try:
    mcp_client = await create_mcp_client(config)
    tools = await mcp_client.tools()
except MCPClientError as e:
    print(f"MCP Error: {e}")
except Exception as e:
    print(f"General Error: {e}")
finally:
    if 'mcp_client' in locals():
        await mcp_client.close()
```

## Advanced Usage

### Custom Error Handling

```python
def handle_mcp_error(error):
    print(f"MCP Error: {error}")
    # Log to monitoring system
    # Send alerts
    # etc.

config = MCPClientConfig(
    transport=stdio_config,
    on_uncaught_error=handle_mcp_error
)
```

### Tool Schema Validation

MCP tools automatically validate input parameters based on the server's JSON schema:

```python
# This will validate that 'path' is provided and is a string
result = await file_tool.execute(path="/path/to/file.txt")
```

### Connection Management

```python
class MCPManager:
    def __init__(self):
        self.clients = {}
    
    async def add_server(self, name, config):
        client = await create_mcp_client(config)
        self.clients[name] = client
        return client
    
    async def get_all_tools(self):
        all_tools = {}
        for name, client in self.clients.items():
            tools = await client.tools()
            for tool_name, tool in tools.items():
                all_tools[f"{name}_{tool_name}"] = tool
        return all_tools
    
    async def close_all(self):
        for client in self.clients.values():
            await client.close()
```

## Best Practices

### 1. Connection Lifecycle
- Always close MCP clients when done
- Use try/finally blocks or async context managers
- Handle connection failures gracefully

### 2. Tool Management
- Prefix tool names when using multiple servers
- Validate tool availability before use
- Handle tool execution failures

### 3. Error Handling
- Implement comprehensive error handling
- Log MCP errors for debugging
- Provide fallback behaviors

### 4. Performance
- Reuse MCP clients when possible
- Cache tool schemas
- Use connection pooling for high-traffic scenarios

## Troubleshooting

### Common Issues

**Server Not Found**
```
MCPClientError: Failed to initialize MCP client: [Errno 2] No such file or directory: 'mcp-server'
```
- Ensure the MCP server is installed and in PATH
- Check server command and arguments

**Connection Timeout**
```
MCPClientError: Request timeout for method 'initialize'
```
- Check server startup time
- Verify server is responsive
- Increase timeout if needed

**Tool Execution Failed**
```
MCPClientError: Failed to execute MCP tool 'read_file': Permission denied
```
- Check tool parameters
- Verify server permissions
- Review server logs

### Debugging

Enable debug logging:

```python
import logging
logging.getLogger("ai_sdk.tools.mcp").setLevel(logging.DEBUG)
```

## Protocol Support

This implementation supports:
- **Protocol Versions**: 2025-06-18, 2025-03-26, 2024-11-05
- **Transport**: STDIO (Subprocess communication)
- **Features**: Tool calling, initialization, notifications
- **Content Types**: Text, images, embedded resources

## Limitations

Current limitations:
- Only STDIO transport (no HTTP/WebSocket yet)
- No server-side request handling
- No session management
- No streaming responses

## Contributing

The MCP implementation is actively developed. Contributions welcome:
- Additional transport types (HTTP, WebSocket)
- Enhanced error handling
- Performance optimizations
- Documentation improvements

## Resources

- [MCP Specification](https://spec.modelcontextprotocol.io/)
- [MCP Server Examples](https://github.com/modelcontextprotocol/servers)
- [AI SDK Documentation](https://ai-sdk.dev/)