
from datetime import datetime, timedelta, timezone

from sqlalchemy import  func
from celery_app import celery_app
from database import SyncSessionLocal 
from models import Product, PriceHistory, UserProduct 

from scraper.generic import scrape_generic
from utils.product_cache import (
    invalidate_product_list_cache_sync,
    normalize_product_url,
    set_cached_product_by_url_sync,
)





@celery_app.task
def scrape_and_update_product(url: str, user_id: int):
    db = SyncSessionLocal()
    try:
        normalized_url = normalize_product_url(str(url))
        # Reuse existing product records to avoid duplicate product rows per URL.
        product = db.query(Product).filter(Product.url == normalized_url).first()

        if product:
            # Attach the requesting user to the existing product if needed.
            rel_check = db.query(UserProduct).filter(
                UserProduct.user_id == user_id,
                UserProduct.product_id == product.id
            ).first()
            
            if not rel_check:
                db.add(UserProduct(user_id=user_id, product_id=product.id))
        else:
            try:
                product_data, price = scrape_generic(normalized_url)
            except ValueError as e:
                raise Exception(str(e))
            except Exception as scrape_error:
                raise Exception(f"Failed to scrape product data: {str(scrape_error)}")
            product = Product(**product_data)
            product.next_scrape = datetime.now(timezone.utc) + timedelta(hours=2)
            
            db.add(product)
            db.flush()
            
            db.add(UserProduct(user_id=user_id, product_id=product.id))

            # Seed first price snapshot for trend history.
            db.add(PriceHistory(price=price, product_id=product.id))

        db.commit()
        db.refresh(product)

        # Refresh cache payload with the latest watcher count.
        count = db.query(func.count(UserProduct.user_id).label("user_count"))\
                  .filter(UserProduct.product_id == product.id)\
                  .scalar()

        db.refresh(product)
        product.user_count = count   
        set_cached_product_by_url_sync(product, count)
        invalidate_product_list_cache_sync()

        return f"Successfully processed tracking records for product url: {url}"

    except Exception as e:
        db.rollback()
        raise
    finally:
        db.close()