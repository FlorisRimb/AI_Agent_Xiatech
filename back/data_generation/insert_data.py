import httpx
import pandas as pd

async def insert_item(item_type, item):
    async with httpx.AsyncClient() as client:
        response = await client.post(f"http://back:8000/{item_type}/", json=item.to_dict())
        print(f"Inserted into {item_type}: {response.status_code}")
        return response

async def insert_product(df_product):
    for _, row in df_product.iterrows():
        await insert_item("products", row)

async def insert_sale(df_sale):
    for _, row in df_sale.iterrows():
        await insert_item("sales", row)

async def insert_stock(df_stock):
    for _, row in df_stock.iterrows():
        await insert_item("stock", row)