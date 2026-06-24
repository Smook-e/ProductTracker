from celery_app import celery_app
from database import SyncSessionLocal
from datetime import datetime, timedelta, timezone
import random
import time
from scraper.generic import scrape_generic
from models import Product, PriceHistory


@celery_app.task
def check_expired_products():
    db = SyncSessionLocal()
    try:
        now = datetime.now(timezone.utc)
        prev_is_amazon = False
        
        # Process only products that are due for a refresh cycle.
        expired_products = db.query(Product).filter(Product.next_scrape <= now).all()
        
        if not expired_products:
            return "No expired products found during this cycle."
            
        print(f"[CRON LOOP] Initiating batch update for {len(expired_products)} expired products.")
        
        for product in expired_products:
            try:
                # Fetch latest metadata and price from the source page.
                product_data, price = scrape_generic(str(product.url))
                if prev_is_amazon and "amazon" in product.source:
                    delay_seconds = random.uniform(2, 6)
                    time.sleep(delay_seconds)
                
                # Append a new historical price point.
                db.add(PriceHistory(price=price, product_id=product.id))
                
                # Keep product metadata synchronized with the source listing.
                product.title = product_data.get("title", product.title)
                product.image_url = product_data.get("image_url", product.image_url)
                
                # Schedule next regular refresh.
                product.next_scrape = now + timedelta(hours=2)
                prev_is_amazon = "amazon" in product.source
                db.commit()
                print(f"[SUCCESS] Updated '{product.title}' to new price: {price}")
                
            except Exception as scrape_error:
                # Continue the batch if one product fails to scrape.
                print(f"[ERROR] Skipping {product.url} due to failure: {str(scrape_error)}")
                # Back off retries for broken links to avoid hot-looping.
                product.next_scrape = now + timedelta(hours=15)
                db.commit()
                continue
                
        return f"Successfully processed automated updates for {len(expired_products)} products."
        
    except Exception as e:
        
        print(f"[CRON GLOBAL ERROR] Automated routine failed: {str(e)}")
        raise
    finally:
        db.close()