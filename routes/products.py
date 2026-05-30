from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from models import Product, PriceHistory, UserProduct
from scraper.generic import scrape_generic
from schemas import ProductScrapeRequest, ProductScrapeResponse

router = APIRouter(
    prefix="/products",
    tags=["products"],
)

@router.post("/", response_model=ProductScrapeResponse , status_code=status.HTTP_201_CREATED) 
async def create_product(request: ProductScrapeRequest, db: Session = Depends(get_db)):
    try:
        product_data = scrape_generic(str(request.url))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    # db_product = Product(**product_data)
    # db.add(db_product)
    # db.commit()
    # db.refresh(db_product)
    product_data["url"] = str(request.url)

    return product_data

