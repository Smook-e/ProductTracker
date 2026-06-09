
from datetime import datetime, timedelta, timezone

from sqlalchemy import  func
from celery_app import celery_app
from database import SyncSessionLocal # Your existing sync sessionmaker
from models import Product, PriceHistory, UserProduct # Your working database models
# Assume you export your scrape utility function from your scraping file
from scraper.generic import scrape_generic





@celery_app.task
def scrape_and_update_product(url: str, user_id: int):
    

    db = SyncSessionLocal()
    try:
        # Query if product url already exists
        product = db.query(Product).filter(Product.url == url).first()

        if product:
            # product.next_scrape = datetime.now(timezone.utc) + timedelta(hours=2)
            
            # Check if user has already added the product to their watchlist
            rel_check = db.query(UserProduct).filter(
                UserProduct.user_id == user_id,
                UserProduct.product_id == product.id
            ).first()
            
            if not rel_check:
                db.add(UserProduct(user_id=user_id, product_id=product.id))
        else:
            try:
                product_data, price = scrape_generic(str(url))
            except ValueError as e:
                raise Exception(str(e))
            product_data["url"] = url
            product = Product(**product_data)
            product.next_scrape = datetime.now(timezone.utc) + timedelta(hours=2)
            
            db.add(product)
            db.flush()  # Forces generation of product.id
            
            db.add(UserProduct(user_id=user_id, product_id=product.id))

        # Record price timeline capture
            db.add(PriceHistory(price=price, product_id=product.id))

        db.commit()
        db.refresh(product)

        # Count users watching this product 
        count = db.query(func.count(UserProduct.user_id).label("user_count"))\
                  .filter(UserProduct.product_id == product.id)\
                  .scalar()

        db.refresh(product)
        product.user_count = count   

        return f"Successfully processed tracking records for product url: {url}"

    except Exception as e:
        db.rollback()
        raise
    finally:
        db.close()