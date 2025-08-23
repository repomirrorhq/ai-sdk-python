# AI SDK for Python

A Python port of the AI SDK, providing a unified interface for working with various AI providers including OpenAI, Anthropic, Google, and many more.

> **⚠️ Early Development**: This project is currently in early development (v0.1.0). The API is not stable and breaking changes are expected.

## 🎯 Project Goals

This is a comprehensive Python port of the [Vercel AI SDK](https://github.com/vercel/ai), aiming to provide:

- **Unified Interface**: Work with 30+ AI providers through a consistent API
- **Modern Python**: Built with modern Python features (async/await, type hints, Pydantic)
- **Framework Integration**: Support for FastAPI, Django, Flask, and other Python web frameworks
- **Streaming Support**: Real-time streaming for text generation and structured outputs
- **Tool Calling**: Function/tool calling support across providers
- **Type Safety**: Full type safety with Pydantic models and mypy support

## 🚧 Current Status

**Phase 1: Foundation (In Progress)**

- [x] Project structure and build system
- [x] Core provider interfaces and types
- [x] Error hierarchy
- [x] Basic utilities and HTTP client
- [ ] Streaming abstractions
- [ ] Schema system with Pydantic
- [ ] Core text generation functions

## 📋 Planned Features

### Core Functionality
- `generate_text()` - Generate text with any provider
- `stream_text()` - Stream text generation
- `generate_object()` - Generate structured objects
- `stream_object()` - Stream structured object generation
- `embed()` - Generate embeddings
- `embed_many()` - Batch embedding generation

### Providers (Planned)
- **OpenAI** - GPT models, DALL-E, Whisper
- **Anthropic** - Claude models  
- **Google** - Gemini models
- **Azure** - Azure OpenAI
- **Amazon Bedrock** - AWS AI models
- **And 25+ more providers**

### Framework Integrations (Planned)
- **FastAPI** - Async routes and WebSocket streaming
- **Django** - Model integration and admin interface
- **Flask** - Extension and streaming support
- **Starlette/Sanic** - ASGI framework support

## 🛠️ Development

This project uses modern Python tooling:

- **uv** - Fast Python package manager
- **ruff** - Fast Python linter and formatter  
- **mypy** - Static type checking
- **pytest** - Testing framework
- **pydantic** - Data validation and serialization

### Setup

```bash
# Clone the repository
git clone https://github.com/Yonom/ai-sdk-python.git
cd ai-sdk-python

# Install dependencies (requires uv)
uv sync --dev

# Run tests
uv run pytest

# Run linting
uv run ruff check
uv run mypy src
```

### Testing

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=ai_sdk --cov-report=html

# Run specific test
uv run pytest tests/test_basic.py -v
```

## 📚 Documentation

Comprehensive documentation is planned and will be available at a later date. For now, refer to:

- `agent/LONG_TERM_PLAN.md` - Detailed development roadmap
- `agent/CURRENT_SESSION_TODOS.md` - Current session progress
- Source code with extensive type hints and docstrings

## 🤝 Contributing

This project is in early development. Contributions will be welcome once the core architecture is established.

## 📄 License

Apache 2.0 - same as the original AI SDK.

## 🙏 Acknowledgments

This project is a Python port of the excellent [Vercel AI SDK](https://github.com/vercel/ai). All credit for the original design and API goes to the Vercel team.