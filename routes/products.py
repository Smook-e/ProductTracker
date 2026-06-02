from fastapi import APIRouter, Depends, HTTPException, status

from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from models import Product, PriceHistory, UserProduct
from scraper.generic import scrape_generic
from schemas import ProductScrapeRequest, ProductScrapeResponse, ProductRead
from datetime import timedelta
router = APIRouter(
    prefix="/products",
    tags=["products"],
)

@router.get("/", response_model=list[ProductRead])
async def read_products(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Product))
    return result.scalars().all()

@router.get("/{product_id}", response_model=ProductRead)
async def read_product(product_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Product).where(Product.id == product_id))
    product = result.scalar_one_or_none()
    
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@router.post("/", response_model=ProductScrapeResponse , status_code=status.HTTP_201_CREATED) 
async def create_product(request: ProductScrapeRequest, db: AsyncSession = Depends(get_db)):
    try:
        product_data, price = scrape_generic(str(request.url))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    # db_product = Product(**product_data)
    # db.add(db_product)
    # db.commit()
    # db.refresh(db_product)
    product_data["url"] = str(request.url)
    

    return product_data, price

