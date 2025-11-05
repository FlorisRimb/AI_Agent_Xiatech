import asyncio
from mcp.server.fastmcp import FastMCP
from datetime import datetime
from http import HTTPStatus
from httpx import AsyncClient
import os

FASTAPI_BASE_URL = os.getenv("FASTAPI_URL", "http://back:8000/api")

mcp = FastMCP("retail-agent-mcp")


@mcp.tool()
async def get_products_soon_out_of_stock(days: int = 3):
    """
    Get a list of products that will be out of stock within a specified number of days.
    
    Args:
        days (int): Number of days to look ahead. Products that will be out of stock 
                   within this timeframe will be returned. Default is 3 days.
                   Example: days=7 returns products running out within a week.
    """
    try:
        async with AsyncClient() as client:
            response = await client.get(f"{FASTAPI_BASE_URL}/agent/products_soon_out_of_stock", params={"days": days})
            if response.status_code != HTTPStatus.OK:
                return {"error": f"Erreur {response.status_code}: {response.text}"}
            return response.json()
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
async def order_product(sku: str, quantity: int):
    """
    Create a purchase order for a product.
    
    Args:
        sku (str): The SKU of the product to order.
                   Example: "SKU-001"
        quantity (int): The quantity of the product to order.
                        Example: quantity=50
    """
    try:
        async with AsyncClient() as client:
            response = await client.post(f"{FASTAPI_BASE_URL}/agent/order_product", json={"sku": sku, "quantity": quantity})
            if response.status_code != HTTPStatus.CREATED:
                return {"error": f"Erreur {response.status_code}: {response.text}"}
            return response.json()
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
async def get_daily_sales_for_product(sku: str, days: int = 3):
    """
    Retrieve daily sales data for a product over a specified time period.
    
    Args:
        sku (str): The SKU of the product to retrieve sales data for.
                   Example: "SKU-001"
        days (int): Number of days to retrieve sales data for. Default is 3 days.
                    Example: days=7 retrieves sales data for the past week.
    """
    try:
        async with AsyncClient() as client:
            response = await client.post(f"{FASTAPI_BASE_URL}/agent/daily_sales_data", json={"sku": sku, "days": days})
            if response.status_code != HTTPStatus.OK:
                return {"error": f"Erreur {response.status_code}: {response.text}"}
            return response.json()
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
async def get_stock_levels_for_product(sku: str):
    """
    Get current stock levels for a product.
    
    Args:
        sku (str): The SKU of the product to check stock levels for.
                   Example: "SKU-001"
    """
    try:
        async with AsyncClient() as client:
            response = await client.post(f"{FASTAPI_BASE_URL}/agent/stock_level", json={"sku": sku})
            if response.status_code != HTTPStatus.OK:
                return {"error": f"Erreur {response.status_code}: {response.text}"}
            return response.json()
    except Exception as e:
        return {"error": str(e)}


if __name__ == "__main__":
    print("[MCP Server] Starting Retail Inventory MCP Server")
    print(f"[MCP Server] FastAPI URL: {FASTAPI_BASE_URL}")
    print(f"[MCP Server] Tools registered: get_products_soon_out_of_stock, order_products, get_daily_sales_for_products, get_stock_levels_for_products")
    mcp.run()