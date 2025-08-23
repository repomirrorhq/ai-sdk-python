"""Amazon Bedrock provider example for AI SDK Python.

This example demonstrates how to use AWS Bedrock with the AI SDK Python,
including authentication options and various model families.

Requirements:
- pip install 'ai-sdk[bedrock]'
- AWS credentials configured (one of the following):
  - AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY environment variables
  - AWS_BEARER_TOKEN_BEDROCK for API key authentication
  - AWS credentials file or IAM role
"""

import asyncio
import os
from ai_sdk import generate_text, stream_text
from ai_sdk.providers.bedrock import create_bedrock, BedrockProviderSettings


async def basic_bedrock_example():
    """Basic text generation with Claude on Bedrock."""
    
    print("🚀 Basic Bedrock Example with Claude")
    print("=" * 50)
    
    # Option 1: Use default credentials (from environment or AWS config)
    bedrock = create_bedrock()
    model = await bedrock.language_model("anthropic.claude-3-haiku-20240307-v1:0")
    
    try:
        result = await generate_text(
            model=model,
            prompt="Explain AWS Bedrock in one sentence.",
            max_tokens=100
        )
        
        print(f"Response: {result['content']}")
        print(f"Tokens used: {result.get('usage', {})}")
        
    except Exception as e:
        print(f"Error: {e}")


async def custom_credentials_example():
    """Example with custom AWS credentials."""
    
    print("\n🔐 Custom Credentials Example")
    print("=" * 50)
    
    # Option 2: Use custom credentials
    settings = BedrockProviderSettings(
        region="us-east-1",
        access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        session_token=os.getenv("AWS_SESSION_TOKEN"),  # Optional
    )
    
    bedrock = create_bedrock(settings)
    model = await bedrock.language_model("anthropic.claude-3-sonnet-20240229-v1:0")
    
    try:
        result = await generate_text(
            model=model,
            prompt="What are the benefits of using AWS Bedrock?",
            max_tokens=150,
            temperature=0.7
        )
        
        print(f"Response: {result['content']}")
        
    except Exception as e:
        print(f"Error: {e}")


async def api_key_authentication_example():
    """Example using API key authentication (Bearer token)."""
    
    print("\n🔑 API Key Authentication Example")
    print("=" * 50)
    
    # Option 3: Use API key authentication
    api_key = os.getenv("AWS_BEARER_TOKEN_BEDROCK")
    if not api_key:
        print("AWS_BEARER_TOKEN_BEDROCK not set, skipping this example")
        return
        
    settings = BedrockProviderSettings(
        region="us-east-1",
        api_key=api_key
    )
    
    bedrock = create_bedrock(settings)
    model = await bedrock.language_model("anthropic.claude-3-haiku-20240307-v1:0")
    
    try:
        result = await generate_text(
            model=model,
            prompt="Explain the difference between Bedrock and EC2.",
            max_tokens=100
        )
        
        print(f"Response: {result['content']}")
        
    except Exception as e:
        print(f"Error: {e}")


async def streaming_example():
    """Example of streaming responses from Bedrock."""
    
    print("\n🌊 Streaming Example")
    print("=" * 50)
    
    bedrock = create_bedrock()
    model = await bedrock.language_model("anthropic.claude-3-haiku-20240307-v1:0")
    
    try:
        print("Streaming response:")
        stream = await stream_text(
            model=model,
            prompt="Write a short story about a robot learning to paint.",
            max_tokens=200
        )
        
        async for chunk in stream:
            if chunk.get("type") == "content_delta":
                print(chunk["delta"]["text"], end="", flush=True)
            elif chunk.get("type") == "done":
                print(f"\n\nFinished. Tokens used: {chunk.get('usage', {})}")
                
    except Exception as e:
        print(f"Error: {e}")


async def multiple_models_example():
    """Example using different model families on Bedrock."""
    
    print("\n🎯 Multiple Models Example")  
    print("=" * 50)
    
    bedrock = create_bedrock()
    
    models_to_test = [
        ("anthropic.claude-3-haiku-20240307-v1:0", "Claude 3 Haiku"),
        ("amazon.titan-text-express-v1:0", "Amazon Titan Express"),
        ("meta.llama3-8b-instruct-v1:0", "Llama 3 8B"),
    ]
    
    prompt = "What is artificial intelligence?"
    
    for model_id, model_name in models_to_test:
        try:
            print(f"\n{model_name} ({model_id}):")
            
            model = await bedrock.language_model(model_id)
            result = await generate_text(
                model=model,
                prompt=prompt,
                max_tokens=50
            )
            
            print(f"Response: {result['content']}")
            
        except Exception as e:
            print(f"Error with {model_name}: {e}")


async def tool_calling_example():
    """Example of tool calling with Claude on Bedrock."""
    
    print("\n🔧 Tool Calling Example")
    print("=" * 50)
    
    bedrock = create_bedrock()
    model = await bedrock.language_model("anthropic.claude-3-sonnet-20240229-v1:0")
    
    tools = [
        {
            "type": "function",
            "function": {
                "name": "get_weather",
                "description": "Get the weather for a location",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "location": {
                            "type": "string",
                            "description": "The location to get weather for"
                        }
                    },
                    "required": ["location"]
                }
            }
        }
    ]
    
    try:
        result = await generate_text(
            model=model,
            prompt="What's the weather like in San Francisco?",
            tools=tools,
            max_tokens=200
        )
        
        print(f"Response: {result['content']}")
        if result.get('tool_calls'):
            print(f"Tool calls: {result['tool_calls']}")
            
    except Exception as e:
        print(f"Error: {e}")


async def main():
    """Run all examples."""
    print("🏗️  AWS Bedrock Provider Examples")
    print("=" * 50)
    print("Testing Amazon Bedrock integration with AI SDK Python")
    print()
    
    # Check if basic AWS credentials are available
    if not any([
        os.getenv("AWS_ACCESS_KEY_ID"),
        os.getenv("AWS_BEARER_TOKEN_BEDROCK"),
        os.path.exists(os.path.expanduser("~/.aws/credentials"))
    ]):
        print("⚠️  No AWS credentials found!")
        print("Please configure AWS credentials using one of:")
        print("- AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY environment variables")
        print("- AWS_BEARER_TOKEN_BEDROCK for API key authentication")
        print("- AWS credentials file (~/.aws/credentials)")
        print("- IAM role if running on EC2")
        return
    
    try:
        await basic_bedrock_example()
        await custom_credentials_example()
        await api_key_authentication_example()
        await streaming_example()
        await multiple_models_example()
        await tool_calling_example()
        
    except KeyboardInterrupt:
        print("\n\nExamples interrupted by user")
    except Exception as e:
        print(f"\n\nUnexpected error: {e}")
    
    print("\n🎉 Bedrock examples completed!")


if __name__ == "__main__":
    asyncio.run(main())