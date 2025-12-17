import asyncio
from mcp.server.fastmcp import FastMCP
from datetime import datetime, timezone
from http import HTTPStatus
from httpx import AsyncClient
from typing import List, Dict
import os

FASTAPI_BASE_URL = os.getenv("FASTAPI_URL", "http://back:8000/api")

mcp = FastMCP("retail-agent-mcp")


async def save_to_history(response: str, history_type: str):
    """Save agent interaction to history."""
    try:
        async with AsyncClient() as client:
            history_data = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "response": response,
                "type": history_type
            }
            await client.post(f"{FASTAPI_BASE_URL}/agent", json=history_data)
    except Exception as e:
        print(f"[History] Error saving to history: {e}")


@mcp.tool()
async def get_products_stock_levels():
    """
    Get a list of products with their stock levels

    Returns:
        List of products with their SKUs and stock levels.
    """
    try:
        async with AsyncClient() as client:
            await save_to_history(
                "Getting products stock levels",
                "tool"
            )

            response = await client.get(f"{FASTAPI_BASE_URL}/stocks")
            if response.status_code != HTTPStatus.OK:
                error_msg = f"Erreur {response.status_code}: {response.text}"
                await save_to_history("Error getting products stock levels", "tool")
                return {"error": error_msg}

            data = response.json()
            await save_to_history(f"{len(data)} products successfully retrieved", "tool")
            result = [{"sku": item["sku"], "stock": item["stock_on_hand"]} for item in data]

            return result
    except Exception as e:
        error_msg = str(e)
        await save_to_history("Error getting products stock levels", "tool")
        return {"error": error_msg}


@mcp.tool()
async def order_product(sku: str, quantity: int):
    """
    Place an order for a product to replenish stock.

    Args:
        sku (str): The SKU of the product to order.
        quantity (int): The quantity to order.
    Returns:
        Confirmation message or error.
    """
    try:
        await save_to_history(f"Ordering {quantity} units of {sku}", "tool")

        if not sku or not sku.strip():
            error_msg = "SKU cannot be empty"
            await save_to_history("Error when ordering product", "tool")
            return {"error": error_msg}

        if quantity <= 0:
            error_msg = "Quantity must be positive"
            await save_to_history("Error when ordering product", "tool")
            return {"error": error_msg}

        async with AsyncClient() as client:
            order_data = {
                "sku": sku.strip(),
                "quantity": quantity,
                "order_date": datetime.now(timezone.utc).isoformat()
            }
            response = await client.post(f"{FASTAPI_BASE_URL}/orders", json=order_data)
            if response.status_code != HTTPStatus.CREATED:
                error_msg = f"Erreur {response.status_code}: {response.text}"
                await save_to_history("Error when ordering product", "tool")
                return {"error": error_msg}

            # Save to history
            await save_to_history(f"Order of {quantity} units of {sku} successfully placed", "tool")

            return {"message": f"Order placed for SKU {sku}, quantity {quantity}."}
    except Exception as e:
        error_msg = str(e)
        await save_to_history("Error when ordering product", "tool")
        return {"error": error_msg}


@mcp.tool()
async def get_average_daily_sales(days: int):
    """
    Get average daily sales per product SKU for the past given number of days.

    Args:
        days (int): Number of days back from today to retrieve sales for.

    Returns:
        List of products with their SKUs and average daily sales.
    """
    try:
        async with AsyncClient() as client:
            await save_to_history(
                f"Getting sales for the past {days} days",
                "tool"
            )

            response = await client.get(f"{FASTAPI_BASE_URL}/sales", params={"limit": 1000})
            if response.status_code != HTTPStatus.OK:
                error_msg = f"Erreur {response.status_code}: {response.text}"
                await save_to_history("Error getting daily sales", "tool")
                return {"error": error_msg}

            data = response.json()
            cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
            filtered_sales = [
                sale for sale in data
                if datetime.fromisoformat(sale["timestamp"]).replace(tzinfo=timezone.utc) >= cutoff_date
            ]

            sales_summary: Dict[str, int] = {}
            for sale in filtered_sales:
                sku = sale["sku"]
                quantity = sale["quantity"]
                sales_summary[sku] = sales_summary.get(sku, 0) + quantity

            result = [{"sku": sku, "total_quantity_sold": qty} for sku, qty in sales_summary.items()]

            await save_to_history(f"Retrieved sales data for {len(result)} products", "tool")
            return result
    except Exception as e:
        error_msg = str(e)
        await save_to_history("Error getting daily sales", "tool")
        return {"error": error_msg}


if __name__ == "__main__":
    mcp.run()




