from urllib.parse import urlparse, parse_qs, unquote

import httpx

from scraper.factory import ScraperFactory

#urlparse: Splits a URL string into component parts (like protocol, domain, path, and query).
#parse_qs: Parses the query string of a URL into a dictionary of key-value pairs.
#unquote: Decodes percent-encoded characters in a URL string back to their original form


HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
}

def scrape_generic(url: str) -> dict:
    
    domain = urlparse(url).netloc
    

    response = httpx.get(url, headers=HEADERS, timeout=10)
    response.raise_for_status()

    


    scraper = ScraperFactory.create_scraper(domain, response.text)
    return {
        "title": scraper.title,
        "price": scraper.price,
        "image_url": scraper.image_url,
    }
    
    



url = "https://www.sigma-computer.com/en/item?id=dell-vostro-3520-intel-core-i5-1235u-intel-uhd-graphics-8gb-ddr4-3200hz-512gb-nvme-156-inch-fhd-va-250nits-120hz-dos-carbon-black-8syhihudtt0t"
scrape_generic(url)