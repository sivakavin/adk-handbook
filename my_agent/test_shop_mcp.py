import asyncio
import json
import os
import sys

from dotenv import load_dotenv
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

load_dotenv()

URL = os.getenv("SHOP_MCP_URL") or "http://127.0.0.1:8080/mcp"


async def main() -> None:
    async with streamablehttp_client(URL) as (read, write, _):
        async with ClientSession(read, write) as session:
            await session.initialize()
            print(f"Connected to {URL}")

            tools = (await session.list_tools()).tools
            print(f"Tools ({len(tools)}):")
            for tool in tools:
                print(f"  - {tool.name}: {tool.description}")

            if len(sys.argv) > 1:
                name = sys.argv[1]
                arguments = json.loads(sys.argv[2]) if len(sys.argv) > 2 else {}
                print(f"\nCalling {name}({arguments}) ...")
                result = await session.call_tool(name, arguments)
                for content in result.content:
                    print(getattr(content, "text", content))


if __name__ == "__main__":
    asyncio.run(main())
