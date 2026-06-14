
from scraper.factory import amazonScraper, NextJsScraper, GenericScraper, WooCommerceScraper

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 KHTML, like Gecko Chrome/124.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}

SELECTORS = {
    "www.amazon.eg": {
        "title": "span#productTitle",       
        "price": "span.a-price-whole",      
        "image_url": amazonScraper,  
    },
    "www.sigma-computer.com": {
        "title": "h1.text-2xl.font-semibold.text-sigma-blue-600",       
        "price": "span.text-3xl",      
        "image_url": GenericScraper,  
    },
    "hardwaremarket.net": {
        "title": "h1.product_title",       
        "price": "p.price ins span.woocommerce-Price-amount.amount bdi",       
        "image_url": GenericScraper,  
    },
}
