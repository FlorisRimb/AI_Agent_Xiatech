import asyncio
from mcp.server.fastmcp import FastMCP
from datetime import datetime
from http import HTTPStatus
from httpx import AsyncClient

FASTAPI_BASE_URL = "http://localhost:8000/api"

mcp = FastMCP("retail-agent-mcp")


@mcp.tool()
async def get_products_soon_out_of_stock(days: int = 3):
    async with AsyncClient() as client:
        response = await client.get(f"{FASTAPI_BASE_URL}/products_soon_out_of_stock", params={"days": days})
        if response.status_code != HTTPStatus.OK:
            return {"error": f"Erreur {response.status_code}: {response.text}"}
        return response.json()


@mcp.tool()
async def order_product(sku: str, quantity: int):
    async with AsyncClient() as client:
        response = await client.post(f"{FASTAPI_BASE_URL}/order_product", params={"sku": sku, "quantity": quantity})
        if response.status_code != HTTPStatus.CREATED:
            return {"error": f"Erreur {response.status_code}: {response.text}"}
        return response.json()

@mcp.prompt("initialized")
async def on_initialized(params):
    print(f"MCP initialized at {datetime.utcnow().isoformat()} with params: {params}")


if __name__ == "__main__":
    print("Server starting...")
    print(f"Tools: {list(mcp._tool.keys())}")
    mcp.run()