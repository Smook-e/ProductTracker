from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import HttpUrl

from sqlalchemy import select, update, delete, func
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from models import Product, PriceHistory, UserProduct
from schemas import ProductScrapeRequest, ProductScrapeResponse, ProductRead
from datetime import timedelta, datetime
from utils.oauth2 import get_current_user
from utils.product_cache import (
    delete_cached_product_by_url,
    get_cached_product_by_url,
    normalize_product_url,
    set_cached_product_by_url,
)
from worker.tasks import scrape_and_update_product
from utils.product_cache import ASYNC_REDIS
import json
router = APIRouter(
    prefix="/products",
    tags=["products"],
)
user_count_subquery = (
        select(func.count(UserProduct.user_id))
        .where(UserProduct.product_id == Product.id)
        .scalar_subquery().correlate(Product)
        .label("user_count")
    )
@router.get("/", response_model=list[ProductRead])
async def read_all_products(db: AsyncSession = Depends(get_db)):
    cache_key = "products:list:v2"
    
    # 1. Try cache first
    if ASYNC_REDIS:
        cached = await ASYNC_REDIS.get(cache_key)
        if cached:
            return json.loads(cached)

    # 2. Cache miss → query DB
    stmt = select(Product, user_count_subquery).order_by(user_count_subquery.desc())
    # Optional: Add this if you want price histories too
    # .options(selectinload(Product.price_histories))

    result = await db.execute(stmt)
    product_rows = result.all()

    products_data = []
    for product, user_count in product_rows:
        product.user_count = user_count
        product_dict = {
            "id": product.id,
            "title": product.title,
            "url": product.url,
            "image_url": product.image_url,
            "source": product.source,
            "created_at": product.created_at.isoformat(),
            "next_scrape": product.next_scrape.isoformat(),
            "price_histories": [
                {
                    "id": ph.id,
                    "price": ph.price,
                    "recorded_at": ph.recorded_at.isoformat()
                }
                for ph in getattr(product, "price_histories", [])
            ],
            "user_count": user_count,
        }
        products_data.append(product_dict)


    # 3. Cache the full list
    if ASYNC_REDIS:
        await ASYNC_REDIS.set(cache_key, json.dumps(products_data), ex=300)  

    return products_data

@router.get("/me", response_model=list[ProductRead])
async def read_user_products(db: AsyncSession = Depends(get_db), current_user: dict = Depends(get_current_user)):
    user_id = int(current_user["user_id"])
    
    stmt = (
        select(Product, user_count_subquery)
        .join(UserProduct, Product.id == UserProduct.product_id)
        .where(UserProduct.user_id == user_id)
    )
    result = await db.execute(stmt)
    product_rows = result.all() #list of tuples (Product, user_count)
    
    products_list = []
    
    for product, user_count in product_rows:
        product.user_count = user_count
        await set_cached_product_by_url(product, user_count)
        products_list.append(product)
    return products_list

@router.get("/by-url", response_model=ProductRead)
async def read_product_by_url(url: HttpUrl, db: AsyncSession = Depends(get_db)):
    normalized_url = normalize_product_url(str(url))
    cached_product = await get_cached_product_by_url(normalized_url)
    if cached_product:
        print(f"Cache hit")
        return cached_product

    stmt = select(Product, user_count_subquery).where(Product.url == normalized_url)
    product_result = await db.execute(stmt)
    product_row = product_result.first()
    if not product_row:
        raise HTTPException(status_code=404, detail="Product not found")

    product, user_count = product_row
    product.user_count = user_count
    await set_cached_product_by_url(product, user_count)
    return product

@router.get("/{product_id}", response_model=ProductRead)
async def read_product(product_id: int, db: AsyncSession = Depends(get_db)):
    # result = await db.execute(select(Product).where(Product.id == product_id))
    # product = result.scalar_one_or_none()
    
    stmt = select(Product, user_count_subquery).where(Product.id == product_id)
    product_result = await db.execute(stmt)
    product_row = product_result.first()
    if not product_row:
        raise HTTPException(status_code=404, detail="Product not found")
    product, user_count = product_row
    product.user_count = user_count
    await set_cached_product_by_url(product, user_count)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@router.post("/", status_code=status.HTTP_202_ACCEPTED) 
async def create_product(request: ProductScrapeRequest, db: AsyncSession = Depends(get_db), current_user: dict = Depends(get_current_user)):

    urlstr = str(request.url)
    user_id = int(current_user["user_id"])
    scrape_and_update_product.delay(urlstr, user_id)
    return {"message": f"Product scrape initiated for URL: {urlstr}"}

    
@router.delete("/me/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user_product(product_id: int, db: AsyncSession = Depends(get_db), current_user: dict = Depends(get_current_user)):
    user_id = int(current_user["user_id"])
    product = await db.get(Product, product_id)
    result = await db.execute(
        select(UserProduct).where(
            UserProduct.user_id == user_id, 
            UserProduct.product_id == product_id
        )    )
    user_product = result.scalar_one_or_none()
    if not user_product:
        raise HTTPException(status_code=404, detail="Product not found in user's list")
    await db.delete(user_product)
    await db.commit()
    if product:
        await delete_cached_product_by_url(product.url)

@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(product_id: int, db: AsyncSession = Depends(get_db), current_user: dict = Depends(get_current_user)):
    result = await db.execute(select(Product).where(Product.id == product_id))
    product = result.scalar_one_or_none()
    
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Then delete the product
    await db.delete(product)
    
    await db.commit()
    await delete_cached_product_by_url(product.url)

