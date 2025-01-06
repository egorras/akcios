import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime
from typing import Optional, Tuple
from .base_crawler import BaseCrawler, logger

class AldiCrawler(BaseCrawler):
    def __init__(self):
        super().__init__("ALDI")
    
    def extract_dates_from_url(self, url: str) -> Tuple[Optional[datetime], Optional[datetime]]:
        """Extract dates from URL like 'online_akcios_ujsag_2025_01_02_kw01'"""
        match = re.search(r'_(\d{4})_(\d{2})_(\d{2})_', url)
        if match:
            year, month, day = map(int, match.groups())
            start_date = datetime(year, month, day)
            end_date = datetime(year, month, day + 6)  # Usually valid for a week
            return start_date, end_date
        return None, None
    
    def get_catalog_info(self):
        url = 'https://www.aldi.hu/hu/ajanlatok/online-akcios-ujsag.html'
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

        logger.info(f"Fetching URL: {url}")
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        catalogs = []
        seen_urls = set()
        
        catalog_links = soup.find_all('a', title=re.compile(r'^ALDI online akciós újság'))
        logger.info(f"Found {len(catalog_links)} catalog links")
        
        for link in catalog_links:
            url = link['href']
            
            if url in seen_urls:
                logger.debug(f"Skipping duplicate URL: {url}")
                continue
            
            seen_urls.add(url)
            logger.debug(f"\nProcessing link: {url}")
            
            valid_from, valid_to = self.extract_dates_from_url(url)
            
            if not valid_from or not valid_to:
                logger.debug(f"Skipping entry without valid dates: {url}")
                continue
            
            catalog = {
                'url': url,
                'valid_from': valid_from,
                'valid_to': valid_to,
                'last_updated': datetime.now()
            }
            
            logger.debug(f"Created catalog entry: {catalog}")
            catalogs.append(catalog)
        
        logger.info(f"Found {len(catalogs)} unique catalogs with valid dates")
        return catalogs 