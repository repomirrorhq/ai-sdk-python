"""JSON-RPC message types and utilities for MCP."""

from typing import Any, Union, Literal
from pydantic import BaseModel, Field
from .types import BaseParams

JSONRPC_VERSION = "2.0"

class JSONRPCRequest(BaseModel):
    """JSON-RPC request message."""
    jsonrpc: Literal["2.0"] = JSONRPC_VERSION
    id: Union[str, int]
    method: str
    params: BaseParams = Field(default_factory=BaseParams)

class JSONRPCResponse(BaseModel):
    """JSON-RPC response message."""
    jsonrpc: Literal["2.0"] = JSONRPC_VERSION  
    id: Union[str, int]
    result: Any

class JSONRPCErrorDetail(BaseModel):
    """JSON-RPC error detail."""
    code: int
    message: str
    data: Any = None

class JSONRPCError(BaseModel):
    """JSON-RPC error message."""
    jsonrpc: Literal["2.0"] = JSONRPC_VERSION
    id: Union[str, int]
    error: JSONRPCErrorDetail

class JSONRPCNotification(BaseModel):
    """JSON-RPC notification message."""
    jsonrpc: Literal["2.0"] = JSONRPC_VERSION
    method: str
    params: BaseParams = Field(default_factory=BaseParams)

JSONRPCMessage = Union[JSONRPCRequest, JSONRPCResponse, JSONRPCError, JSONRPCNotification]