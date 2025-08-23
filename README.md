# AI SDK for Python

A Python port of the AI SDK, providing a unified interface for working with various AI providers including OpenAI, Anthropic, Google, and many more.

> **🎉 Production Ready**: This project has achieved 100% provider parity with the TypeScript AI SDK (v0.2.0). All 29 providers are implemented and ready for production use.

## 🎯 Project Goals

This is a comprehensive Python port of the [Vercel AI SDK](https://github.com/vercel/ai), aiming to provide:

- **Unified Interface**: Work with 30+ AI providers through a consistent API
- **Modern Python**: Built with modern Python features (async/await, type hints, Pydantic)
- **Framework Integration**: Support for FastAPI, Django, Flask, and other Python web frameworks
- **Streaming Support**: Real-time streaming for text generation and structured outputs
- **Tool Calling**: Function/tool calling support across providers
- **Type Safety**: Full type safety with Pydantic models and mypy support

## ✅ Current Status

**All Major Features Completed** ✨

### Core Functionality ✅ COMPLETE
- ✅ `generate_text()` - Generate text with any provider
- ✅ `stream_text()` - Stream text generation
- ✅ `generate_object()` - Generate structured objects
- ✅ `stream_object()` - Stream structured object generation
- ✅ `embed()` - Generate embeddings
- ✅ `embed_many()` - Batch embedding generation
- ✅ `generate_image()` - AI image generation
- ✅ `generate_speech()` - Text-to-speech synthesis
- ✅ `transcribe()` - Speech-to-text transcription
- ✅ Agent system with multi-step reasoning
- ✅ Advanced tool calling and orchestration
- ✅ Comprehensive middleware system
- ✅ LangChain and LlamaIndex adapters for ecosystem integration

### Providers ✅ ALL 29 IMPLEMENTED
- ✅ **OpenAI** - GPT, DALL-E, Whisper, embeddings
- ✅ **Anthropic** - Claude models with tool calling
- ✅ **Google** - Gemini models with multimodal support
- ✅ **Google Vertex** - Enterprise Google AI with auth
- ✅ **Azure OpenAI** - Azure-hosted OpenAI models
- ✅ **Amazon Bedrock** - AWS-hosted AI models
- ✅ **Groq** - Ultra-fast LPU inference
- ✅ **TogetherAI** - 100+ open-source models
- ✅ **Mistral** - Mixtral and Mistral models
- ✅ **Cohere** - Enterprise NLP models
- ✅ **Perplexity** - Search-augmented generation
- ✅ **DeepSeek** - Advanced reasoning models
- ✅ **xAI** - Grok models
- ✅ **Cerebras** - High-performance inference
- ✅ **DeepInfra** - Cost-effective model hosting
- ✅ **Fireworks** - Fast model serving
- ✅ **Replicate** - ML model marketplace
- ✅ **ElevenLabs** - Advanced text-to-speech
- ✅ **Deepgram** - Speech-to-text API
- ✅ **AssemblyAI** - Speech understanding
- ✅ **Fal** - Image/video generation
- ✅ **Hume** - Emotion-aware speech
- ✅ **LMNT** - Real-time speech synthesis
- ✅ **Gladia** - Audio transcription
- ✅ **Luma** - AI video generation
- ✅ **Vercel** - Vercel model endpoints
- ✅ **Rev AI** - Professional transcription
- ✅ **Gateway** - AI Gateway for routing/analytics
- ✅ **OpenAI-Compatible** - Local & custom endpoints

### Framework Integrations ✅ 2/4 COMPLETE
- ✅ **LangChain** - Seamless integration with LangChain ecosystem
- ✅ **LlamaIndex** - RAG and document processing integration
- ⏳ **FastAPI** - Async routes and WebSocket streaming (planned)
- ⏳ **Django** - Model integration and admin interface (planned)

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