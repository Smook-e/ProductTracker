from urllib.parse import urlparse, parse_qs, unquote

import httpx

# from factory import ScraperFactory
from scraper.factory import ScraperFactory
from scraper.config import HEADERS
#urlparse: Splits a URL string into component parts (like protocol, domain, path, and query).




def handle_amazon_url(url: str) -> str:
    parsed_url = urlparse(url)
    path_parts = parsed_url.path.split('/')
    try:
        dp_index = path_parts.index('dp')
        clean_path = '/'.join(path_parts[dp_index:dp_index+2])  # Keep /dp/PRODUCTID
        url = f"{parsed_url.scheme}://{parsed_url.netloc}/{clean_path}"
        
    except ValueError:
        pass  # If dp not found, keep original URL
    return url

def scrape_generic(url: str) -> dict:
    
    domain = urlparse(url).netloc
    
    if "amazon" in domain:
        url = handle_amazon_url(url)
        
    
    response = httpx.get(url, headers=HEADERS, timeout=10)
    response.raise_for_status()

    #get the appropriate scraper class based on the domain, defaulting to GenericScraper if no specific one is found
    scraper = ScraperFactory.create_scraper(domain, response.text)

    if scraper.title == "N/A" and scraper.price == "N/A":
        raise ValueError("Failed to scrape product data")
    # print(scraper.title, "\n",  scraper.price)
    return {
        "title": scraper.title,
        "image_url": scraper.image_url,
        "source": domain,
        "url": url
    }, scraper.price
    
    



url = "https://www.noon.com/egypt-en/band-11-pro-smart-watch-enhanced-sleep-tracking-health-gnss-position-fitness-tracker-up-to-14-day-battery-life-ultra-slim-comfort-wear-compatible-with-ios-android-black/N70285078V/p/?o=ad0ca7c6c05b11ae&shareId=51f2f9c5-f6fa-419d-8377-77e666b670c5"
# print(scrape_generic(url))