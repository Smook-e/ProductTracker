from fastapi import APIRouter, Depends, HTTPException, status

from sqlalchemy import select, update, delete, func
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from models import Product, PriceHistory, UserProduct
from scraper.generic import scrape_generic
from schemas import ProductScrapeRequest, ProductScrapeResponse, ProductRead
from datetime import timedelta, datetime
from utils.oauth2 import get_current_user
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
async def read_all_products(db: AsyncSession = Depends(get_db), current_user: dict = Depends(get_current_user)):
    
    
    
    stmt = select(Product, user_count_subquery).order_by(user_count_subquery.desc())  
    
    product_result = await db.execute(stmt)
    product_rows = product_result.all()  
    
    products_list = []
    
    
    for product, user_count in product_rows:
        product.user_count = user_count
        products_list.append(product)
        
    return products_list

@router.get("/me", response_model=list[ProductRead])
async def read_user_products(db: AsyncSession = Depends(get_db), current_user: dict = Depends(get_current_user)):
    user_id = int(current_user["user_id"])
    
    stmt = (
        select(Product, user_count_subquery)
        .join(UserProduct, Product.id == UserProduct.product_id)
        .where(UserProduct.user_id == user_id)
    )
    result = await db.execute(stmt)
    product_rows = result.all() # Use .all() to keep both items in the row tuple
    
    products_list = []
    
    # Unpack exactly like your working single-product endpoint
    for product, user_count in product_rows:
        product.user_count = user_count
        products_list.append(product)
    return products_list

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
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@router.post("/", response_model=ProductRead , status_code=status.HTTP_201_CREATED) 
async def create_product(request: ProductScrapeRequest, db: AsyncSession = Depends(get_db), current_user: dict = Depends(get_current_user)):
    try:
        product_data, price = scrape_generic(str(request.url))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    product_data["url"] = str(request.url)
    db_product = Product(**product_data)
    db_product.next_scrape = datetime.utcnow() + timedelta(hours=2) 

    #save new product to db
    db.add(db_product)
    await db.commit()
    await db.refresh(db_product)

    #add the first price history entry for the product
    price_history = PriceHistory(price=price, product_id=db_product.id)
    db.add(price_history)
    await db.commit()
    await db.refresh(price_history)

    #associate product with user
    user_product = UserProduct(user_id=int(current_user["user_id"]), product_id=db_product.id)
    db.add(user_product)
    await db.commit()
    await db.refresh(user_product)
    
    #one last refresh to get the price history relationship populated
    await db.refresh(db_product)
    return db_product

@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(product_id: int, db: AsyncSession = Depends(get_db), current_user: dict = Depends(get_current_user)):
    result = await db.execute(select(Product).where(Product.id == product_id))
    product = result.scalar_one_or_none()
    
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Then delete the product
    await db.delete(product)
    
    await db.commit()

