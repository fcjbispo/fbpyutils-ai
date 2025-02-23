from typing import Any
import httpx

from fbpyutils_ai.tools.search import SearXNGUtils, SearXNGTool
from mcp.server.fastmcp import FastMCP

# Initialize SearXNG tool
searxng = SearXNGTool()

# Initialize FastMCP server
mcp = FastMCP("search")


