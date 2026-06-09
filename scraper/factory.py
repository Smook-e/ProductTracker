from bs4 import BeautifulSoup
import re




def _parse_price(raw: str) -> int:
    # strips currency symbols, commas, whitespace and converts to cents
    
    cleaned = re.sub(r'[^\d.,]', '', raw)
    
    if cleaned[-1] in ['.', ',']:
        cleaned = cleaned[:-1]
    if not cleaned:
        return 0.0
            
        # 2. If it has both dots and commas (like 3.699,00)
    if '.' in cleaned and ',' in cleaned:
        cleaned = cleaned.replace('.', '').replace(',', '.')
            
        # 3. If it only has a comma acting as a decimal point (like 1234,56)
    elif ',' in cleaned and '.' not in cleaned:
            # Check if comma is a decimal or thousand separator
            # If there are exactly 2 digits after the comma, it's likely a decimal
        if len(cleaned.split(',')[-1]) == 2:
            cleaned = cleaned.replace(',', '.')
        else:
            cleaned = cleaned.replace(',', '') # It's a thousands separator
                
    try:
        return int(float(cleaned) * 100)
    except ValueError:
        return 0.0

class BaseScraper:
    def __init__(self, html: str, htmltitle: str, htmlprice: str):
        self.soup = BeautifulSoup(html, "html.parser")
        
        title_tag = self.soup.select_one(htmltitle)
        price_tag = self.soup.select_one(htmlprice)
        
        self.title = title_tag.text.strip() if title_tag else "N/A"
        self.price = _parse_price(price_tag.text.strip()) if price_tag else "N/A"
        
        self.image_url = ""

    def extract_image(self) -> str:
        raise NotImplementedError()


class WooCommerceScraper(BaseScraper):
    def extract_image(self) -> None:
        img = self.soup.find('img', class_='wp-post-image')
        self.image_url = img.get('data-large_image') or img.get('src') if img else ""
        

class NextJsScraper(BaseScraper):
    def extract_image(self) -> None:
        img = self.soup.select_one('main img[src*="_next/image"]')
        self.image_url = img.get('src') if img else ""
class amazonScraper(BaseScraper):
    def extract_image(self) -> None:
        img = self.soup.select_one('#landingImage')
        self.image_url = img.get('src') if img else ""
class GenericScraper(BaseScraper):
    def extract_image(self) -> None:
        og_img = self.soup.find('meta', property='og:image')
        self.image_url = og_img.get('content', '') if og_img else ""
        print("generic image URL:", self.image_url)


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


class ScraperFactory:
    _MAPPING = SELECTORS.copy()

    @classmethod
    def create_scraper(cls, domain: str, html: str) -> BaseScraper:
        
        
        selectors = cls._MAPPING.get(domain)
        if "amazon" in domain:
            selectors = cls._MAPPING.get("www.amazon.eg")
        if not selectors:
            raise ValueError(f"No scraper class found for {domain}")
        
        Scraper = cls._MAPPING.get(domain, GenericScraper)['image_url'](html, selectors["title"], selectors["price"])
        Scraper.extract_image()
        return Scraper

