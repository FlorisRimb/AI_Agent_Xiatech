from fastapi import FastAPI
import uvicorn
from data_generation.insert_data import insert_product, insert_sale, insert_stock
from data_generation.synthetic_data_generator import generate_synthetic_data

app = FastAPI()
from db.init_db import init_db
from api.router import router
from core.config import settings


app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
)

app.include_router(router, prefix="/api")


@app.get("/")
async def root():
    return {"greeting": "Hello world", "project": settings.PROJECT_NAME}


@app.get("/health")
async def health():
    return {"status": "healthy"}


@app.on_event("startup")
async def on_startup():
    await init_db()
    
    # Insert synthetic data
    products_df, sales_df, stock_df = generate_synthetic_data()
    await insert_product(products_df)
    await insert_sale(sales_df)
    await insert_stock(stock_df)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)