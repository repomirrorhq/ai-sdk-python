.PHONY: fastapi-example

fastapi-example:
	PYTHONPATH=src uv run --with fastapi --with uvicorn --with pydantic --with httpx --with anthropic --with openai python fastapi_example.py