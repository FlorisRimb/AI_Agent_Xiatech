import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

# --- CONFIG ---
NUM_PRODUCTS = 50
AVG_ORDERS_PER_DAY = 160    # total number of orders in a day
MAX_ITEMS_PER_ORDER = 3     # max number of SKUs per order
REORDER_THRESHOLD_DAYS = 3
FIXED_REORDER_QTY = 200
np.random.seed(42)
random.seed(42)

def generate_synthetic_data():
    # --- 1. Generate Product Data ---
    categories = ["Electronics", "Home", "Clothing", "Books", "Toys"]
    product_data = {
        "sku": [f"SKU-{i:04d}" for i in range(1, NUM_PRODUCTS + 1)],
        "name": [f"Product_{i}" for i in range(1, NUM_PRODUCTS + 1)],
        "category": np.random.choice(categories, NUM_PRODUCTS),
        "price": np.round(np.random.uniform(5, 500, NUM_PRODUCTS), 2),
    }
    products_df = pd.DataFrame(product_data)

    # --- 2. Generate Orders and Sales Lines ---
    yesterday = datetime.now() - timedelta(days=1)
    sales_records = []
    order_counter = 10000

    for _ in range(AVG_ORDERS_PER_DAY):
        order_counter += 1
        order_id = f"ORDER_{order_counter}"
        order_time = yesterday + timedelta(seconds=random.randint(0, 24 * 60 * 60 - 1))
        order_skus = random.sample(list(products_df["sku"]), k=random.randint(1, MAX_ITEMS_PER_ORDER))

        for sku in order_skus:
            sales_records.append({
                "transaction_id": order_id,
                "sku": sku,
                "timestamp": order_time.strftime("%Y-%m-%d %H:%M:%S"),
                "quantity": np.random.randint(1, 5)  # 1–4 units per line
            })

    sales_df = pd.DataFrame(sales_records)

    # --- 3. Generate Stock Data ---
    stock_data = {
        "sku": products_df["sku"],
        "stock_on_hand": np.random.randint(10, 500, size=NUM_PRODUCTS),
    }
    stock_df = pd.DataFrame(stock_data)
    
    return products_df, sales_df, stock_df

# print("Generating synthetic data...")
# products_df, sales_df, stock_df = generate_synthetic_data()
# print("Products Data:")
# print(products_df)
# print("\nSales Transactions Data:")
# print(sales_df)
# print("\nStock Levels Data:")
# print(stock_df)
# print("Data generation complete.")


# # --- 4. Print Summaries ---
# print("\n=== Products ===")
# print(products_df)

# print("\n=== Example Sales Transactions ===")
# print(sales_df)


# print("\n=== Stock Levels ===")
# print(stock_df)

# # --- 5. (Optional) Export to CSV ---
# products_df.to_csv("./data_generation/products.csv", index=False)
# sales_df.to_csv("./data_generation/sales_transactions.csv", index=False)
# #sales_agg.to_csv("sales_aggregated.csv", index=False)
# stock_df.to_csv("./data_generation/stock.csv", index=False)
# #po_df.to_csv("purchase_orders.csv", index=False)
# #adjusted_stock_df.to_csv("adjusted_stock.csv", index=False)

# print("\n✅ Data generation complete. CSV files saved.")


