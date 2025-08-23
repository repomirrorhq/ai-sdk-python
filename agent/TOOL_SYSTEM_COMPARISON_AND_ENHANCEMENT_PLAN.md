# Tool System: TypeScript vs Python Comparison and Enhancement Plan

## Current State Analysis

### Python Tool System Status
The Python tool system is reasonably well developed with:
- ✅ Core Tool, ToolCall, ToolResult classes
- ✅ tool() and dynamic_tool() helper functions  
- ✅ simple_tool decorator
- ✅ ToolRegistry for managing tool collections
- ✅ Tool execution engine with async support
- ✅ Schema validation and input/output handling
- ✅ Integration with enhanced generate_text

### Key Differences from TypeScript

#### 1. **Schema System Flexibility**
- **TypeScript**: Uses FlexibleSchema that supports Zod, JSON Schema, etc.
- **Python**: Only supports JSON Schema via dictionaries, no Pydantic integration

#### 2. **Tool Types**
- **TypeScript**: Multiple tool types (`function`, `dynamic`, `provider-defined`)
- **Python**: Basic support for static and dynamic tools, no provider-defined tools

#### 3. **Streaming Callbacks**
- **TypeScript**: Rich streaming callbacks (`onInputStart`, `onInputDelta`, `onInputAvailable`)
- **Python**: Limited streaming callback support

#### 4. **Provider Integration**
- **TypeScript**: Deep provider integration with `providerOptions`, `toModelOutput`
- **Python**: Basic provider integration

#### 5. **MCP (Model Context Protocol) Support**
- **TypeScript**: Full MCP client implementation with transport layers
- **Python**: No MCP support

#### 6. **Advanced Tool Features**
- **TypeScript**: Tool call repair, tool result conversion, complex type inference
- **Python**: Basic tool functionality

## Enhancement Plan

### Phase 1: Core Improvements (High Priority)

#### 1.1 Enhanced Schema Support
```python
from typing import Union
from pydantic import BaseModel

FlexibleSchema = Union[
    Dict[str, Any],           # JSON Schema
    Type[BaseModel],          # Pydantic model
    # Could add Zod-like schema in future
]

def normalize_schema(schema: FlexibleSchema) -> Dict[str, Any]:
    """Convert various schema types to JSON schema."""
    if isinstance(schema, type) and issubclass(schema, BaseModel):
        return schema.model_json_schema()
    return schema
```

#### 1.2 Provider-Defined Tools
```python
class ProviderDefinedTool(Tool):
    """Tool defined by a provider with specific configuration."""
    
    type: str = "provider-defined"
    id: str  # Format: "provider.tool_name"
    args: Dict[str, Any]  # Provider-specific configuration
```

#### 1.3 Enhanced Streaming Support
```python
class StreamingCallbacks:
    """Callbacks for streaming tool interactions."""
    
    on_input_start: Optional[Callable[[ToolCallOptions], None]] = None
    on_input_delta: Optional[Callable[[str, ToolCallOptions], None]] = None  
    on_input_available: Optional[Callable[[Any, ToolCallOptions], None]] = None
```

### Phase 2: Advanced Features (Medium Priority)

#### 2.1 MCP (Model Context Protocol) Support
```python
class MCPClient:
    """Client for Model Context Protocol interactions."""
    
    async def list_tools(self) -> List[Dict[str, Any]]:
        """List available tools from MCP server."""
    
    async def call_tool(self, name: str, arguments: Dict[str, Any]) -> Any:
        """Call a tool via MCP."""

class MCPTransport:
    """Transport layer for MCP communication."""
    pass

class MCPSSETransport(MCPTransport):
    """Server-sent events transport for MCP."""
    pass
```

#### 2.2 Tool Result Conversion
```python
class ToolResultConverter:
    """Convert tool results for model consumption."""
    
    @staticmethod
    def to_model_output(
        result: Any, 
        converter: Optional[Callable[[Any], Any]] = None
    ) -> Dict[str, Any]:
        """Convert tool result to model-compatible format."""
```

#### 2.3 Advanced Tool Decorators
```python
def pydantic_tool(
    model: Type[BaseModel],
    description: Optional[str] = None,
    name: Optional[str] = None
):
    """Decorator that creates a tool from Pydantic model."""
    def decorator(func):
        return Tool(
            name=name or func.__name__,
            description=description or func.__doc__ or "",
            input_schema=model.model_json_schema(),
            execute=func
        )
    return decorator

def streaming_tool(
    name: str,
    description: str, 
    input_schema: FlexibleSchema
):
    """Decorator for tools that support streaming callbacks."""
```

### Phase 3: Advanced Capabilities (Lower Priority)

#### 3.1 Tool Composition and Chaining
```python
class ToolChain:
    """Chain multiple tools together."""
    
    def add_tool(self, tool: Tool) -> 'ToolChain':
        """Add a tool to the chain."""
    
    async def execute_chain(self, input_data: Any) -> Any:
        """Execute the tool chain."""

def compose_tools(*tools: Tool) -> ToolChain:
    """Compose multiple tools into a chain."""
```

#### 3.2 Tool Validation and Testing
```python
class ToolValidator:
    """Validate tool definitions and behavior."""
    
    def validate_tool(self, tool: Tool) -> List[str]:
        """Validate a tool definition."""
    
    async def test_tool(self, tool: Tool, test_inputs: List[Any]) -> List[Any]:
        """Test a tool with various inputs."""
```

#### 3.3 Tool Analytics and Monitoring
```python
class ToolAnalytics:
    """Analytics and monitoring for tool usage."""
    
    def track_execution(self, tool_name: str, duration: float, success: bool):
        """Track tool execution metrics."""
    
    def get_usage_stats(self) -> Dict[str, Any]:
        """Get tool usage statistics."""
```

## Missing Features to Implement

### Immediate (This Session)
1. ✅ Create comparison analysis
2. 🔄 Enhanced schema support with Pydantic integration
3. 🔄 Provider-defined tools
4. 🔄 Streaming callbacks support

### Next Session
1. MCP client implementation
2. Tool result conversion system
3. Advanced decorators
4. Tool composition system

### Future Sessions
1. Tool validation and testing framework
2. Analytics and monitoring
3. Performance optimizations
4. Advanced type inference

## Implementation Priority

### Core Enhancements
1. **Pydantic Schema Integration**: Critical for better type safety
2. **Provider-Defined Tools**: Important for provider ecosystem
3. **Streaming Callbacks**: Better real-time tool interaction
4. **Tool Result Conversion**: Better model integration

### Advanced Features
1. **MCP Support**: Future-proofing for protocol adoption
2. **Tool Composition**: Advanced workflow capabilities
3. **Validation Framework**: Better developer experience
4. **Analytics**: Production monitoring

## Success Criteria
- [ ] Full schema flexibility (JSON Schema + Pydantic)
- [ ] Provider-defined tools working with at least one provider
- [ ] Streaming callbacks integrated with enhanced generate_text
- [ ] MCP client can connect to MCP servers
- [ ] Tool composition enables complex workflows
- [ ] Performance comparable to TypeScript version
- [ ] All tool examples pass

## Files to Modify/Create
1. `src/ai_sdk/tools/core.py` - Enhanced Tool class with new features
2. `src/ai_sdk/tools/schema.py` - Flexible schema system
3. `src/ai_sdk/tools/streaming.py` - Streaming callback support
4. `src/ai_sdk/tools/mcp/` - MCP client implementation
5. `src/ai_sdk/tools/decorators.py` - Advanced decorators
6. `src/ai_sdk/tools/composition.py` - Tool composition system
7. Update examples and tests

## TypeScript Features to Port
- FlexibleSchema support with multiple schema types
- Provider-defined tools with configuration
- Rich streaming callbacks for real-time interaction
- MCP (Model Context Protocol) client and transport
- Tool result conversion for model compatibility
- Advanced type inference and validation
- Tool composition and chaining capabilities