from urllib.parse import urlparse, parse_qs, unquote

import httpx

from scraper.factory import ScraperFactory

#urlparse: Splits a URL string into component parts (like protocol, domain, path, and query).
#parse_qs: Parses the query string of a URL into a dictionary of key-value pairs.
#unquote: Decodes percent-encoded characters in a URL string back to their original form


HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 KHTML, like Gecko Chrome/124.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}

def scrape_generic(url: str) -> dict:
    
    domain = urlparse(url).netloc
    

    response = httpx.get(url, headers=HEADERS, timeout=10)
    response.raise_for_status()

    


    scraper = ScraperFactory.create_scraper(domain, response.text)
    if scraper.title == "N/A" and scraper.price == "N/A":
        raise ValueError("Failed to scrape product data")
    # print(scraper.title, "\n",  scraper.price)
    return {
        "title": scraper.title,
        "image_url": scraper.image_url,
        "source": domain,
    }, scraper.price
    
    



url = "https://www.amazon.eg/ASUS-UX3405CA-PZ007W-Graphics-14-0-Inch-Warranty/dp/B0G42FJ9JS/?_encoding=UTF8&ref_=pd_hp_d_btf_ci_mcx_mr_ca_id_hp_d"
# scrape_generic(url)