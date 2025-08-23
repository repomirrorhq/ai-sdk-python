#!/usr/bin/env python3
"""
AI SDK Registry Example - Dynamic provider management and model routing.

This example demonstrates how to use the AI SDK registry system for:
- Managing multiple AI providers in a unified interface
- Accessing models using provider:model format
- Creating custom providers with specific models
- Applying middleware to all models in a registry
- Dynamic provider registration and model routing

Run with:
    python examples/registry_example.py
"""

import asyncio
from typing import Dict, Any

# Mock imports for demonstration - in real usage:
# from ai_sdk import create_openai, create_anthropic, create_google
# from ai_sdk.registry import create_provider_registry, custom_provider
# from ai_sdk.middleware import logging_middleware, caching_middleware

# Mock classes for demonstration
class MockModel:
    def __init__(self, provider_id: str, model_id: str):
        self.provider_id = provider_id
        self.model_id = model_id
        self.full_id = f"{provider_id}:{model_id}"
    
    def __repr__(self):
        return f"MockModel({self.full_id})"

class MockProvider:
    def __init__(self, provider_id: str):
        self.provider_id = provider_id
        self._models = {}
    
    def add_model(self, model_id: str):
        self._models[model_id] = MockModel(self.provider_id, model_id)
    
    def language_model(self, model_id: str):
        return self._models.get(model_id)
    
    def embedding_model(self, model_id: str):
        return self._models.get(model_id)
    
    def image_model(self, model_id: str):
        return self._models.get(model_id)
    
    def speech_model(self, model_id: str):
        return self._models.get(model_id)
    
    def transcription_model(self, model_id: str):
        return self._models.get(model_id)

def create_openai():
    provider = MockProvider("openai")
    provider.add_model("gpt-4")
    provider.add_model("gpt-3.5-turbo")
    provider.add_model("gpt-4o")
    provider.add_model("text-embedding-3-small")
    provider.add_model("dall-e-3")
    provider.add_model("whisper-1")
    provider.add_model("tts-1")
    return provider

def create_anthropic():
    provider = MockProvider("anthropic")
    provider.add_model("claude-3-opus")
    provider.add_model("claude-3-sonnet")
    provider.add_model("claude-3-haiku")
    return provider

def create_google():
    provider = MockProvider("google")
    provider.add_model("gemini-1.5-pro")
    provider.add_model("gemini-1.5-flash")
    provider.add_model("text-embedding-004")
    return provider

class MockRegistry:
    def __init__(self, providers: Dict[str, Any], separator=":"):
        self.providers = providers
        self.separator = separator
    
    def language_model(self, model_id: str):
        provider_id, model_name = model_id.split(self.separator, 1)
        provider = self.providers.get(provider_id)
        if provider:
            return provider.language_model(model_name)
        raise Exception(f"Provider {provider_id} not found")
    
    def embedding_model(self, model_id: str):
        provider_id, model_name = model_id.split(self.separator, 1)
        provider = self.providers.get(provider_id)
        if provider:
            return provider.embedding_model(model_name)
        raise Exception(f"Provider {provider_id} not found")

def create_provider_registry(providers, **kwargs):
    return MockRegistry(providers, kwargs.get('separator', ':'))

class MockCustomProvider:
    def __init__(self, **models):
        self.language_models = models.get('language_models', {})
        self.embedding_models = models.get('embedding_models', {})
        self.fallback = models.get('fallback_provider')
    
    def language_model(self, model_id: str):
        if model_id in self.language_models:
            return self.language_models[model_id]
        if self.fallback:
            return self.fallback.language_model(model_id)
        return None

def custom_provider(**kwargs):
    return MockCustomProvider(**kwargs)

def logging_middleware(**kwargs):
    return {"type": "logging", **kwargs}


async def demonstrate_basic_registry():
    """Demonstrate basic registry usage."""
    print("=" * 60)
    print("Basic Registry Usage")
    print("=" * 60)
    
    # Create individual providers
    openai = create_openai()
    anthropic = create_anthropic()
    google = create_google()
    
    print("✅ Created individual providers:")
    print(f"  - OpenAI: {openai.provider_id}")
    print(f"  - Anthropic: {anthropic.provider_id}")
    print(f"  - Google: {google.provider_id}")
    
    # Create registry with multiple providers
    registry = create_provider_registry({
        "openai": openai,
        "anthropic": anthropic,
        "google": google
    })
    
    print("\\n🏪 Created unified registry with all providers")
    
    # Access models through registry using provider:model format
    model_requests = [
        "openai:gpt-4",
        "anthropic:claude-3-sonnet",
        "google:gemini-1.5-pro",
        "openai:gpt-3.5-turbo",
        "anthropic:claude-3-haiku"
    ]
    
    print("\\n🎯 Accessing models through registry:")
    for model_id in model_requests:
        try:
            model = registry.language_model(model_id)
            print(f"  ✅ {model_id} → {model}")
        except Exception as e:
            print(f"  ❌ {model_id} → Error: {e}")
    
    # Access embedding models
    print("\\n📊 Accessing embedding models:")
    embedding_requests = [
        "openai:text-embedding-3-small",
        "google:text-embedding-004"
    ]
    
    for model_id in embedding_requests:
        try:
            model = registry.embedding_model(model_id)
            print(f"  ✅ {model_id} → {model}")
        except Exception as e:
            print(f"  ❌ {model_id} → Error: {e}")


async def demonstrate_custom_provider():
    """Demonstrate custom provider creation."""
    print("\\n" + "=" * 60)
    print("Custom Provider Example")
    print("=" * 60)
    
    # Create base providers for sourcing models
    openai = create_openai()
    anthropic = create_anthropic()
    
    # Get specific models
    gpt4 = openai.language_model("gpt-4")
    turbo = openai.language_model("gpt-3.5-turbo")
    claude_sonnet = anthropic.language_model("claude-3-sonnet")
    embedding = openai.language_model("text-embedding-3-small")
    
    print("🔧 Creating custom provider with curated models:")
    print(f"  - 'smart' → {gpt4}")
    print(f"  - 'fast' → {turbo}")
    print(f"  - 'claude' → {claude_sonnet}")
    print(f"  - 'embedding' → {embedding}")
    
    # Create custom provider with specific model mappings
    custom = custom_provider(
        language_models={
            "smart": gpt4,
            "fast": turbo,
            "claude": claude_sonnet
        },
        embedding_models={
            "default": embedding
        },
        fallback_provider=openai  # Fallback to OpenAI for unlisted models
    )
    
    print("\\n✨ Custom provider created with fallback to OpenAI")
    
    # Use custom provider
    print("\\n🎪 Testing custom provider:")
    
    # Test custom mappings
    test_models = ["smart", "fast", "claude"]
    for model_id in test_models:
        model = custom.language_model(model_id)
        print(f"  ✅ custom.language_model('{model_id}') → {model}")
    
    # Test fallback
    print("\\n🔄 Testing fallback functionality:")
    fallback_models = ["gpt-4o", "whisper-1"]
    for model_id in fallback_models:
        model = custom.language_model(model_id)
        if model:
            print(f"  ✅ Fallback: '{model_id}' → {model}")
        else:
            print(f"  ❌ Fallback failed for '{model_id}'")


async def demonstrate_registry_with_middleware():
    """Demonstrate registry with middleware."""
    print("\\n" + "=" * 60)
    print("Registry with Middleware")
    print("=" * 60)
    
    # Create providers
    openai = create_openai()
    anthropic = create_anthropic()
    
    # Create middleware
    middleware = [
        logging_middleware(level="INFO", include_params=True),
        # In real usage: caching_middleware(ttl=300),
        # rate_limiting_middleware(requests_per_minute=60)
    ]
    
    print("🔧 Creating registry with middleware:")
    for mw in middleware:
        print(f"  - {mw['type']} middleware")
    
    # Create registry with middleware (simplified for demo)
    registry = create_provider_registry(
        {
            "openai": openai,
            "anthropic": anthropic
        },
        language_model_middleware=middleware
    )
    
    print("\\n🚀 Registry created with middleware applied to all language models")
    
    # In a real implementation, middleware would be automatically applied
    print("\\n💡 Benefits of middleware in registry:")
    print("  - Automatic logging for all models")
    print("  - Response caching across providers")  
    print("  - Consistent rate limiting")
    print("  - Telemetry and monitoring")
    print("  - Error handling and retries")
    
    # Simulate using models (middleware would be applied transparently)
    models = ["openai:gpt-4", "anthropic:claude-3-sonnet"]
    print("\\n🎯 Using models (middleware applied transparently):")
    for model_id in models:
        model = registry.language_model(model_id)
        print(f"  ✅ {model_id} → {model} (with middleware)")


async def demonstrate_advanced_routing():
    """Demonstrate advanced model routing patterns."""
    print("\\n" + "=" * 60)
    print("Advanced Model Routing")
    print("=" * 60)
    
    # Create a smart routing system
    providers = {
        "openai": create_openai(),
        "anthropic": create_anthropic(), 
        "google": create_google()
    }
    
    registry = create_provider_registry(providers)
    
    print("🧠 Smart routing patterns:")
    
    # Define routing strategies
    routing_strategies = {
        "best_reasoning": "anthropic:claude-3-opus",
        "fastest": "google:gemini-1.5-flash", 
        "balanced": "openai:gpt-4",
        "cost_effective": "openai:gpt-3.5-turbo",
        "multimodal": "google:gemini-1.5-pro",
        "coding": "anthropic:claude-3-sonnet"
    }
    
    print("\\n📋 Routing strategy mappings:")
    for strategy, model_id in routing_strategies.items():
        model = registry.language_model(model_id)
        print(f"  {strategy:15} → {model}")
    
    # Simulate use case based routing
    print("\\n🎯 Use case based routing:")
    use_cases = [
        ("Complex reasoning task", "best_reasoning"),
        ("Simple Q&A", "fastest"),
        ("Code generation", "coding"),  
        ("Image analysis", "multimodal"),
        ("High volume processing", "cost_effective")
    ]
    
    for use_case, strategy in use_cases:
        model_id = routing_strategies[strategy]
        model = registry.language_model(model_id)
        print(f"  '{use_case}' → {strategy} → {model}")


async def demonstrate_dynamic_registry_management():
    """Demonstrate dynamic registry management."""
    print("\\n" + "=" * 60)
    print("Dynamic Registry Management")
    print("=" * 60)
    
    # Start with empty registry
    registry = create_provider_registry({})
    print("🏗️  Started with empty registry")
    
    # Simulate dynamic provider registration
    print("\\n📝 Dynamically registering providers:")
    
    providers_to_add = [
        ("openai", create_openai()),
        ("anthropic", create_anthropic()),
        ("google", create_google())
    ]
    
    for provider_id, provider in providers_to_add:
        # In real implementation: registry.register_provider(provider_id, provider)
        registry.providers[provider_id] = provider
        print(f"  ✅ Registered {provider_id}")
        
        # Test immediate availability
        try:
            test_model = f"{provider_id}:test-model" 
            # This would fail but shows the concept
            print(f"     Provider {provider_id} is now available in registry")
        except:
            print(f"     Provider {provider_id} registered successfully")
    
    print("\\n🔄 Registry now contains:", list(registry.providers.keys()))
    
    # Demonstrate provider removal
    print("\\n🗑️  Removing provider 'google':")
    if "google" in registry.providers:
        del registry.providers["google"]
        print("  ✅ Google provider removed")
        print("  🔄 Registry now contains:", list(registry.providers.keys()))
    
    # Show error handling for removed provider
    print("\\n❌ Attempting to use removed provider:")
    try:
        # This would raise NoSuchProviderError in real implementation
        print("  Would raise: NoSuchProviderError for 'google:gemini-1.5-pro'")
    except Exception as e:
        print(f"  Error: {e}")


async def demonstrate_registry_best_practices():
    """Demonstrate best practices for using registries."""
    print("\\n" + "=" * 60)
    print("Registry Best Practices")
    print("=" * 60)
    
    print("🎯 Best Practices Summary:")
    
    practices = [
        {
            "title": "1. Centralized Configuration",
            "description": "Use registry to centrally manage all AI providers",
            "example": "registry = create_provider_registry(all_providers)"
        },
        {
            "title": "2. Consistent Naming",
            "description": "Use consistent provider:model naming conventions",
            "example": "'openai:gpt-4', 'anthropic:claude-3-sonnet'"
        },
        {
            "title": "3. Middleware Application",
            "description": "Apply common middleware to all models through registry",
            "example": "language_model_middleware=[logging, caching, telemetry]"
        },
        {
            "title": "4. Custom Providers for Abstraction", 
            "description": "Create custom providers to abstract model complexity",
            "example": "custom_provider(language_models={'smart': gpt4, 'fast': turbo})"
        },
        {
            "title": "5. Fallback Strategies",
            "description": "Use fallback providers for reliability",
            "example": "fallback_provider=primary_provider"
        },
        {
            "title": "6. Dynamic Management",
            "description": "Register/unregister providers based on availability",
            "example": "registry.register_provider('new_provider', provider)"
        }
    ]
    
    for practice in practices:
        print(f"\\n{practice['title']}")
        print(f"  📖 {practice['description']}")
        print(f"  💡 Example: {practice['example']}")
    
    print("\\n🚀 Result: Unified, scalable, maintainable AI provider management!")


async def main():
    """Run all registry demonstrations."""
    print("AI SDK Registry System Examples")
    print("=" * 60)
    print("Demonstrating dynamic provider management and model routing")
    print()
    
    await demonstrate_basic_registry()
    await demonstrate_custom_provider()
    await demonstrate_registry_with_middleware()
    await demonstrate_advanced_routing()
    await demonstrate_dynamic_registry_management()
    await demonstrate_registry_best_practices()
    
    print("\\n" + "=" * 60)
    print("Registry Examples Complete!")
    print("=" * 60)
    print("""
🎯 Registry System Benefits:

✨ Unified Interface
   - Single point of access for all AI providers
   - Consistent provider:model naming convention
   - Transparent middleware application

🔧 Flexibility
   - Custom providers for specialized use cases
   - Dynamic provider registration/removal
   - Fallback provider support

🚀 Scalability  
   - Easy to add new providers
   - Centralized configuration management
   - Middleware applied consistently

💡 Developer Experience
   - Simple, intuitive API
   - Type-safe model access
   - Comprehensive error handling

The registry system transforms provider chaos into organized,
manageable AI infrastructure! 🎉
    """)


if __name__ == "__main__":
    asyncio.run(main())