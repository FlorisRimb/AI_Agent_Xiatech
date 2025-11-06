import asyncio
from mcp.server.fastmcp import FastMCP
from datetime import datetime
from http import HTTPStatus
from httpx import AsyncClient
from typing import List, Dict
import os

FASTAPI_BASE_URL = os.getenv("FASTAPI_URL", "http://back:8000/api")

mcp = FastMCP("retail-agent-mcp")


@mcp.tool()
async def get_products_soon_out_of_stock(days: int = 3):
    """
    Get products that will be out of stock within the specified number of days.
    
    Args:
        - days: Number of days to look ahead (default: 3)
    
    Returns:
        - List of products with SKU, name, and days until out of stock
    """
    try:
        async with AsyncClient() as client:
            response = await client.get(
                f"{FASTAPI_BASE_URL}/agent/products_soon_out_of_stock",
                params={"days": days}
            )
            if response.status_code != HTTPStatus.OK:
                return {"error": f"Erreur {response.status_code}: {response.text}"}
            return response.json()
    except Exception as e:
        return {"error": str(e)}


# @mcp.tool()
# async def get_stock_level_for_product(sku: str):
#     """
#     Get current stock level for a product.
    
#     Args:
#         sku: Product SKU (e.g., "SKU-0002")
    
#     Returns:
#         Current stock quantity for the product
#     """
#     try:
#         async with AsyncClient() as client:
#             response = await client.post(
#                 f"{FASTAPI_BASE_URL}/agent/stock_level",
#                 json={"sku": sku}
#             )
#             if response.status_code != HTTPStatus.OK:
#                 return {"error": f"Erreur {response.status_code}: {response.text}"}
#             return response.json()
#     except Exception as e:
#         return {"error": str(e)}


# @mcp.tool()
# async def get_daily_sales_for_product(sku: str, days: int = 3):
#     """
#     Get daily sales data for a product.
    
#     Args:
#         sku: Product SKU (e.g., "SKU-0002")
#         days: Number of days of sales history (default: 3)
    
#     Returns:
#         Daily sales quantities for the product
#     """
#     try:
#         async with AsyncClient() as client:
#             response = await client.post(
#                 f"{FASTAPI_BASE_URL}/agent/daily_sales_data",
#                 json={"sku": sku, "days": days}
#             )
#             if response.status_code != HTTPStatus.OK:
#                 return {"error": f"Erreur {response.status_code}: {response.text}"}
#             return response.json()
#     except Exception as e:
#         return {"error": str(e)}


@mcp.tool()
async def order_products(skus: List[str], quantities: List[int]):
    """
    Create a purchase order for a product.
    
    Args:
        - skus (List[str]): The SKUs of the products to order.
        - quantities (List[int]): The quantities of the products to order.
        Note: skus and quantities lists must be of the same length.

    Returns:
        - Order confirmation details.
    """
    try:
        async with AsyncClient() as client:
            response = await client.post(f"{FASTAPI_BASE_URL}/agent/order_products", json={"orders": [{"sku": skus[i], "quantity": quantities[i]} for i in range(len(skus))]})
            if response.status_code != HTTPStatus.CREATED:
                return {"error": f"Erreur {response.status_code}: {response.text}"}
            return response.json()
    except Exception as e:
        return {"error": str(e)}


if __name__ == "__main__":
    print("[MCP Server] Starting Retail Inventory MCP Server")
    print(f"[MCP Server] FastAPI URL: {FASTAPI_BASE_URL}")
    mcp.run()