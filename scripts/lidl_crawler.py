import requests
from bs4 import BeautifulSoup
from datetime import datetime
import re
from .base_crawler import BaseCrawler, logger

class LidlCrawler(BaseCrawler):
    def __init__(self):
        super().__init__("LIDL")
    
    def parse_date(self, date_text: str) -> datetime:
        """Parse date from text like 'Érvényes 01.09-től'"""
        try:
            # Extract date part (e.g., "01.09")
            match = re.search(r'(\d{2})\.(\d{2})', date_text)
            if match:
                month, day = match.groups()
                current_year = datetime.now().year
                
                # Try current year first
                try:
                    date = datetime(current_year, int(month), int(day))
                                            
                    return date
                    
                except ValueError as e:
                    logger.debug(f"Invalid date: {month}/{day}: {e}")
                    return None
                    
        except (ValueError, AttributeError) as e:
            logger.debug(f"Error parsing date '{date_text}': {e}")
        return None

    def get_catalog_info(self):
        url = 'https://www.lidl.hu/c/szorolap/s10013623'
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

        logger.info(f"Fetching URL: {url}")
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        catalogs = []
        seen_urls = set()
        
        # Find the "Akciós szórólapok" section
        main_section = soup.find('h2', string='Akciós szórólapok')
        if not main_section:
            logger.warning("Could not find 'Akciós szórólapok' section")
            return catalogs
            
        section = main_section.find_parent('section')
        if not section:
            logger.warning("Could not find parent section")
            return catalogs
        
        # Find all flyer links within this section
        flyer_links = section.find_all('a', class_='flyer')
        logger.info(f"Found {len(flyer_links)} flyer links")
        
        for link in flyer_links:
            url = link.get('href', '')
            
            if not url or url in seen_urls:
                continue
            
            # Skip non-food catalogs
            title_elem = link.find('h4', class_='flyer__title')
            if title_elem and 'nonfood' in title_elem.text.lower():
                logger.debug(f"Skipping non-food catalog: {url}")
                continue
                
            seen_urls.add(url)
            logger.debug(f"Processing link: {url}")
            
            # Get flyer name and title
            name_elem = link.find('h2', class_='flyer__name')
            title = title_elem.text.strip() if title_elem else ''
            name = name_elem.text.strip() if name_elem else ''
            
            # Find validity date
            valid_text = name if 'érvényes' in name.lower() else title
            if not valid_text or 'érvényes' not in valid_text.lower():
                continue
            
            valid_from = self.parse_date(valid_text)
            if not valid_from:
                continue
            
            # Assume valid for one week
            valid_to = datetime(valid_from.year, valid_from.month, valid_from.day + 6)
            
            # Get image URL if available
            img = link.find('img', class_='flyer__image')
            image_url = img.get('src', '') if img else None
            
            catalog = {
                'title': title,  # Use just the title, not the combined name+title
                'url': url,
                'valid_from': valid_from,
                'valid_to': valid_to,
                'image_url': image_url,
                'last_updated': datetime.now()
            }
            
            logger.debug(f"Created catalog entry: {catalog}")
            catalogs.append(catalog)
        
        logger.info(f"Found {len(catalogs)} unique food catalogs with valid dates")
        return catalogs 