"""
DeepInfra provider types and model definitions.
"""

from typing import Literal, Union
from pydantic import BaseModel

# DeepInfra Chat Model IDs based on https://deepinfra.com/models/text-generation
DeepInfraChatModelId = Union[
    # Latest Llama Models
    Literal["meta-llama/Llama-4-Maverick-17B-128E-Instruct-FP8"],
    Literal["meta-llama/Llama-4-Scout-17B-16E-Instruct"],
    Literal["meta-llama/Llama-3.3-70B-Instruct"],
    Literal["meta-llama/Llama-3.3-70B-Instruct-Turbo"],
    
    # Llama 3.1 Family
    Literal["meta-llama/Meta-Llama-3.1-70B-Instruct"],
    Literal["meta-llama/Meta-Llama-3.1-8B-Instruct"],
    Literal["meta-llama/Meta-Llama-3.1-405B-Instruct"],
    Literal["meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo"],
    Literal["meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo"],
    
    # Qwen Models
    Literal["Qwen/QwQ-32B-Preview"],
    Literal["Qwen/Qwen2.5-Coder-32B-Instruct"],
    Literal["Qwen/Qwen2.5-72B-Instruct"],
    Literal["Qwen/Qwen2-72B-Instruct"],
    Literal["Qwen/Qwen2-7B-Instruct"],
    Literal["Qwen/Qwen2.5-7B-Instruct"],
    Literal["Qwen/Qwen2.5-Coder-7B"],
    
    # Vision Models
    Literal["meta-llama/Llama-3.2-90B-Vision-Instruct"],
    Literal["meta-llama/Llama-3.2-11B-Vision-Instruct"],
    
    # Specialized Models
    Literal["nvidia/Llama-3.1-Nemotron-70B-Instruct"],
    Literal["microsoft/WizardLM-2-8x22B"],
    Literal["NousResearch/Hermes-3-Llama-3.1-405B"],
    Literal["deepseek-ai/DeepSeek-V3"],
    Literal["nvidia/Nemotron-4-340B-Instruct"],
    
    # Code Models  
    Literal["Phind/Phind-CodeLlama-34B-v2"],
    Literal["bigcode/starcoder2-15b"],
    Literal["bigcode/starcoder2-15b-instruct-v0.1"],
    Literal["codellama/CodeLlama-34b-Instruct-hf"],
    Literal["codellama/CodeLlama-70b-Instruct-hf"],
    Literal["google/codegemma-7b-it"],
    
    # Mistral Models
    Literal["mistralai/Mistral-7B-Instruct-v0.3"],
    Literal["mistralai/Mistral-Nemo-Instruct-2407"],
    Literal["mistralai/Mixtral-8x22B-Instruct-v0.1"],
    Literal["mistralai/Mixtral-8x7B-Instruct-v0.1"],
    
    # Google Models
    Literal["google/gemma-1.1-7b-it"],
    Literal["google/gemma-2-27b-it"],
    Literal["google/gemma-2-9b-it"],
    
    # Older Llama Models
    Literal["meta-llama/Llama-2-13b-chat-hf"],
    Literal["meta-llama/Llama-2-70b-chat-hf"],
    Literal["meta-llama/Llama-2-7b-chat-hf"],
    Literal["meta-llama/Meta-Llama-3-70B-Instruct"],
    Literal["meta-llama/Meta-Llama-3-8B-Instruct"],
    Literal["meta-llama/Llama-3.2-1B-Instruct"],
    Literal["meta-llama/Llama-3.2-3B-Instruct"],
    
    # Microsoft Models
    Literal["microsoft/Phi-3-medium-4k-instruct"],
    Literal["microsoft/WizardLM-2-7B"],
    
    # Other Open Models
    Literal["databricks/dbrx-instruct"],
    Literal["01-ai/Yi-34B-Chat"],
    Literal["openchat/openchat-3.6-8b"],
    Literal["openchat/openchat_3.5"],
    Literal["openbmb/MiniCPM-Llama3-V-2_5"],
    
    # Community Models
    Literal["Austism/chronos-hermes-13b-v2"],
    Literal["Gryphe/MythoMax-L2-13b"],
    Literal["Gryphe/MythoMax-L2-13b-turbo"],
    Literal["HuggingFaceH4/zephyr-orpo-141b-A35b-v0.1"],
    Literal["KoboldAI/LLaMA2-13B-Tiefighter"],
    Literal["Sao10K/L3-70B-Euryale-v2.1"],
    Literal["Sao10K/L3-8B-Lunaris-v1"],
    Literal["Sao10K/L3.1-70B-Euryale-v2.2"],
    Literal["cognitivecomputations/dolphin-2.6-mixtral-8x7b"],
    Literal["cognitivecomputations/dolphin-2.9.1-llama-3-70b"],
    Literal["deepinfra/airoboros-70b"],
    Literal["lizpreciatior/lzlv_70b_fp16_hf"],
    Literal["mattshumer/Reflection-Llama-3.1-70B"],
    
    str,  # Allow custom model IDs
]

# DeepInfra Embedding Model IDs based on https://deepinfra.com/models/embeddings  
DeepInfraEmbeddingModelId = Union[
    # BGE Models (Best Performance)
    Literal["BAAI/bge-base-en-v1.5"],
    Literal["BAAI/bge-large-en-v1.5"],
    Literal["BAAI/bge-m3"],
    
    # E5 Models (Multilingual)
    Literal["intfloat/e5-base-v2"],
    Literal["intfloat/e5-large-v2"],
    Literal["intfloat/multilingual-e5-large"],
    
    # Sentence Transformers
    Literal["sentence-transformers/all-MiniLM-L12-v2"],
    Literal["sentence-transformers/all-MiniLM-L6-v2"],
    Literal["sentence-transformers/all-mpnet-base-v2"],
    Literal["sentence-transformers/multi-qa-mpnet-base-dot-v1"],
    Literal["sentence-transformers/paraphrase-MiniLM-L6-v2"],
    
    # CLIP Models (Multimodal)
    Literal["sentence-transformers/clip-ViT-B-32"],
    Literal["sentence-transformers/clip-ViT-B-32-multilingual-v1"],
    
    # GTE Models
    Literal["thenlper/gte-base"],
    Literal["thenlper/gte-large"],
    
    # Chinese Models
    Literal["shibing624/text2vec-base-chinese"],
    
    str,  # Allow custom model IDs
]

# DeepInfra Image Model IDs based on https://deepinfra.com/models/text-to-image
DeepInfraImageModelId = Union[
    # FLUX Models (State-of-the-art)
    Literal["black-forest-labs/FLUX-1.1-pro"],
    Literal["black-forest-labs/FLUX-1-schnell"], 
    Literal["black-forest-labs/FLUX-1-dev"],
    Literal["black-forest-labs/FLUX-pro"],
    
    # Stable Diffusion 3.5 (Latest)
    Literal["stabilityai/sd3.5"],
    Literal["stabilityai/sd3.5-medium"],
    
    # SDXL Turbo (Fast)
    Literal["stabilityai/sdxl-turbo"],
    
    str,  # Allow custom model IDs  
]


class DeepInfraProviderSettings(BaseModel):
    """Configuration settings for DeepInfra provider."""
    
    base_url: str = "https://api.deepinfra.com/v1"
    """Base URL for DeepInfra API calls. Defaults to https://api.deepinfra.com/v1"""
    
    api_key: str | None = None
    """API key for DeepInfra. If not provided, will try DEEPINFRA_API_KEY environment variable."""
    
    headers: dict[str, str] | None = None
    """Additional headers to include in requests."""


class DeepInfraFinishReason:
    """DeepInfra finish reasons (OpenAI-compatible)."""
    STOP = "stop"
    LENGTH = "length"
    TOOL_CALLS = "tool_calls"
    CONTENT_FILTER = "content_filter"
    ERROR = "error"


class DeepInfraResponseFormat(BaseModel):
    """DeepInfra response format configuration."""
    type: Literal["json_object"] 
    schema: dict | None = None


class DeepInfraMessage(BaseModel):
    """DeepInfra message format (OpenAI-compatible)."""
    role: Literal["system", "user", "assistant", "tool"]
    content: str | list[dict] | None = None
    tool_calls: list[dict] | None = None


class DeepInfraChatRequest(BaseModel):
    """DeepInfra chat API request format (OpenAI-compatible)."""
    model: str
    messages: list[DeepInfraMessage]
    tools: list[dict] | None = None
    tool_choice: dict | str | None = None
    max_tokens: int | None = None
    temperature: float | None = None
    top_p: float | None = None
    frequency_penalty: float | None = None
    presence_penalty: float | None = None
    stop: list[str] | str | None = None
    seed: int | None = None
    response_format: DeepInfraResponseFormat | None = None
    stream: bool = False


class DeepInfraEmbeddingRequest(BaseModel):
    """DeepInfra embedding API request format (OpenAI-compatible)."""
    model: str
    input: list[str] | str
    encoding_format: Literal["float", "base64"] = "float"
    dimensions: int | None = None


class DeepInfraImageRequest(BaseModel):
    """DeepInfra image generation API request format."""
    model: str
    prompt: str
    n: int = 1
    size: str | None = None
    height: int | None = None
    width: int | None = None
    response_format: Literal["url", "b64_json"] = "url"


class DeepInfraUsage(BaseModel):
    """DeepInfra usage statistics (OpenAI-compatible)."""
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0


class DeepInfraStreamChunk(BaseModel):
    """DeepInfra streaming chunk (OpenAI-compatible)."""
    id: str
    object: str = "chat.completion.chunk"
    created: int
    model: str
    choices: list[dict]
    usage: DeepInfraUsage | None = None


class DeepInfraChatResponse(BaseModel):
    """DeepInfra chat response format (OpenAI-compatible)."""
    id: str
    object: str = "chat.completion" 
    created: int
    model: str
    choices: list[dict]
    usage: DeepInfraUsage | None = None


class DeepInfraEmbeddingResponse(BaseModel):
    """DeepInfra embedding response format (OpenAI-compatible)."""
    object: str = "list"
    data: list[dict]
    model: str
    usage: DeepInfraUsage | None = None


class DeepInfraImageResponse(BaseModel):
    """DeepInfra image response format."""
    created: int
    data: list[dict]