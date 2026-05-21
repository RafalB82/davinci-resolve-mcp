#!/usr/bin/env python3
"""
DaVinci Resolve MCP Server — HTTP transport wrapper (streamable-http).

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
        "--mount-path",
        default="/mcp",
        help="Path to mount the transport on (default: /mcp)",
    )
    args = parser.parse_args()

    if args.full:
        logger.info("Loading granular server (329 tools)...")
        from src.granular import mcp as resolve_mcp
    else:
        logger.info("Loading compound server (32 tools)...")
        from src.server import mcp as resolve_mcp

    # Use streamable-http app directly
    app = resolve_mcp.streamable_http_app()

    logger.info(f"Starting DaVinci Resolve MCP server on http://{args.host}:{args.port}/mcp")
    logger.info("OpenClaw config:")
    logger.info(f'  "url": "http://{args.host}:{args.port}/mcp",')
    logger.info(f'  "transport": "streamable-http"')
    logger.warning("SECURITY: No built-in authentication. Run only on a trusted LAN network.")

    uvicorn.run(
        app,
        host=args.host,
        port=args.port,
        log_level="info",
    )


if __name__ == "__main__":
    main()
