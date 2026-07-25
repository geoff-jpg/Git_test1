#!/usr/bin/env python3
"""
Stdio MCP server that provides tools for chunking large prompts/text
into smaller pieces suitable for LLM context windows.
"""

import json
import sys
import textwrap
from typing import Any

# MCP protocol version
PROTOCOL_VERSION = "2024-11-05"
SERVER_NAME = "chunk-prompt-server"
SERVER_VERSION = "1.0.0"

TOOLS = [
    {
        "name": "chunk_text",
        "description": (
            "Split a large text or prompt into chunks of a specified size. "
            "Useful for processing documents that exceed LLM context limits."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "text": {
                    "type": "string",
                    "description": "The text or prompt to chunk.",
                },
                "chunk_size": {
                    "type": "integer",
                    "description": "Maximum number of characters per chunk (default: 2000).",
                    "default": 2000,
                },
                "overlap": {
                    "type": "integer",
                    "description": "Number of characters to overlap between chunks (default: 0).",
                    "default": 0,
                },
            },
            "required": ["text"],
        },
    },
    {
        "name": "chunk_by_tokens",
        "description": (
            "Split text into chunks by approximate token count. "
            "Assumes ~4 characters per token as a rough estimate."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "text": {
                    "type": "string",
                    "description": "The text or prompt to chunk.",
                },
                "max_tokens": {
                    "type": "integer",
                    "description": "Maximum tokens per chunk (default: 500).",
                    "default": 500,
                },
                "overlap_tokens": {
                    "type": "integer",
                    "description": "Tokens to overlap between chunks (default: 0).",
                    "default": 0,
                },
            },
            "required": ["text"],
        },
    },
    {
        "name": "chunk_by_paragraphs",
        "description": (
            "Split text into chunks by paragraph boundaries, grouping paragraphs "
            "until the chunk size limit is reached."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "text": {
                    "type": "string",
                    "description": "The text or prompt to chunk.",
                },
                "max_chars": {
                    "type": "integer",
                    "description": "Maximum characters per chunk (default: 2000).",
                    "default": 2000,
                },
            },
            "required": ["text"],
        },
    },
    {
        "name": "chunk_by_sentences",
        "description": (
            "Split text into chunks at sentence boundaries, keeping chunks "
            "under the specified character limit."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "text": {
                    "type": "string",
                    "description": "The text or prompt to chunk.",
                },
                "max_chars": {
                    "type": "integer",
                    "description": "Maximum characters per chunk (default: 2000).",
                    "default": 2000,
                },
            },
            "required": ["text"],
        },
    },
]


# --- chunking logic ---

def chunk_text(text: str, chunk_size: int = 2000, overlap: int = 0) -> list[str]:
    if chunk_size <= 0:
        raise ValueError("chunk_size must be positive")
    if overlap < 0 or overlap >= chunk_size:
        raise ValueError("overlap must be >= 0 and < chunk_size")

    chunks = []
    step = chunk_size - overlap
    start = 0
    while start < len(text):
        chunks.append(text[start : start + chunk_size])
        start += step
    return chunks


def chunk_by_tokens(text: str, max_tokens: int = 500, overlap_tokens: int = 0) -> list[str]:
    chars_per_token = 4
    chunk_size = max_tokens * chars_per_token
    overlap = overlap_tokens * chars_per_token
    return chunk_text(text, chunk_size=chunk_size, overlap=overlap)


def chunk_by_paragraphs(text: str, max_chars: int = 2000) -> list[str]:
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    chunks = []
    current: list[str] = []
    current_len = 0

    for para in paragraphs:
        # If a single paragraph exceeds the limit, break it up with textwrap.
        if len(para) > max_chars:
            if current:
                chunks.append("\n\n".join(current))
                current, current_len = [], 0
            for sub in textwrap.wrap(para, width=max_chars):
                chunks.append(sub)
            continue

        # Would adding this paragraph exceed the limit?
        sep_len = 2 if current else 0  # "\n\n" separator
        if current_len + sep_len + len(para) > max_chars and current:
            chunks.append("\n\n".join(current))
            current, current_len = [], 0

        current.append(para)
        current_len += len(para) + (2 if len(current) > 1 else 0)

    if current:
        chunks.append("\n\n".join(current))

    return chunks or [text]


def chunk_by_sentences(text: str, max_chars: int = 2000) -> list[str]:
    import re
    sentences = re.split(r"(?<=[.!?])\s+", text)
    chunks = []
    current: list[str] = []
    current_len = 0

    for sentence in sentences:
        sep_len = 1 if current else 0  # space separator
        if current_len + sep_len + len(sentence) > max_chars and current:
            chunks.append(" ".join(current))
            current, current_len = [], 0

        # Single oversized sentence — emit as-is.
        if len(sentence) > max_chars:
            if current:
                chunks.append(" ".join(current))
                current, current_len = [], 0
            chunks.append(sentence)
            continue

        current.append(sentence)
        current_len += len(sentence) + sep_len

    if current:
        chunks.append(" ".join(current))

    return chunks or [text]


def _format_chunks_result(chunks: list[str]) -> list[dict]:
    return [
        {
            "type": "text",
            "text": json.dumps(
                {
                    "total_chunks": len(chunks),
                    "chunks": [
                        {
                            "index": i,
                            "length": len(c),
                            "text": c,
                        }
                        for i, c in enumerate(chunks)
                    ],
                },
                ensure_ascii=False,
                indent=2,
            ),
        }
    ]


def call_tool(name: str, arguments: dict[str, Any]) -> list[dict]:
    if name == "chunk_text":
        chunks = chunk_text(
            text=arguments["text"],
            chunk_size=int(arguments.get("chunk_size", 2000)),
            overlap=int(arguments.get("overlap", 0)),
        )
        return _format_chunks_result(chunks)

    if name == "chunk_by_tokens":
        chunks = chunk_by_tokens(
            text=arguments["text"],
            max_tokens=int(arguments.get("max_tokens", 500)),
            overlap_tokens=int(arguments.get("overlap_tokens", 0)),
        )
        return _format_chunks_result(chunks)

    if name == "chunk_by_paragraphs":
        chunks = chunk_by_paragraphs(
            text=arguments["text"],
            max_chars=int(arguments.get("max_chars", 2000)),
        )
        return _format_chunks_result(chunks)

    if name == "chunk_by_sentences":
        chunks = chunk_by_sentences(
            text=arguments["text"],
            max_chars=int(arguments.get("max_chars", 2000)),
        )
        return _format_chunks_result(chunks)

    raise ValueError(f"Unknown tool: {name}")


# --- MCP stdio transport ---

def send(msg: dict) -> None:
    line = json.dumps(msg, ensure_ascii=False)
    sys.stdout.write(line + "\n")
    sys.stdout.flush()


def handle(request: dict) -> None:
    method = request.get("method")
    req_id = request.get("id")

    def ok(result: Any) -> None:
        if req_id is not None:
            send({"jsonrpc": "2.0", "id": req_id, "result": result})

    def err(code: int, message: str) -> None:
        if req_id is not None:
            send({"jsonrpc": "2.0", "id": req_id, "error": {"code": code, "message": message}})

    if method == "initialize":
        ok(
            {
                "protocolVersion": PROTOCOL_VERSION,
                "capabilities": {"tools": {}},
                "serverInfo": {"name": SERVER_NAME, "version": SERVER_VERSION},
            }
        )

    elif method == "notifications/initialized":
        pass  # no response for notifications

    elif method == "tools/list":
        ok({"tools": TOOLS})

    elif method == "tools/call":
        params = request.get("params", {})
        tool_name = params.get("name", "")
        arguments = params.get("arguments", {})
        try:
            content = call_tool(tool_name, arguments)
            ok({"content": content})
        except ValueError as exc:
            err(-32602, str(exc))
        except Exception as exc:
            err(-32603, f"Internal error: {exc}")

    elif method == "ping":
        ok({})

    else:
        if req_id is not None:
            err(-32601, f"Method not found: {method}")


def main() -> None:
    for raw_line in sys.stdin:
        raw_line = raw_line.strip()
        if not raw_line:
            continue
        try:
            request = json.loads(raw_line)
        except json.JSONDecodeError as exc:
            send({"jsonrpc": "2.0", "id": None, "error": {"code": -32700, "message": f"Parse error: {exc}"}})
            continue
        handle(request)


if __name__ == "__main__":
    main()
