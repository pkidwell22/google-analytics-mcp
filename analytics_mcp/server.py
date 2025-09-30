#!/usr/bin/env python

# Copyright 2025 Google LLC All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Entry point for the Google Analytics MCP server."""

import argparse
import os
import sys
from typing import Optional

from analytics_mcp.coordinator import mcp

# The following imports are necessary to register the tools with the `mcp`
# object, even though they are not directly used in this file.
# The `# noqa: F401` comment tells the linter to ignore the "unused import"
# warning.
from analytics_mcp.tools.admin import info  # noqa: F401
from analytics_mcp.tools.admin import conversions  # noqa: F401
from analytics_mcp.tools.admin import data_streams  # noqa: F401
from analytics_mcp.tools.admin import custom_definitions  # noqa: F401
from analytics_mcp.tools.reporting import realtime  # noqa: F401
from analytics_mcp.tools.reporting import core  # noqa: F401
from analytics_mcp.tools import gsc  # noqa: F401
from analytics_mcp.tools import gmc  # noqa: F401


def run_server(transport: str = "stdio", port: Optional[int] = None) -> None:
    """Runs the server.

    Args:
        transport: The transport method to use ("stdio" or "http")
        port: The port to use for HTTP transport (required if transport is "http")
    """
    if transport == "http":
        if port is None:
            port = int(os.environ.get("PORT", 8080))
        
        # Use streamable-http transport for MCP over HTTP
        # The port is configured in the FastMCP constructor, not in run()
        mcp.run(transport="streamable-http")
    else:
        mcp.run()


def main() -> None:
    """Main entry point with argument parsing."""
    parser = argparse.ArgumentParser(description="Google Analytics MCP Server")
    parser.add_argument(
        "--transport",
        choices=["stdio", "http"],
        default="stdio",
        help="Transport method to use (default: stdio)"
    )
    parser.add_argument(
        "--port",
        type=int,
        help="Port for HTTP transport (default: 8080 or PORT env var)"
    )
    
    args = parser.parse_args()
    
    if args.transport == "http" and args.port is None:
        args.port = int(os.environ.get("PORT", 8080))
    
    run_server(transport=args.transport, port=args.port)


if __name__ == "__main__":
    main()
