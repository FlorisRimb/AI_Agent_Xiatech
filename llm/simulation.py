"""
Retail Inventory Simulation Script

This script simulates a retail inventory management system by:
1. Running an AI agent to identify and order low-stock products
2. Generating random sales transactions (based on realistic data patterns)
3. Decreasing stock based on sales
4. Delivering pending orders to increase stock

Each iteration runs sequentially to allow stock changes to propagate.

Configuration based on synthetic_data_generator_update.py:
- AVG_ORDERS_PER_DAY: 160 orders
- MAX_ITEMS_PER_ORDER: 1-3 items per order
- QUANTITY_PER_ITEM: 1-5 units
- INITIAL_STOCK: 50-900 units per product
"""

import asyncio
import httpx
import random
import os
from datetime import datetime, timedelta
from app_llm.agent import RetailInventoryAgent


async def run_simulation(agent: RetailInventoryAgent, iterations: int):
    """
    Run the simulation for n iterations sequentially.

    Args:
        agent: The RetailInventoryAgent instance
        iterations: Number of iterations to run
        base_url: Base URL for the FastAPI backend
    """
    print("\n" + "="*80)
    print(f"[SIMULATION] Starting simulation with {iterations} iterations")
    print("="*80)

    base_url = "http://back:8000/api"

    async with httpx.AsyncClient(timeout=30.0) as client:
        # Step 0: Save existing sales before simulation
        print(f"\n[SIMULATION] Saving existing sales data...")
        saved_sales = []
        try:
            existing_sales_response = await client.get(f"{base_url}/sales?limit=10000")
            saved_sales = existing_sales_response.json()
            print(f"[SIMULATION] Saved {len(saved_sales)} existing sales")

            # Delete existing sales to start with clean slate
            if saved_sales:
                print(f"[SIMULATION] Removing existing sales for clean simulation...")
                deleted = 0
                for sale in saved_sales:
                    try:
                        await client.delete(f"{base_url}/sales/{sale['transaction_id']}")
                        deleted += 1
                    except:
                        pass
                print(f"[SIMULATION] Removed {deleted}/{len(saved_sales)} sales")
        except Exception as e:
            print(f"[SIMULATION] Error saving existing sales: {e}")

        await asyncio.sleep(0.5)

        # Track sales created in current iteration
        current_iteration_sales = []

        for iteration in range(1, iterations + 1):
            current_simulation_date = datetime.now()

            print(f"\n{'='*80}")
            print(f"[SIMULATION] Iteration {iteration}/{iterations} - Date: {current_simulation_date.strftime('%Y-%m-%d')}")
            print(f"{'='*80}")

            # Step 1: Generate random sales transactions
            print(f"\n[SIMULATION] Step 1: Generating random sales...")
            try:
                # Get all products
                products_response = await client.get(f"{base_url}/products")
                products = products_response.json()

                if not products:
                    print(f"[SIMULATION] No products found, skipping sales generation")
                else:
                    orders_per_iteration = 80
                    max_items_per_order = 3

                    created_sales = 0
                    total_items = 0

                    for _ in range(orders_per_iteration):
                        # Each order has 1-3 items
                        num_items = random.randint(1, max_items_per_order)
                        order_skus = random.sample(products, min(num_items, len(products)))

                        for product in order_skus:
                            quantity = random.randint(1, 20)

                            # Create sale transaction with TODAY's timestamp
                            sale_data = {
                                "sku": product["sku"],
                                "quantity": quantity,
                                "timestamp": current_simulation_date.isoformat()
                            }
                            sale_response = await client.post(f"{base_url}/sales", json=sale_data)
                            if sale_response.status_code == 201:
                                created_sales += 1
                                total_items += quantity
                                # Track this sale to delete it at the end of iteration
                                sale_result = sale_response.json()
                                current_iteration_sales.append(sale_result["transaction_id"])

                    print(f"[SIMULATION] Created {created_sales} sales ({total_items} items total from {orders_per_iteration} orders)")
            except Exception as e:
                print(f"[SIMULATION] Error generating sales: {e}")
                import traceback
                traceback.print_exc()

            # Wait for sales to be processed
            await asyncio.sleep(0.5)

            # Step 2: Decrease stock based on sales
            print(f"\n[SIMULATION] Step 2: Decreasing stock based on sales...")
            try:
                # Get sales for the current simulation day
                day_start = current_simulation_date.replace(hour=0, minute=0, second=0, microsecond=0)
                day_end = current_simulation_date.replace(hour=23, minute=59, second=59, microsecond=999999)

                sales_response = await client.get(
                    f"{base_url}/sales",
                    params={
                        "start_date": day_start.isoformat(),
                        "end_date": day_end.isoformat(),
                        "limit": 1000
                    }
                )
                iteration_sales = sales_response.json()

                # Group sales by SKU and sum quantities
                sales_by_sku = {}
                for sale in iteration_sales:
                    sku = sale["sku"]
                    qty = sale["quantity"]
                    sales_by_sku[sku] = sales_by_sku.get(sku, 0) + qty

                # Update stock levels
                stock_updates = 0
                for sku, total_qty in sales_by_sku.items():
                    stock_response = await client.get(f"{base_url}/stocks/{sku}")
                    if stock_response.status_code == 200:
                        stock = stock_response.json()
                        new_stock = max(0, stock["stock_on_hand"] - total_qty)

                        update_response = await client.put(
                            f"{base_url}/stocks/{sku}",
                            json={"stock_on_hand": new_stock}
                        )

                        if update_response.status_code == 200:
                            print(f"[SIMULATION] Updated {sku}: {stock['stock_on_hand']} -> {new_stock} (sold: {total_qty})")
                            stock_updates += 1

                print(f"[SIMULATION] Updated stock for {stock_updates} products")
            except Exception as e:
                print(f"[SIMULATION] Error decreasing stock: {e}")
                import traceback
                traceback.print_exc()

            # Wait for stock updates to propagate
            await asyncio.sleep(0.5)


            # Step 3: Run restock agent to check stock and place orders
            print(f"\n[SIMULATION] Step 3: Running restock agent...")
            restock_query = "Based of the daily sales, determine the products that will run out of stock in the next 7 days. After identifying them, place orders to restock each products with its sufficient amount to last a least one week. If no products need restocking, simply respond with [DONE]."
            try:
                response = await agent.run_with_tools(restock_query)
                print(f"[SIMULATION] Restock agent response: {response[:200]}...")
            except Exception as e:
                print(f"[SIMULATION] Error running restock agent: {e}")
                import traceback
                traceback.print_exc()

            # Wait for agent to complete before continuing
            await asyncio.sleep(1)

            # Step 4: Deliver pending orders
            print(f"\n[SIMULATION] Step 4: Delivering pending orders...")
            try:
                orders_response = await client.get(f"{base_url}/orders?status=pending")
                pending_orders = orders_response.json()

                if pending_orders:
                    delivered_count = 0
                    for order in pending_orders:
                        # Update order status to completed (this automatically increases stock)
                        update_response = await client.put(
                            f"{base_url}/orders/{order['order_id']}",
                            json={"status": "completed"}
                        )

                        if update_response.status_code == 200:
                            print(f"[SIMULATION] Delivered order {order['order_id']}: {order['sku']} +{order['quantity']}")
                            delivered_count += 1

                        # Small delay between deliveries
                        await asyncio.sleep(0.2)

                    print(f"[SIMULATION] Delivered {delivered_count}/{len(pending_orders)} pending orders")
                else:
                    print(f"[SIMULATION] No pending orders to deliver")
            except Exception as e:
                print(f"[SIMULATION] Error delivering orders: {e}")
                import traceback
                traceback.print_exc()

            # Step 5: Clean up sales from this iteration
            if current_iteration_sales:
                print(f"\n[SIMULATION] Step 5: Cleaning up {len(current_iteration_sales)} sales from this iteration...")
                deleted_count = 0
                for transaction_id in current_iteration_sales:
                    try:
                        delete_response = await client.delete(f"{base_url}/sales/{transaction_id}")
                        if delete_response.status_code == 204:
                            deleted_count += 1
                    except Exception as e:
                        print(f"[SIMULATION] Error deleting sale {transaction_id}: {e}")

                print(f"[SIMULATION] Deleted {deleted_count}/{len(current_iteration_sales)} sales")
                # Reset for next iteration
                current_iteration_sales = []

            # Wait between iterations to allow system to stabilize
            if iteration < iterations:
                print(f"\n[SIMULATION] Waiting before next iteration...")
                await asyncio.sleep(3)



    # Restore original sales after simulation
    if saved_sales:
        print(f"\n{'='*80}")
        print(f"[SIMULATION] Restoring {len(saved_sales)} original sales...")
        restored = 0
        for sale in saved_sales:
            try:
                # Remove the _id field if present (MongoDB internal field)
                sale_data = {k: v for k, v in sale.items() if k != '_id' and k != 'id'}
                await client.post(f"{base_url}/sales", json=sale_data)
                restored += 1
            except Exception as e:
                print(f"[SIMULATION] Error restoring sale {sale.get('transaction_id')}: {e}")

        print(f"[SIMULATION] Restored {restored}/{len(saved_sales)} sales")

    print(f"\n{'='*80}")
    print(f"[SIMULATION] Simulation completed after {iterations} iterations")
    print(f"{'='*80}\n")


async def main():
    """Main entry point for the simulation."""
    # Configuration
    iterations = int(os.getenv("SIMULATION_ITERATIONS", "5"))
    model_path = os.getenv("MODEL_PATH", "/app/qwen2.5-7b-instruct-q4_k_m-00001-of-00002.gguf")
    base_url = "http://back:8000/api"

    print("[SIMULATION] Initializing agent...")

    # Check if model file exists
    if os.path.exists(model_path):
        file_size = os.path.getsize(model_path)
        print(f"[SIMULATION] Model file found: {model_path}")
        print(f"[SIMULATION] Model file size: {file_size / (1024**3):.2f} GB")
    else:
        print(f"[SIMULATION] ERROR: Model file not found at {model_path}")
        return

    try:
        # Initialize agent
        agent = RetailInventoryAgent(model_path)
        print("[SIMULATION] Agent ready")

        # Run simulation
        await run_simulation(agent, iterations, base_url)

    except Exception as e:
        print(f"[SIMULATION] ERROR: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
