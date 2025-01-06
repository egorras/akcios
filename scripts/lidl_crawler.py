from datetime import datetime, timedelta
import logging
from typing import List, Dict, Any
from .base_crawler import BaseCrawler
import requests

logger = logging.getLogger(__name__)

class LidlCrawler(BaseCrawler):
    def __init__(self):
        super().__init__("LIDL")
        
    def validate_url(self, url: str) -> bool:
        """Check if URL returns a valid response."""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            }
            response = requests.head(url, timeout=5, headers=headers, allow_redirects=True)
            return response.status_code == 200
        except Exception as e:
            logger.debug(f"URL validation failed for {url}: {e}")
            return False
            
    def get_catalog_info(self) -> List[Dict[str, Any]]:
        catalogs = []
        
        try:
            # Get current date
            now = datetime.now()
            
            # Generate for previous week (current catalog) and current week (next catalog)
            for week_offset in [-1, 0]:
                try:
                    # Calculate date for this iteration
                    target_date = now + timedelta(days=7 * week_offset)
                    # Find Thursday of that week (weekday 3 = Thursday)
                    thursday = target_date - timedelta(days=target_date.weekday()) + timedelta(days=3)
                    
                    # Set time to midnight
                    valid_from = datetime.combine(thursday.date(), datetime.min.time())
                    valid_to = datetime.combine((valid_from + timedelta(days=6)).date(), datetime.min.time())
                    
                    # Get week number
                    week_num = valid_from.isocalendar()[1]
                    year = valid_from.year
                    
                    # Generate URL
                    url = f"https://www.lidl.hu/l/hu/ujsag/akcios-ujsag-{week_num:02d}-het-{year}/ar/0?lf=HHZ"
                    
                    # Validate URL
                    if not self.validate_url(url):
                        logger.debug(f"Skipping invalid URL: {url}")
                        continue
                    
                    catalog = {
                        'url': url,
                        'valid_from': valid_from.isoformat(),
                        'valid_to': valid_to.isoformat(),
                        'last_updated': datetime.now().isoformat()
                    }
                    
                    catalogs.append(catalog)
                    logger.debug(f"Created catalog entry: {catalog}")
                    
                except Exception as e:
                    logger.error(f"Error processing week offset {week_offset}: {e}")
                    continue
            
            logger.info(f"Generated {len(catalogs)} catalog entries")
            return catalogs
            
        except Exception as e:
            logger.error(f"Error generating Lidl catalogs: {e}")
            return [] 