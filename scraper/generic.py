from urllib.parse import urlparse

import httpx

from scraper.factory import ScraperFactory
from scraper.config import HEADERS

def handle_amazon_url(url: str) -> str:
    # Keep only the canonical /dp/<product-id> path so cache keys stay stable.
    parsed_url = urlparse(url)
    path_parts = parsed_url.path.split('/')
    try:
        dp_index = path_parts.index('dp')
        clean_path = '/'.join(path_parts[dp_index:dp_index+2])
        url = f"{parsed_url.scheme}://{parsed_url.netloc}/{clean_path}"
        
    except ValueError:
        pass
    return url

def scrape_generic(url: str) -> dict:
    # Normalize Amazon links first, then scrape using a domain-specific parser.
    if "amazon" in urlparse(url).netloc:
        url = handle_amazon_url(url)
    domain = urlparse(url).netloc
    
    response = httpx.get(url, headers=HEADERS, timeout=10)
    response.raise_for_status()

    scraper = ScraperFactory.create_scraper(domain, response.text)

    if scraper.title == "N/A" and scraper.price == "N/A":
        raise ValueError("Failed to scrape product data")
    return {
        "title": scraper.title,
        "image_url": scraper.image_url,
        "source": domain,
        "url": url
    }, scraper.price