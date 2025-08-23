# Generate Text: TypeScript vs Python Comparison and Enhancement Plan

## Key Differences Identified

### 1. **Multi-step Tool Calling**
- **TypeScript**: Full multi-step tool calling with retry loops, tool execution, and step-by-step processing
- **Python**: Basic single-step generation, no multi-step tool calling workflow

### 2. **Advanced Features Missing in Python**
- **Steps System**: TS has a comprehensive steps system with `StepResult` objects
- **Tool Execution**: No built-in tool execution engine in Python version
- **Stop Conditions**: Python lacks stop conditions like `stepCountIs()`, `hasToolCall()` 
- **Step Callbacks**: Missing `onStepFinish` callback system
- **Tool Call Repair**: No `repairToolCall` functionality
- **Prepare Step**: Missing `prepareStep` function for dynamic step configuration

### 3. **Result Object Completeness**
- **TypeScript**: Rich result object with `toolCalls`, `toolResults`, `files`, `reasoning`, `sources`, `steps`, `totalUsage`
- **Python**: Simple result with just `text`, `content`, `finish_reason`, `usage`

### 4. **Advanced Options**
- **TypeScript**: `activeTools`, `experimental_output`, `experimental_context`, provider options
- **Python**: Basic options only

### 5. **Error Handling & Telemetry**
- **TypeScript**: Comprehensive telemetry, tracing, span recording, error wrapping
- **Python**: Basic error handling only

### 6. **File Generation Support**
- **TypeScript**: Built-in support for generated files via `DefaultGeneratedFile`
- **Python**: No file generation support

## Enhancement Plan

### Phase 1: Core Multi-step Tool Calling (High Priority)

#### 1.1 Implement Step System
```python
@dataclass
class StepResult:
    """Result of a single generation step."""
    content: List[Content]
    text: str
    tool_calls: List[ToolCall]
    tool_results: List[ToolResult]
    files: List[GeneratedFile]
    reasoning_text: Optional[str]
    finish_reason: FinishReason
    usage: Usage
    warnings: Optional[List[str]]
    provider_metadata: Optional[Dict[str, Any]]
    request: Dict[str, Any]
    response: Dict[str, Any]
```

#### 1.2 Add Tool Execution Engine
```python
async def execute_tools(
    tool_calls: List[ToolCall],
    tools: Dict[str, Tool],
    context: Optional[Any] = None
) -> List[ToolResult]:
    """Execute tool calls and return results."""
```

#### 1.3 Implement Stop Conditions
```python
class StopCondition:
    """Base class for stop conditions."""
    async def is_met(self, steps: List[StepResult]) -> bool:
        raise NotImplementedError

def step_count_is(count: int) -> StopCondition:
    """Stop after specific number of steps."""
    
def has_tool_call(tool_name: Optional[str] = None) -> StopCondition:
    """Stop when tool call is present."""
```

#### 1.4 Multi-step Generation Loop
Implement the core multi-step loop similar to TypeScript version:
1. Prepare step with dynamic configuration
2. Execute model generation
3. Parse and execute tool calls
4. Check stop conditions
5. Continue or finish

### Phase 2: Advanced Features (Medium Priority)

#### 2.1 Enhanced Result Objects
- Add `steps` property to `GenerateTextResult`
- Add `toolCalls`, `toolResults`, `files` properties
- Implement `totalUsage` calculation across steps
- Add `reasoning` and `sources` support

#### 2.2 Callback System
```python
class GenerateTextCallbacks:
    on_step_finish: Optional[Callable[[StepResult], None]] = None
    on_tool_call: Optional[Callable[[ToolCall], None]] = None
    on_tool_result: Optional[Callable[[ToolResult], None]] = None
```

#### 2.3 Dynamic Step Configuration
```python
@dataclass
class PrepareStepResult:
    """Result from preparing a step."""
    model: Optional[LanguageModel] = None
    system: Optional[str] = None
    messages: Optional[List[Message]] = None
    tools: Optional[Dict[str, Tool]] = None
    tool_choice: Optional[Union[str, Dict]] = None
    active_tools: Optional[List[str]] = None

PrepareStepFunction = Callable[[PrepareStepArgs], Awaitable[PrepareStepResult]]
```

### Phase 3: Advanced Capabilities (Lower Priority)

#### 3.1 File Generation Support
```python
@dataclass
class GeneratedFile:
    """Represents a generated file."""
    name: str
    content_type: str
    content: bytes
    url: Optional[str] = None
```

#### 3.2 Tool Call Repair
```python
ToolCallRepairFunction = Callable[[FailedToolCall], Awaitable[Optional[ToolCall]]]
```

#### 3.3 Telemetry & Observability
- Add OpenTelemetry integration
- Implement span recording for steps and tool calls
- Add structured logging

#### 3.4 Advanced Options
- `active_tools` for limiting available tools
- `experimental_output` for structured output parsing
- `experimental_context` for tool execution context
- Enhanced provider options

## Implementation Priority

### Immediate (This Session)
1. ✅ Create comparison analysis
2. 🔄 Implement basic Step system
3. 🔄 Add multi-step generation loop
4. 🔄 Basic tool execution

### Next Session
1. Enhanced result objects
2. Stop conditions
3. Callback system
4. Tool call repair

### Future Sessions
1. File generation support
2. Telemetry integration
3. Advanced options
4. Performance optimization

## Success Criteria
- [ ] Multi-step tool calling works like TypeScript version
- [ ] All tool examples pass
- [ ] Result objects have feature parity
- [ ] Performance is comparable
- [ ] Agent examples work correctly

## Files to Modify/Create
1. `src/ai_sdk/core/generate_text.py` - Main enhancements
2. `src/ai_sdk/core/step.py` - New step system
3. `src/ai_sdk/core/tool_execution.py` - Tool execution engine
4. `src/ai_sdk/core/stop_conditions.py` - Stop condition system
5. `src/ai_sdk/tools/execution.py` - Enhanced tool execution
6. Update examples and tests