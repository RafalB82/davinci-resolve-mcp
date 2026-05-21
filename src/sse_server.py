#!/usr/bin/env python3
"""
DaVinci Resolve MCP Server — SSE transport wrapper.

Allows the MCP server to run over HTTP/SSE instead of stdio,
enabling remote AI assistants (e.g. OpenClaw on another machine
in the same LAN) to control DaVinci Resolve.

Usage:
    python src/sse_server.py                    # compound server (default)
    python src/sse_server.py --full             # granular 329-tool server
    python src/sse_server.py --host 0.0.0.0     # bind all interfaces
    python src/sse_server.py --port 8765        # custom port

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
        description="DaVinci Resolve MCP Server (SSE transport)"
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
        default=None,
        help="Mount path for SSE endpoint (default: '/')",
    )
    args = parser.parse_args()

    if args.full:
        logger.info("Loading granular server (329 tools)...")
        from src.granular import mcp as resolve_mcp
    else:
        logger.info("Loading compound server (32 tools)...")
        from src.server import mcp as resolve_mcp

    app = resolve_mcp.sse_app(mount_path=args.mount_path)

    logger.info(
        "Starting DaVinci Resolve MCP SSE server on "
        f"http://{args.host}:{args.port}{args.mount_path or '/sse'}"
    )
    logger.info(
        "Connect your MCP client using:\n"
        f"  url: http://{args.host}:{args.port}{args.mount_path or ''}\n"
        "  transport: sse"
    )
    logger.warning(
        "SECURITY: The SSE server has no built-in authentication. "
        "Run only on a trusted LAN network."
    )

    uvicorn.run(app, host=args.host, port=args.port, log_level="info", forwarded_allow_ips="*")


if __name__ == "__main__":
    main()
