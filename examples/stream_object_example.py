#!/usr/bin/env python3
"""Example usage of stream_object functionality."""

import asyncio
from typing import List

from pydantic import BaseModel, Field

from ai_sdk.core import stream_object, collect_stream_object
from ai_sdk.providers.openai import OpenAIProvider


# Define schema for a recipe
class Recipe(BaseModel):
    """A cooking recipe."""
    
    title: str = Field(description="The title of the recipe")
    cuisine: str = Field(description="The cuisine type (e.g., Italian, Mexican, Asian)")
    prep_time: int = Field(description="Preparation time in minutes", ge=1, le=300)
    cook_time: int = Field(description="Cooking time in minutes", ge=1, le=480)
    servings: int = Field(description="Number of servings", ge=1, le=20)
    difficulty: str = Field(description="Difficulty level: easy, medium, or hard")
    ingredients: List[str] = Field(description="List of ingredients with amounts", min_items=3)
    instructions: List[str] = Field(description="Step-by-step cooking instructions", min_items=3)
    notes: str = Field(description="Additional cooking tips or notes")


# Define schema for a product review
class ProductReview(BaseModel):
    """A product review analysis."""
    
    product_name: str = Field(description="Name of the product")
    rating: int = Field(description="Rating out of 5 stars", ge=1, le=5)
    reviewer_sentiment: str = Field(description="Overall sentiment: positive, negative, or neutral")
    pros: List[str] = Field(description="List of positive aspects", min_items=1)
    cons: List[str] = Field(description="List of negative aspects")
    summary: str = Field(description="Summary of the review")
    would_recommend: bool = Field(description="Whether the reviewer would recommend this product")


async def main():
    """Run stream_object examples."""
    # Initialize OpenAI provider
    provider = OpenAIProvider(
        api_key="your-openai-api-key",  # Replace with your API key
        base_url="https://api.openai.com/v1"
    )
    
    # Get a language model
    model = provider.language_model("gpt-4o-mini")
    
    print("🔧 Testing stream_object functionality...")
    print("=" * 50)
    
    # Example 1: Stream a recipe generation
    print("\n🍳 Example 1: Stream recipe generation")
    print("-" * 35)
    
    try:
        current_object = {}
        text_so_far = ""
        
        async for part in stream_object(
            model=model,
            schema=Recipe,
            prompt="Create a recipe for chocolate chip cookies",
            temperature=0.7,
            max_tokens=500,
        ):
            if part.type == "text-delta":
                text_so_far += part.text_delta
                print(f"📝 Text: {part.text_delta}", end="", flush=True)
                
            elif part.type == "object":
                # Show what's new in the object
                new_keys = set(part.object.keys()) - set(current_object.keys())
                if new_keys:
                    print(f"\n🆕 New fields: {', '.join(new_keys)}")
                    for key in new_keys:
                        print(f"   {key}: {part.object[key]}")
                current_object = part.object
                
            elif part.type == "finish":
                print(f"\n✅ Generation finished!")
                print(f"🏁 Finish reason: {part.finish_reason}")
                print(f"📊 Usage: {part.usage.total_tokens} tokens")
                
            elif part.type == "error":
                print(f"\n❌ Error: {part.error}")
                break
                
        print("\n" + "="*50)
        
    except Exception as e:
        print(f"❌ Error in streaming example: {e}")
    
    # Example 2: Collect complete stream result
    print("\n📊 Example 2: Collect complete stream result")
    print("-" * 40)
    
    try:
        result = await collect_stream_object(
            model=model,
            schema=ProductReview,
            prompt="Analyze this review: 'This wireless headset is amazing! Great sound quality and comfortable to wear for hours. Battery life could be better though.'",
            temperature=0.3,
        )
        
        print(f"✅ Final product review:")
        print(f"   Product: {result.object.product_name}")
        print(f"   Rating: {'⭐' * result.object.rating} ({result.object.rating}/5)")
        print(f"   Sentiment: {result.object.reviewer_sentiment}")
        print(f"   Pros: {', '.join(result.object.pros)}")
        print(f"   Cons: {', '.join(result.object.cons) if result.object.cons else 'None mentioned'}")
        print(f"   Recommend: {'Yes' if result.object.would_recommend else 'No'}")
        print(f"   Summary: {result.object.summary}")
        
        print(f"\n📈 Stream Statistics:")
        print(f"   Total partial objects: {len(result.partial_objects)}")
        print(f"   Total text deltas: {len(result.text_deltas)}")
        print(f"   Total characters: {sum(len(delta) for delta in result.text_deltas)}")
        print(f"   Finish reason: {result.finish_reason}")
        print(f"   Token usage: {result.usage.total_tokens}")
        
    except Exception as e:
        print(f"❌ Error in collect example: {e}")
    
    # Example 3: Real-time streaming with progress indicators
    print("\n⏱️  Example 3: Real-time streaming with progress")
    print("-" * 45)
    
    try:
        print("Generating a pasta recipe... 🍝")
        
        fields_completed = set()
        required_fields = {'title', 'cuisine', 'prep_time', 'cook_time', 'servings', 
                          'difficulty', 'ingredients', 'instructions', 'notes'}
        
        async for part in stream_object(
            model=model,
            schema=Recipe,
            prompt="Create a detailed recipe for homemade pasta with marinara sauce",
            temperature=0.6,
        ):
            if part.type == "object":
                new_fields = set(part.object.keys()) - fields_completed
                for field in new_fields:
                    print(f"✓ {field}")
                fields_completed.update(new_fields)
                
                # Show progress
                progress = len(fields_completed) / len(required_fields) * 100
                print(f"   Progress: {progress:.1f}% ({len(fields_completed)}/{len(required_fields)} fields)")
                
            elif part.type == "finish":
                print(f"🎉 Recipe generation complete!")
                print(f"📊 Final usage: {part.usage.total_tokens} tokens")
                break
                
            elif part.type == "error":
                print(f"❌ Error: {part.error}")
                break
    
    except Exception as e:
        print(f"❌ Error in progress example: {e}")
    
    print("\n🎉 All streaming examples completed!")


if __name__ == "__main__":
    asyncio.run(main())