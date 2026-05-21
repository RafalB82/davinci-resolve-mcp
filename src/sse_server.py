#!/usr/bin/env python3
"""
DaVinci Resolve MCP Server — Streamable HTTP transport wrapper.

Allows the MCP server to run over HTTP instead of stdio,
enabling remote AI assistants (e.g. OpenClaw on another machine
in the same LAN) to control DaVinci Resolve.

Usage:
    python src/sse_server.py                    # compound server (default)
    python src/sse_server.py --full             # granular 329-tool server
    python src/sse_server.py --host 0.0.0.0
    python src/sse_server.py --port 8765

Requires:
    pip install uvicorn
"""

import argparse
import logging
import os
import sys

import uvicorn
from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

current_dir = os.path.dirname(os.path.abspath(__file__))
project_dir = os.path.dirname(current_dir)
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)
if project_dir not in sys.path:
    sys.path.insert(0, project_dir)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("davinci-resolve-mcp.sse")


class BypassHostCheckMiddleware(BaseHTTPMiddleware):
    """Override the strict Host check so LAN clients can connect."""

    async def dispatch(self, request: Request, call_next):
        # Patch the Host header to satisfy MCP's transport_security
        request.headers.__dict__["_list"].append(
            (b"host", b"localhost:8765")
        )
        # Also patch scope
        request.scope["headers"].append((b"host", b"localhost:8765"))
        return await call_next(request)


def main():
    parser = argparse.ArgumentParser(
        description="DaVinci Resolve MCP Server (HTTP transport)"
    )
    parser.add_argument(
        "--full",
        action="store_true",
        help="Run the 329-tool granular server instead of the 32-tool compound server",
    )
    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="Host to bind to (default: 0.0.0.0)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8765,
        help="Port to listen on (default: 8765)",
    )
    parser.add_argument(
        "--mode",
        choices=["sse", "streamable-http"],
        default="streamable-http",
        help="Transport mode: sse or streamable-http (default: streamable-http)",
    )
    args = parser.parse_args()

    if args.full:
        logger.info("Loading granular server (329 tools)...")
        from src.granular import mcp as resolve_mcp
    else:
        logger.info("Loading compound server (32 tools)...")
        from src.server import mcp as resolve_mcp

    if args.mode == "streamable-http":
        app = resolve_mcp.streamable_http_app()
        endpoint_path = "/"
        logger.info("Using streamable-http mode (POST /)")
    else:
        app = resolve_mcp.sse_app(mount_path=args.mount_path)
        endpoint_path = args.mount_path or "/sse"
        logger.info("Using SSE mode (GET /sse, POST /messages)")

    # Wrap with middleware to bypass Host header check for LAN access
    # Wrap with middleware to bypass Host header check for LAN access
    # Build kwargs only Starlette version supports
    starlette_kwargs = {
        "routes": app.routes,
        "middleware": [Middleware(BypassHostCheckMiddleware)],
    }
    # Some Starlette versions don't accept on_startup/on_shutdown
    if hasattr(app.router, "on_startup") and app.router.on_startup:
        try:
            starlette_kwargs["on_startup"] = app.router.on_startup
        except TypeError:
            pass
    if hasattr(app.router, "on_shutdown") and app.router.on_shutdown:
        try:
            starlette_kwargs["on_shutdown"] = app.router.on_shutdown
        except TypeError:
            pass
    app = Starlette(**starlette_kwargs)

    logger.info(
        "Starting DaVinci Resolve MCP server on "
        f"http://{args.host}:{args.port}{endpoint_path}"
    )
    logger.info(
        "OpenClaw config:\n"
        f'  "url": "http://{args.host}:{args.port}/",\n'
        f'  "transport": "{args.mode}"'
    )
    logger.warning(
        "SECURITY: No built-in authentication. "
        "Run only on a trusted LAN network."
    )

    uvicorn.run(
        app,
        host=args.host,
        port=args.port,
        log_level="info",
        forwarded_allow_ips="*",
    )


if __name__ == "__main__":
    main()
