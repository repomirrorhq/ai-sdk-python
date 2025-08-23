# Gateway Provider Analysis & Porting Plan
*August 23, 2025*

## TypeScript Implementation Analysis

### Core Components

#### 1. GatewayProvider (`gateway-provider.ts`)
- **Main factory function**: `createGatewayProvider(options)`
- **Key features**:
  - Metadata caching with configurable refresh intervals
  - Dual authentication: API key or Vercel OIDC token
  - Vercel observability headers integration
  - Base URL configuration (defaults to `https://ai-gateway.vercel.sh/v1/ai`)
  - Language model and embedding model support
  
#### 2. GatewayLanguageModel (`gateway-language-model.ts`)  
- **Implements**: `LanguageModelV2` interface
- **Key features**:
  - Full streaming support with transform streams
  - File part encoding to base64 for binary data
  - Model configuration headers for gateway routing
  - Comprehensive error handling with context
  
#### 3. GatewayEmbeddingModel (`gateway-embedding-model.ts`)
- **Implements**: `EmbeddingModelV2<string>` interface  
- **Key features**:
  - Batch embedding support (up to 2048 per call)
  - Parallel call support
  - Usage tracking and provider metadata
  
#### 4. GatewayFetchMetadata (`gateway-fetch-metadata.ts`)
- **Purpose**: Fetches available models from gateway
- **Features**:
  - Model discovery and capabilities
  - Pricing information
  - Model type classification (language/embedding/image)
  
#### 5. Authentication System
- **API Key**: Standard bearer token auth
- **OIDC**: Vercel integration with automatic token extraction
- **Vercel Environment**: Integration with Vercel deployment context
  
#### 6. Error System
- **Comprehensive error hierarchy**:
  - `GatewayError` (base)
  - `GatewayAuthenticationError`  
  - `GatewayRateLimitError`
  - `GatewayModelNotFoundError`
  - `GatewayInvalidRequestError`
  - `GatewayInternalServerError`

### Key APIs and Endpoints

#### Gateway Endpoints
- **Config**: `GET /v1/ai/config` - Model discovery  
- **Language Model**: `POST /v1/ai/language-model` - Text generation
- **Embedding Model**: `POST /v1/ai/embedding-model` - Embeddings

#### Headers System
- **Authentication**: `Authorization: Bearer <token>`
- **Protocol Version**: `ai-gateway-protocol-version: 0.0.1`
- **Auth Method**: `x-ai-gateway-auth-method: api-key|oidc`
- **Model Config**: 
  - `ai-language-model-specification-version: 2`
  - `ai-language-model-id: <model-id>`
  - `ai-language-model-streaming: true|false`
- **Observability** (Vercel specific):
  - `ai-o11y-deployment-id`
  - `ai-o11y-environment`  
  - `ai-o11y-region`
  - `ai-o11y-request-id`

## Python Implementation Plan

### Directory Structure
```
src/ai_sdk/providers/gateway/
├── __init__.py              # Main exports
├── provider.py              # GatewayProvider class
├── language_model.py        # GatewayLanguageModel class  
├── embedding_model.py       # GatewayEmbeddingModel class
├── fetch_metadata.py        # GatewayFetchMetadata class
├── config.py               # Configuration types
├── auth.py                 # Authentication utilities
└── errors.py               # Gateway-specific errors
```

### Phase 1: Core Infrastructure

#### 1.1 Error System (`errors.py`)
```python
class GatewayError(Exception):
    """Base gateway error"""
    
class GatewayAuthenticationError(GatewayError):
    """Authentication failed"""
    
class GatewayRateLimitError(GatewayError):
    """Rate limit exceeded"""
    
# ... other error classes
```

#### 1.2 Configuration (`config.py`)
```python
from typing import Optional, Dict, Callable, Awaitable
from ai_sdk.utils.http import HttpClient

class GatewayConfig:
    base_url: str
    headers: Callable[[], Awaitable[Dict[str, str]]]
    http_client: Optional[HttpClient] = None
```

#### 1.3 Authentication (`auth.py`)
```python
async def get_gateway_auth_token(
    api_key: Optional[str] = None,
) -> Optional[Dict[str, str]]:
    """Get authentication token (API key or OIDC)"""
```

### Phase 2: Model Implementations

#### 2.1 Language Model (`language_model.py`)
- Port streaming functionality using Python async generators
- Implement file encoding for binary data
- Add comprehensive error handling
- Support both generation and streaming

#### 2.2 Embedding Model (`embedding_model.py`) 
- Port batch embedding support
- Implement usage tracking
- Add provider metadata handling

#### 2.3 Metadata Fetching (`fetch_metadata.py`)
- Port model discovery functionality
- Implement caching with configurable refresh
- Add model filtering and search

### Phase 3: Main Provider (`provider.py`)
- Port factory function with full configuration
- Implement metadata caching
- Add observability headers support
- Support both sync and async usage patterns

## Implementation Considerations

### Python-Specific Adaptations

#### 1. Async/Await Patterns
- Use `async def` for all async operations
- Replace Promise chains with `await`
- Use `asyncio` for concurrency

#### 2. Type Hints  
- Use `typing` module for comprehensive type annotations
- Port TypeScript interfaces to Python protocols/dataclasses
- Use `Pydantic` for request/response validation

#### 3. HTTP Client
- Use existing `ai_sdk.utils.http.HttpClient`
- Maintain consistency with other providers
- Support streaming responses

#### 4. Error Handling
- Follow Python exception patterns
- Maintain error context and chaining  
- Use descriptive error messages

### Key Challenges

#### 1. Vercel Integration
- Port Vercel environment detection
- Handle OIDC token extraction (may be Vercel-specific)
- Adapt observability headers

#### 2. Streaming Implementation
- Port TypeScript TransformStream to Python async generators
- Handle backpressure correctly
- Maintain compatibility with existing streaming patterns

#### 3. File Handling
- Port file encoding logic (base64 conversion)
- Handle binary data efficiently
- Support URL-based file references

## Testing Strategy

### Unit Tests
- Test all error scenarios
- Mock gateway API responses  
- Test authentication flows
- Verify streaming functionality

### Integration Tests  
- Test against real gateway (if available)
- Test model discovery
- Test various model types
- Test error handling with real responses

### Examples
- Basic usage example
- Streaming example  
- Model discovery example
- Error handling example

## Success Criteria

1. **Full API Compatibility**: All TypeScript features ported
2. **Performance**: Comparable latency and throughput
3. **Error Handling**: Comprehensive error coverage
4. **Documentation**: Clear usage examples and API docs
5. **Testing**: 90%+ code coverage with integration tests

This analysis provides the foundation for implementing a complete Gateway provider in Python that maintains full compatibility with the TypeScript version while following Python best practices.