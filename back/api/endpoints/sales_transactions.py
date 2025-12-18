from fastapi import APIRouter, HTTPException, status
from models.sales_transaction import SalesTransaction
from models.product import Product
from typing import List
from datetime import datetime, timedelta
from pydantic import BaseModel

router = APIRouter()


class SalesTransactionUpdate(BaseModel):
    sku: str | None = None
    quantity: int | None = None
    timestamp: datetime | None = None


@router.post("", response_model=SalesTransaction, status_code=status.HTTP_201_CREATED)
async def create_sale(sale: SalesTransaction):
    """Create a new sales transaction."""
    try:
        product = await Product.find_one(Product.sku == sale.sku)
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product with SKU {sale.sku} not found"
            )

        await sale.insert()
        return sale
    except HTTPException:
        raise
    except Exception as e:
        print(f"[Sales] Error creating sale: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating sale: {str(e)}"
        )


@router.get("", response_model=List[SalesTransaction])
async def list_sales(days: int | None = None, limit: int = 100):
    """List all sales transactions."""
    if days is not None:
        cutoff_date = datetime.now() - timedelta(days=days)
        sales = await SalesTransaction.find(SalesTransaction.timestamp >= cutoff_date).limit(limit).to_list()
    else:
        sales = await SalesTransaction.find_all().limit(limit).to_list()
    return sales


@router.get("/{transaction_id}", response_model=SalesTransaction)
async def get_sale(transaction_id: str):
    """Get a sales transaction by ID."""
    sale = await SalesTransaction.find_one(SalesTransaction.transaction_id == transaction_id)
    if not sale:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Transaction {transaction_id} not found"
        )
    return sale


@router.put("/{transaction_id}", response_model=SalesTransaction)
async def update_sale(
    transaction_id: str,
    update_data: SalesTransactionUpdate
):
    """Update a sales transaction."""
    sale = await SalesTransaction.find_one(SalesTransaction.transaction_id == transaction_id)
    if not sale:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Transaction {transaction_id} not found"
        )

    if update_data.sku is not None:
        product = await Product.find_one(Product.sku == update_data.sku)
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product with SKU {update_data.sku} not found"
            )
        sale.sku = update_data.sku

    if update_data.quantity is not None:
        if update_data.quantity < 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Quantity must be at least 1"
            )
        sale.quantity = update_data.quantity

    if update_data.timestamp is not None:
        sale.timestamp = update_data.timestamp

    await sale.save()
    return sale


@router.delete("/{transaction_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_sale(transaction_id: str):
    """Delete a sales transaction."""
    sale = await SalesTransaction.find_one(SalesTransaction.transaction_id == transaction_id)
    if not sale:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Transaction {transaction_id} not found"
        )

    await sale.delete()