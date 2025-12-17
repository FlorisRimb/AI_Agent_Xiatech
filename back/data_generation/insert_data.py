import httpx
import asyncio

from synthetic_data_generator_update import generate_synthetic_data

async def insert_item(item_type, item):
    url = f"http://localhost:8000/api/{item_type}"
    headers = {"accept": "application/json", "Content-Type": "application/json"}
    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, json=item)
        if response.status_code in [200, 201]:
            try:
                print(f"Inserted into {item_type}: {response.status_code}")
                if response.text:
                    print(response.json())
            except:
                print(f"Response: {response.text}")
        else:
            print(f"Error inserting into {item_type}: {response.status_code}")
            print(f"Response: {response.text}")
        return response

async def insert_product(df_product):
    for _, row in df_product.iterrows():
        row = row.to_dict()
        await insert_item("products", row)

async def insert_sale(df_sale):
    for _, row in df_sale.iterrows():
        row = row.to_dict()
        await insert_item("sales", row)

async def insert_stock(df_stock):
    for _, row in df_stock.iterrows():
        row = row.to_dict()
        await insert_item("stocks", row)

async def insert_sku_supplier(df_sku_supplier) :
    for _, row in df_sku_supplier.iterrows():
        row = row.to_dict()
        await insert_item("sku_supplier", row)


if __name__ == "__main__":
    print("This module provides functions to insert data into the database via API calls.")
    # Insert synthetic data
    products_df, sales_df, stock_df, sku_supplier = generate_synthetic_data()

    asyncio.run(insert_product(products_df))
    asyncio.run(insert_sale(sales_df))
    asyncio.run(insert_stock(stock_df))
    #asyncio.run(insert_sku_supplier(sku_supplier))