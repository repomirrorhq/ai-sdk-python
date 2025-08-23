# Generate Object: TypeScript vs Python Comparison and Enhancement Plan

## Key Differences Identified

### 1. **Schema System**
- **TypeScript**: Supports Zod schemas (v3 and v4), flexible schema inference
- **Python**: Only supports Pydantic models, simpler but less flexible

### 2. **Output Modes**
- **TypeScript**: Comprehensive mode system (`auto`, `json`, `tool`) with smart provider selection
- **Python**: Basic mode support, less sophisticated provider integration

### 3. **Output Types**  
- **TypeScript**: Multiple output types (`object`, `array`, `enum`, `no-schema`)
- **Python**: Only object output supported

### 4. **Text Repair Functionality**
- **TypeScript**: Built-in `experimental_repairText` function for fixing malformed JSON
- **Python**: No text repair mechanism

### 5. **Telemetry & Observability**
- **TypeScript**: Comprehensive telemetry, span recording, error tracking
- **Python**: Basic error handling only

### 6. **Streaming Support**
- **TypeScript**: Advanced streaming with partial objects, text deltas, repair
- **Python**: Basic streaming, less sophisticated

### 7. **Error Handling**
- **TypeScript**: Rich error types, automatic retries, graceful degradation  
- **Python**: Simple error handling

### 8. **Provider Integration**
- **TypeScript**: Deep provider options, response format handling
- **Python**: Basic provider interface

## Enhancement Plan

### Phase 1: Core Improvements (High Priority)

#### 1.1 Enhance Output Types Support
```python
@dataclass
class GenerateObjectOptions:
    """Enhanced options for generate_object."""
    output: Literal['object', 'array', 'enum', 'no-schema'] = 'object'
    mode: Literal['auto', 'json', 'tool'] = 'auto'
    enum_values: Optional[List[Any]] = None  # For enum output
```

#### 1.2 Add Text Repair Functionality  
```python
class TextRepairFunction:
    """Function to repair malformed JSON text."""
    
    async def repair(
        self, 
        text: str, 
        error: Exception,
        schema: Type[BaseModel]
    ) -> Optional[str]:
        """Attempt to repair malformed JSON."""
```

#### 1.3 Enhanced Mode System
```python
class OutputStrategy:
    """Strategy for generating objects based on mode and provider."""
    
    @staticmethod
    def get_strategy(
        mode: str,
        provider: str,
        schema: Type[BaseModel]
    ) -> 'OutputStrategy':
        """Get the best strategy for the given mode and provider."""
```

### Phase 2: Advanced Features (Medium Priority)

#### 2.1 Schema Flexibility
```python
# Support for both Pydantic and dict schemas
SchemaType = Union[Type[BaseModel], Dict[str, Any]]

def normalize_schema(schema: SchemaType) -> Dict[str, Any]:
    """Convert various schema types to JSON schema."""
    if isinstance(schema, type) and issubclass(schema, BaseModel):
        return schema.model_json_schema()
    return schema
```

#### 2.2 Enhanced Streaming
```python
class EnhancedObjectStreamPart(BaseModel):
    """Enhanced streaming part with repair and validation."""
    
    type: str
    partial_object: Optional[Dict[str, Any]] = None
    text_delta: Optional[str] = None
    validation_errors: Optional[List[str]] = None
    repaired_content: Optional[str] = None
```

#### 2.3 Array and Enum Support
```python
async def generate_array(
    model: LanguageModel,
    item_schema: Type[T],
    **kwargs
) -> List[T]:
    """Generate an array of objects."""

async def generate_enum(
    model: LanguageModel, 
    enum_values: List[T],
    **kwargs
) -> T:
    """Generate an enum value."""
```

### Phase 3: Advanced Capabilities (Lower Priority)

#### 3.1 Provider-Specific Optimization
```python
class ProviderOptimizer:
    """Optimize object generation for specific providers."""
    
    @staticmethod
    def optimize_for_provider(
        provider: str,
        schema: Dict[str, Any],
        mode: str
    ) -> Dict[str, Any]:
        """Optimize settings for specific provider."""
```

#### 3.2 Advanced Validation
```python
class SchemaValidator:
    """Enhanced validation with detailed error reporting."""
    
    def validate_with_repair(
        self,
        data: Any,
        schema: Type[BaseModel],
        repair_func: Optional[TextRepairFunction] = None
    ) -> ValidationResult:
        """Validate with optional repair."""
```

#### 3.3 Caching & Performance
```python
class SchemaCacheManager:
    """Cache compiled schemas and validation functions."""
    
    def get_cached_schema(self, schema: Type[BaseModel]) -> Dict[str, Any]:
        """Get cached JSON schema."""
```

## Missing Features to Implement

### Immediate (This Session)
1. ✅ Create comparison analysis  
2. 🔄 Add text repair functionality
3. 🔄 Enhance output type support (array, enum)
4. 🔄 Improve mode system

### Next Session  
1. Advanced streaming with validation
2. Provider-specific optimizations
3. Enhanced error handling
4. Schema caching

### Future Sessions
1. Telemetry integration
2. Performance optimizations
3. Advanced validation features
4. Provider format negotiation

## Implementation Priority

### Core Enhancements
1. **Text Repair System**: Critical for handling malformed JSON
2. **Output Types**: Array and enum support for completeness
3. **Mode System**: Better provider integration
4. **Enhanced Streaming**: More robust partial object handling

### Advanced Features
1. **Schema Caching**: Performance improvements
2. **Provider Optimization**: Better provider-specific handling
3. **Advanced Validation**: Better error reporting
4. **Telemetry**: Observability improvements

## Success Criteria
- [ ] Support for array and enum output types
- [ ] Text repair functionality works with malformed JSON
- [ ] Streaming provides detailed validation feedback
- [ ] Provider-specific optimizations improve success rates
- [ ] Performance is comparable to TypeScript version
- [ ] All object generation examples pass

## Files to Modify/Create
1. `src/ai_sdk/core/generate_object.py` - Main enhancements
2. `src/ai_sdk/core/object_repair.py` - Text repair functionality  
3. `src/ai_sdk/core/object_streaming.py` - Enhanced streaming
4. `src/ai_sdk/core/output_strategy.py` - Mode and strategy system
5. `src/ai_sdk/core/schema_utils.py` - Schema utilities
6. Update examples and tests

## TypeScript Features to Port
- Multiple output types (object, array, enum, no-schema)
- Comprehensive mode system with auto-detection
- Text repair for malformed JSON responses
- Advanced streaming with partial validation
- Provider-specific response format handling
- Rich telemetry and error reporting
- Schema inference and optimization