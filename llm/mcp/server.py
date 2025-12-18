import asyncio
from mcp.server.fastmcp import FastMCP
from datetime import datetime, timedelta, timezone
from http import HTTPStatus
from httpx import AsyncClient
from typing import List, Dict
import os

FASTAPI_BASE_URL = os.getenv("FASTAPI_URL", "http://back:8000/api")

mcp = FastMCP("retail-agent-mcp")


@mcp.tool()
async def soon_out_of_stock_products(days: int = 5):
    """
    Get a list of products that are soon out of stock based on current stock and recent sales trends.

    Args:
        days (int): The number of days to look ahead for stock depletion.

    Returns:
        List of products with their SKUs, current stock, average daily sales, estimated days until out of stock, and recommended order quantity for 2 weeks of stock.
    """
    try:
        async with AsyncClient() as client:

            # Get current stock levels
            stock_response = await client.get(f"{FASTAPI_BASE_URL}/stocks/virtual/all")
            if stock_response.status_code != HTTPStatus.OK:
                error_msg = f"Error getting stock levels: {stock_response.status_code}: {stock_response.text}"
                return {"error": error_msg}

            # Get sales data for the past 'days' period to calculate average
            sales_response = await client.get(f"{FASTAPI_BASE_URL}/sales", params={"days": days})
            if sales_response.status_code != HTTPStatus.OK:
                error_msg = f"Error getting sales data: {sales_response.status_code}: {sales_response.text}"
                return {"error": error_msg}

            stocks = stock_response.json()
            sales = sales_response.json()

            # Calculate average daily sales per SKU
            sales_aggregation: Dict[str, int] = {}
            for sale in sales:
                sku = sale["sku"]
                quantity = sale["quantity"]
                sales_aggregation[sku] = sales_aggregation.get(sku, 0) + quantity

            # Determine products that will run out in the given days
            result = []
            for stock in stocks:
                sku = stock["sku"]
                current_stock = stock.get("virtual_stock", stock["stock_on_hand"])
                total_sales = sales_aggregation.get(sku, 0)

                # Calculate average daily sales (total sales / number of days analyzed)
                average_daily_sales = total_sales / days if days > 0 else 0

                # Calculate days until out of stock
                if average_daily_sales > 0:
                    days_until_out = current_stock / average_daily_sales
                    if days_until_out <= days:
                        # Calculate recommended order quantity for 4 weeks of stock
                        # Target: have enough for 28 days based on current sales rate
                        target_stock = average_daily_sales * 28

                        result.append({
                            "sku": sku,
                            "current_stock": current_stock,
                            "average_daily_sales": round(average_daily_sales, 2),
                            "days_until_out_of_stock": round(days_until_out, 2),
                            "recommended_order_quantity": target_stock
                        })
                elif current_stock == 0:
                    # Already out of stock - recommend ordering based on recent sales or default
                    if total_sales > 0:
                        # Use average from the period
                        avg_sales = total_sales / days
                        recommended_quantity = int(avg_sales * 28)  # 4 weeks
                        recommended_quantity = max(recommended_quantity, 300)
                    else:
                        # No sales history, use default
                        recommended_quantity = 300

                    result.append({
                        "sku": sku,
                        "current_stock": current_stock,
                        "average_daily_sales": round(average_daily_sales, 2),
                        "days_until_out_of_stock": 0,
                        "recommended_order_quantity": recommended_quantity
                    })

            return sorted(result, key=lambda x: x["days_until_out_of_stock"])

    except Exception as e:
        error_msg = str(e)
        return {"error": error_msg}


@mcp.tool()
async def get_products(category: str | None = None, name: str | None = None, limit: int = 50):
    """
    Get a list of products with optional filters.

    Args:
        category (str, optional): Filter by product category.
        name (str, optional): Filter by product name (partial match).
        limit (int): Maximum number of products to return. Default is 50.

    Returns:
        List of products with their SKUs, names, categories, and prices.
    """
    try:
        async with AsyncClient() as client:
            params = {"limit": limit}
            if category:
                params["category"] = category
            if name:
                params["name"] = name

            response = await client.get(f"{FASTAPI_BASE_URL}/products", params=params)
            if response.status_code != HTTPStatus.OK:
                error_msg = f"Error getting products: {response.status_code}: {response.text}"
                return {"error": error_msg}

            data = response.json()
            result = [{
                "sku": item["sku"],
                "name": item["name"],
                "category": item["category"],
                "price": item["price"]
            } for item in data]

            return result
    except Exception as e:
        error_msg = str(e)
        return {"error": error_msg}


@mcp.tool()
async def get_sales(sku: str | None = None, days: int | None = None, limit: int = 100):
    """
    Get sales transactions with optional filters.

    Args:
        sku (str, optional): Filter by product SKU.
        days (int, optional): Get sales from the last N days.
        limit (int): Maximum number of transactions to return. Default is 100.

    Returns:
        List of sales transactions with SKU, quantity, and timestamp.
    """
    try:
        async with AsyncClient() as client:
            params = {"limit": limit}
            if sku:
                params["sku"] = sku
            if days is not None:
                params["days"] = days

            response = await client.get(f"{FASTAPI_BASE_URL}/sales", params=params)
            if response.status_code != HTTPStatus.OK:
                error_msg = f"Error getting sales: {response.status_code}: {response.text}"
                return {"error": error_msg}

            data = response.json()
            result = [{
                "transaction_id": item["transaction_id"],
                "sku": item["sku"],
                "quantity": item["quantity"],
                "timestamp": item["timestamp"]
            } for item in data]

            return result
    except Exception as e:
        error_msg = str(e)
        return {"error": error_msg}


@mcp.tool()
async def get_stock_levels(sku: str | None = None, min_stock: int | None = None, max_stock: int | None = None, limit: int = 100):
    """
    Get stock levels with optional filters.

    Args:
        sku (str, optional): Filter by product SKU.
        min_stock (int, optional): Filter products with stock >= this value.
        max_stock (int, optional): Filter products with stock <= this value.
        limit (int): Maximum number of items to return. Default is 100.

    Returns:
        List of stock levels with SKU and stock on hand.
    """
    try:
        async with AsyncClient() as client:
            params = {"limit": limit}
            if sku:
                params["sku"] = sku
            if min_stock is not None:
                params["min_stock"] = min_stock
            if max_stock is not None:
                params["max_stock"] = max_stock

            response = await client.get(f"{FASTAPI_BASE_URL}/stocks", params=params)
            if response.status_code != HTTPStatus.OK:
                error_msg = f"Error getting stock levels: {response.status_code}: {response.text}"
                return {"error": error_msg}

            data = response.json()
            result = [{
                "sku": item["sku"],
                "stock_on_hand": item["stock_on_hand"]
            } for item in data]

            return result
    except Exception as e:
        error_msg = str(e)
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
        if not sku or not sku.strip():
            error_msg = "SKU cannot be empty"
            return {"error": error_msg}

        if quantity <= 0:
            error_msg = "Quantity must be positive"
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
                return {"error": error_msg}

            return {"message": f"Order placed for SKU {sku}, quantity {quantity}."}
    except Exception as e:
        error_msg = str(e)
        return {"error": error_msg}


@mcp.tool()
async def get_orders_by_status(status: str = "pending", days: int | None = None):
    """
    Get a list of product orders by status, optionally filtered by age.

    Args:
        status (str): The status of orders to retrieve. Default is "pending".
        days (int, optional): If provided, only return orders from the last N days.

    Returns:
        List of orders with their SKUs, quantities, order dates, and order IDs.
    """
    try:
        async with AsyncClient() as client:
            params = {"status": status}
            if days is not None:
                params["days"] = days

            response = await client.get(f"{FASTAPI_BASE_URL}/orders", params=params)
            if response.status_code != HTTPStatus.OK:
                error_msg = f"Erreur {response.status_code}: {response.text}"
                return {"error": error_msg}

            data = response.json()
            result = [{"order_id": item["order_id"], "sku": item["sku"], "quantity": item["quantity"], "order_date": item["order_date"]} for item in data]

            return result
    except Exception as e:
        error_msg = str(e)
        return {"error": error_msg}


@mcp.tool()
async def update_order_status(order_id: str, status: str):
    """
    Update the status of a product order.

    Args:
        order_id (str): The ID of the order to update.
        status (str): The new status for the order. Can be "pending", "completed", or "canceled".

    Returns:
        Confirmation message or error.
    """
    try:

        if not order_id or not order_id.strip():
            error_msg = "Order ID cannot be empty"
            return {"error": error_msg}

        if status not in ["pending", "completed", "canceled"]:
            error_msg = "Invalid status value"
            return {"error": error_msg}

        async with AsyncClient() as client:
            update_data = {
                "status": status
            }
            response = await client.put(f"{FASTAPI_BASE_URL}/orders/{order_id.strip()}", json=update_data)
            if response.status_code != HTTPStatus.OK:
                error_msg = f"Erreur {response.status_code}: {response.text}"
                return {"error": error_msg}

            return {"message": f"Order {order_id} updated to status {status}."}
    except Exception as e:
        error_msg = str(e)
        return {"error": error_msg}



if __name__ == "__main__":
    mcp.run()




