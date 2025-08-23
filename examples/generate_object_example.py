#!/usr/bin/env python3
"""Example usage of generate_object functionality."""

import asyncio
from typing import List

from pydantic import BaseModel, Field

from ai_sdk.core import generate_object
from ai_sdk.providers.openai import OpenAIProvider


# Define schema for a person
class Person(BaseModel):
    """A person with basic information."""
    
    name: str = Field(description="The person's full name")
    age: int = Field(description="The person's age in years", ge=0, le=150)
    occupation: str = Field(description="The person's job or occupation")
    hobbies: List[str] = Field(description="List of the person's hobbies")


# Define schema for a story outline
class StoryOutline(BaseModel):
    """An outline for a short story."""
    
    title: str = Field(description="The title of the story")
    genre: str = Field(description="The genre of the story")
    main_character: str = Field(description="Name of the main character")
    setting: str = Field(description="Where and when the story takes place")
    plot_points: List[str] = Field(description="3-5 key plot points", min_items=3, max_items=5)
    theme: str = Field(description="The main theme or message of the story")


async def main():
    """Run generate_object examples."""
    # Initialize OpenAI provider
    provider = OpenAIProvider(
        api_key="your-openai-api-key",  # Replace with your API key
        base_url="https://api.openai.com/v1"
    )
    
    # Get a language model
    model = provider.language_model("gpt-4o-mini")
    
    print("🔧 Testing generate_object functionality...")
    print("=" * 50)
    
    # Example 1: Generate a person
    print("\n📝 Example 1: Generate a fictional person")
    print("-" * 30)
    
    try:
        result = await generate_object(
            model=model,
            schema=Person,
            prompt="Create a fictional character who is a software engineer living in San Francisco",
            temperature=0.7,
            max_tokens=200,
        )
        
        print(f"✅ Generated person:")
        print(f"   Name: {result.object.name}")
        print(f"   Age: {result.object.age}")
        print(f"   Occupation: {result.object.occupation}")
        print(f"   Hobbies: {', '.join(result.object.hobbies)}")
        print(f"📊 Usage: {result.usage.total_tokens} tokens")
        print(f"🏁 Finish reason: {result.finish_reason}")
        
    except Exception as e:
        print(f"❌ Error generating person: {e}")
    
    # Example 2: Generate a story outline
    print("\n📚 Example 2: Generate a story outline")
    print("-" * 30)
    
    try:
        result = await generate_object(
            model=model,
            schema=StoryOutline,
            prompt="Create an outline for a science fiction short story about AI consciousness",
            temperature=0.8,
            max_tokens=300,
        )
        
        print(f"✅ Generated story outline:")
        print(f"   Title: {result.object.title}")
        print(f"   Genre: {result.object.genre}")
        print(f"   Main Character: {result.object.main_character}")
        print(f"   Setting: {result.object.setting}")
        print(f"   Theme: {result.object.theme}")
        print(f"   Plot Points:")
        for i, point in enumerate(result.object.plot_points, 1):
            print(f"     {i}. {point}")
        print(f"📊 Usage: {result.usage.total_tokens} tokens")
        
    except Exception as e:
        print(f"❌ Error generating story outline: {e}")
    
    # Example 3: Using messages instead of prompt
    print("\n💬 Example 3: Using message format")
    print("-" * 30)
    
    try:
        from ai_sdk.providers.types import Message
        
        messages = [
            Message(role="system", content="You are a helpful assistant that generates structured data."),
            Message(role="user", content="Generate information for a teacher who loves gardening and reading."),
        ]
        
        result = await generate_object(
            model=model,
            schema=Person,
            messages=messages,
            temperature=0.5,
        )
        
        print(f"✅ Generated teacher:")
        print(f"   Name: {result.object.name}")
        print(f"   Age: {result.object.age}")
        print(f"   Occupation: {result.object.occupation}")
        print(f"   Hobbies: {', '.join(result.object.hobbies)}")
        
    except Exception as e:
        print(f"❌ Error generating teacher: {e}")
    
    print("\n🎉 All examples completed!")


if __name__ == "__main__":
    asyncio.run(main())