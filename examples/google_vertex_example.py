"""
Google Vertex AI Provider Example

This example demonstrates how to use the Google Vertex AI provider for enterprise
Google Cloud integration with the AI SDK Python.

Requirements:
- Google Cloud credentials (service account or Application Default Credentials)
- google-auth library: pip install google-auth
- Access to Google Vertex AI APIs

Environment Variables:
- GOOGLE_VERTEX_PROJECT: Your Google Cloud project ID
- GOOGLE_VERTEX_LOCATION: Google Cloud region (e.g., 'us-central1')  
- GOOGLE_APPLICATION_CREDENTIALS: Path to service account JSON (optional)
"""

import asyncio
import os
from ai_sdk import (
    create_vertex,
    generate_text,
    stream_text,
    embed,
    embed_many,
)


async def basic_text_generation():
    """Basic text generation with Google Vertex AI."""
    print("=== Basic Text Generation ===")
    
    # Create Google Vertex AI provider
    vertex = create_vertex(
        project=os.getenv("GOOGLE_VERTEX_PROJECT", "your-project-id"),
        location=os.getenv("GOOGLE_VERTEX_LOCATION", "us-central1")
    )
    
    # Create language model
    model = vertex.language_model("gemini-1.5-pro")
    
    # Generate text
    result = await generate_text(
        model=model,
        messages=[
            {"role": "user", "content": "Explain quantum computing in simple terms."}
        ],
        max_tokens=200,
        temperature=0.7
    )
    
    print(f"Response: {result.text}")
    print(f"Usage: {result.usage}")
    print(f"Finish reason: {result.finish_reason}")


async def streaming_text_generation():
    """Streaming text generation with Google Vertex AI."""
    print("\n=== Streaming Text Generation ===")
    
    vertex = create_vertex()
    model = vertex.language_model("gemini-1.5-flash")
    
    print("Streaming response...")
    
    stream = await stream_text(
        model=model,
        messages=[
            {"role": "user", "content": "Write a short story about AI and creativity."}
        ],
        max_tokens=300,
        temperature=0.8
    )
    
    full_text = ""
    async for chunk in stream:
        if chunk.delta:
            print(chunk.delta, end="", flush=True)
            full_text += chunk.delta
        if chunk.finish_reason:
            print(f"\n\nFinish reason: {chunk.finish_reason}")
            break
    
    print(f"\nFull text length: {len(full_text)} characters")


async def multimodal_example():
    """Example with image understanding (multimodal)."""
    print("\n=== Multimodal Example ===")
    
    vertex = create_vertex()
    model = vertex.language_model("gemini-1.5-pro")
    
    # Example with image URL (you would provide a real image URL)
    result = await generate_text(
        model=model,
        messages=[
            {
                "role": "user", 
                "content": [
                    {"type": "text", "text": "What do you see in this image?"},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": "https://example.com/image.jpg"  # Replace with real image
                        }
                    }
                ]
            }
        ]
    )
    
    print(f"Image analysis: {result.text}")


async def conversation_example():
    """Multi-turn conversation example."""
    print("\n=== Conversation Example ===")
    
    vertex = create_vertex()
    model = vertex.language_model("gemini-1.5-pro")
    
    messages = [
        {"role": "system", "content": "You are a helpful AI assistant specializing in Python programming."},
        {"role": "user", "content": "How do I create a list comprehension in Python?"}
    ]
    
    # First response
    result = await generate_text(model=model, messages=messages)
    messages.append({"role": "assistant", "content": result.text})
    print(f"Assistant: {result.text}")
    
    # Follow-up question
    messages.append({"role": "user", "content": "Can you show me an example with filtering?"})
    result = await generate_text(model=model, messages=messages)
    print(f"\nAssistant: {result.text}")


async def embedding_examples():
    """Text embeddings with Google Vertex AI."""
    print("\n=== Text Embeddings ===")
    
    vertex = create_vertex()
    embedding_model = vertex.embedding_model("text-embedding-004")
    
    # Single embedding
    result = await embed(
        model=embedding_model,
        value="Google Vertex AI provides powerful machine learning capabilities."
    )
    
    print(f"Single embedding dimension: {len(result.embedding)}")
    print(f"Embedding usage: {result.usage}")
    
    # Multiple embeddings
    texts = [
        "Machine learning is transforming industries.",
        "AI models can process natural language effectively.",
        "Cloud computing enables scalable AI solutions.",
        "Google Vertex AI supports enterprise AI workflows."
    ]
    
    batch_result = await embed_many(
        model=embedding_model,
        values=texts,
        task_type="SEMANTIC_SIMILARITY"  # Vertex AI specific parameter
    )
    
    print(f"\nBatch embeddings: {len(batch_result.embeddings)} vectors")
    print(f"Each embedding dimension: {len(batch_result.embeddings[0])}")
    print(f"Total usage: {batch_result.usage}")


async def advanced_configuration():
    """Advanced configuration options."""
    print("\n=== Advanced Configuration ===")
    
    # Using explicit credentials
    try:
        from google.oauth2 import service_account
        
        # Load credentials from file
        credentials = service_account.Credentials.from_service_account_file(
            os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "/path/to/service-account.json"),
            scopes=['https://www.googleapis.com/auth/cloud-platform']
        )
        
        vertex = create_vertex(
            project="your-project-id",
            location="us-central1",
            credentials=credentials
        )
        
        model = vertex.language_model("gemini-1.5-flash")
        
        result = await generate_text(
            model=model,
            messages=[{"role": "user", "content": "Hello from explicitly configured Vertex AI!"}]
        )
        
        print(f"Configured response: {result.text}")
        
    except ImportError:
        print("google-auth not installed. Skipping explicit credentials example.")
    except Exception as e:
        print(f"Configuration example failed: {e}")


async def model_comparison():
    """Compare different Gemini models."""
    print("\n=== Model Comparison ===")
    
    vertex = create_vertex()
    
    prompt = "Explain the concept of machine learning in one paragraph."
    models = ["gemini-1.5-flash", "gemini-1.5-pro"]
    
    for model_id in models:
        print(f"\n--- {model_id} ---")
        model = vertex.language_model(model_id)
        
        result = await generate_text(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=150
        )
        
        print(f"Response: {result.text}")
        print(f"Tokens used: {result.usage.total_tokens}")


async def error_handling_example():
    """Demonstrate error handling."""
    print("\n=== Error Handling ===")
    
    try:
        # This should fail with missing credentials
        vertex = create_vertex(project="invalid-project")
        model = vertex.language_model("gemini-1.5-pro")
        
        result = await generate_text(
            model=model,
            messages=[{"role": "user", "content": "Test"}]
        )
        
    except Exception as e:
        print(f"Expected error caught: {e}")
        print("This demonstrates proper error handling for invalid configurations.")


async def main():
    """Run all examples."""
    print("Google Vertex AI Provider Examples")
    print("=" * 40)
    
    # Check for required environment variables
    if not os.getenv("GOOGLE_VERTEX_PROJECT"):
        print("Warning: GOOGLE_VERTEX_PROJECT not set. Some examples may fail.")
    
    if not os.getenv("GOOGLE_VERTEX_LOCATION"):
        print("Warning: GOOGLE_VERTEX_LOCATION not set. Using default 'us-central1'.")
    
    try:
        await basic_text_generation()
        await streaming_text_generation() 
        await conversation_example()
        await embedding_examples()
        await model_comparison()
        await advanced_configuration()
        await error_handling_example()
        
        print("\n" + "=" * 40)
        print("All examples completed successfully!")
        
    except Exception as e:
        print(f"\nError running examples: {e}")
        print("Please check your Google Cloud credentials and project configuration.")


if __name__ == "__main__":
    asyncio.run(main())