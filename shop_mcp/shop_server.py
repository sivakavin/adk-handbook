import os
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
port = int(os.environ.get("PORT", 8080))

mcp = FastMCP(
    "Shop MCP Server",
    host="0.0.0.0",
    port=port,
    streamable_http_path="/mcp",
)

# # Port 8080 avoids the clash with `adk web`, which uses 8000.
# mcp = FastMCP(
#     "shop",
#     host=MCP_HOST,
#     port=MCP_PORT,
#     streamable_http_path="/mcp",
# )


@mcp.tool()
def get_price(item: str) -> dict:
    """Return the price of a shop item."""
    prices = {"apple": 30, "banana": 10, "milk": 50}
    return {"item": item, "price": prices.get(item.lower(), "not found")}


@mcp.tool()
def list_item() -> dict:
    """List all items available in the shop."""
    return {"items": ["apple", "banana", "milk"]}


if __name__ == "__main__":
    mcp.run(transport="streamable-http")


