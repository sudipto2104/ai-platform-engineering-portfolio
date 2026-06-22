"""FastAPI MCP-compatible server exposing platform engineering tools."""

from __future__ import annotations

import os
from typing import Any

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from mcp_server.tools import call_tool, list_tools

app = FastAPI(title="Platform Assistant MCP Server", version="1.0.0")


class JSONRPCRequest(BaseModel):
    jsonrpc: str = "2.0"
    id: str | int | None = None
    method: str
    params: dict[str, Any] = Field(default_factory=dict)


class ToolCallRequest(BaseModel):
    name: str
    arguments: dict[str, Any] = Field(default_factory=dict)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "healthy"}


@app.get("/tools")
async def get_tools() -> dict[str, Any]:
    return {"tools": list_tools()}


@app.post("/tools/call")
async def invoke_tool(request: ToolCallRequest) -> dict[str, Any]:
    try:
        content = call_tool(request.name, request.arguments)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return {"name": request.name, "content": content}


@app.post("/mcp")
async def mcp_handler(request: JSONRPCRequest) -> dict[str, Any]:
    if request.method == "tools/list":
        result = {"tools": list_tools()}
    elif request.method == "tools/call":
        tool_name = request.params.get("name")
        arguments = request.params.get("arguments", {})
        if not tool_name:
            raise HTTPException(status_code=400, detail="Missing tool name")
        result = {"content": [{"type": "text", "text": call_tool(tool_name, arguments)}]}
    else:
        raise HTTPException(status_code=400, detail=f"Unsupported method: {request.method}")

    return {"jsonrpc": "2.0", "id": request.id, "result": result}


def main() -> None:
    import uvicorn

    port = int(os.getenv("MCP_PORT", "8090"))
    uvicorn.run("mcp_server.server:app", host="0.0.0.0", port=port, reload=False)


if __name__ == "__main__":
    main()