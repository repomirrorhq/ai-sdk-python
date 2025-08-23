"""MCP type definitions and schemas."""

from typing import Any, Dict, List, Optional, Union, TypeVar, Generic, Literal
from pydantic import BaseModel, Field
from typing_extensions import TypedDict

# Protocol versions
LATEST_PROTOCOL_VERSION = "2025-06-18"
SUPPORTED_PROTOCOL_VERSIONS = [
    LATEST_PROTOCOL_VERSION,
    "2025-03-26", 
    "2024-11-05",
]

# Base types
class BaseParams(BaseModel):
    """Base parameters for MCP requests."""
    meta: Optional[Dict[str, Any]] = Field(default=None, alias="_meta")

class Configuration(BaseModel):
    """Client or server implementation configuration."""
    name: str
    version: str

# Tool types
ToolSchemas = Union[Dict[str, Dict[str, Any]], Literal["automatic"], None]

T_ToolSchemas = TypeVar('T_ToolSchemas', bound=ToolSchemas)

class McpToolSet(Generic[T_ToolSchemas]):
    """MCP tool set type definition."""
    pass

class MCPTool(BaseModel):
    """MCP tool definition."""
    name: str
    description: Optional[str] = None
    input_schema: Dict[str, Any] = Field(alias="inputSchema")

# Content types
class TextContent(BaseModel):
    """Text content type."""
    type: Literal["text"]
    text: str

class ImageContent(BaseModel):
    """Image content type."""
    type: Literal["image"] 
    data: str  # base64 encoded
    mime_type: str = Field(alias="mimeType")

class ResourceContents(BaseModel):
    """Resource contents base type."""
    uri: str
    mime_type: Optional[str] = Field(default=None, alias="mimeType")

class TextResourceContents(ResourceContents):
    """Text resource contents."""
    text: str

class BlobResourceContents(ResourceContents):
    """Binary resource contents."""
    blob: str  # base64 encoded

class EmbeddedResource(BaseModel):
    """Embedded resource type."""
    type: Literal["resource"]
    resource: Union[TextResourceContents, BlobResourceContents]

ContentType = Union[TextContent, ImageContent, EmbeddedResource]

# Result types
class CallToolResult(BaseParams):
    """Result from calling an MCP tool."""
    content: Optional[List[ContentType]] = None
    tool_result: Optional[Any] = Field(default=None, alias="toolResult")
    is_error: bool = Field(default=False, alias="isError")

class ServerCapabilities(BaseModel):
    """Server capabilities description."""
    experimental: Optional[Dict[str, Any]] = None
    logging: Optional[Dict[str, Any]] = None
    prompts: Optional[Dict[str, Any]] = None
    resources: Optional[Dict[str, Any]] = None
    tools: Optional[Dict[str, Any]] = None

class InitializeResult(BaseParams):
    """Result of MCP initialization."""
    protocol_version: str = Field(alias="protocolVersion")
    capabilities: ServerCapabilities
    server_info: Configuration = Field(alias="serverInfo")
    instructions: Optional[str] = None

class PaginatedResult(BaseParams):
    """Base type for paginated results."""
    next_cursor: Optional[str] = Field(default=None, alias="nextCursor")

class ListToolsResult(PaginatedResult):
    """Result of listing tools."""
    tools: List[MCPTool]

# Request types
class Request(BaseModel):
    """Base MCP request."""
    method: str
    params: Optional[BaseParams] = None

class PaginatedRequest(Request):
    """Paginated MCP request."""
    params: Optional[BaseParams] = None
    cursor: Optional[str] = None

# Request options
class RequestOptions(TypedDict, total=False):
    """Options for MCP requests."""
    signal: Any  # AbortSignal equivalent
    timeout: int
    max_total_timeout: int

Notification = Request