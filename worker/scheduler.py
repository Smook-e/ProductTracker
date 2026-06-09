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
        
        # 1. Fetch all products whose tracking window has expired
        expired_products = db.query(Product).filter(Product.next_scrape <= now).all()
        
        if not expired_products:
            return "No expired products found during this cycle."
            
        print(f"[CRON LOOP] Initiating batch update for {len(expired_products)} expired products.")
        
        for product in expired_products:
            try:
                # 2. Run the scraping engine on the product URL
                product_data, price = scrape_generic(str(product.url))
                if prev_is_amazon and "amazon" in product.source:
                    delay_seconds = random.uniform(2, 6)
                    time.sleep(delay_seconds)
                
                # 3. Add the historical entry 
                db.add(PriceHistory(price=price, product_id=product.id))
                
                # 4. Synchronize core metadata if details updated on the host site
                product.title = product_data.get("title", product.title)
                product.image_url = product_data.get("image_url", product.image_url)
                
                # 5. Push the next tracking target window out by 2 hours
                product.next_scrape = now + timedelta(hours=2)
                prev_is_amazon = "amazon" in product.source
                db.commit()  # Commit after each product to ensure progress is saved even if one fails
                print(f"[SUCCESS] Updated '{product.title}' to new price: {price}")
                
            except Exception as scrape_error:
                
                # Catch failures per item so one broken link doesn't crash the whole batch
                print(f"[ERROR] Skipping {product.url} due to failure: {str(scrape_error)}")
                # Push next check out slightly so it doesn't spin infinitely on a dead link
                product.next_scrape = now + timedelta(hours=15)
                db.commit()  # Save the updated next_scrape even on failure
                continue
                
        return f"Successfully processed automated updates for {len(expired_products)} products."
        
    except Exception as e:
        
        print(f"[CRON GLOBAL ERROR] Automated routine failed: {str(e)}")
        raise
    finally:
        db.close()