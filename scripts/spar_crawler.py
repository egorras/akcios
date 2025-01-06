from datetime import datetime, timedelta
import logging
from typing import List, Dict, Any
from .base_crawler import BaseCrawler
import requests

logger = logging.getLogger(__name__)

class SparCrawler(BaseCrawler):
    def __init__(self):
        super().__init__("SPAR")
        
    def validate_url(self, url: str) -> bool:
        """Check if URL returns a valid response."""
        try:
            response = requests.head(url, timeout=5)
            return response.status_code == 200
        except Exception as e:
            logger.debug(f"URL validation failed for {url}: {e}")
            return False
            
    def get_catalog_info(self) -> List[Dict[str, Any]]:
        catalogs = []
        
        try:
            # Get current date and calculate weeks
            now = datetime.now()
            current_year = str(now.year)[2:] # Get last 2 digits of year
            
            # Generate for previous week (current catalog) and current week (next catalog)
            for week_offset in [-1, 0]:
                try:
                    # Calculate date for this iteration
                    target_date = now + timedelta(days=7 * week_offset)
                    # Find Thursday of that week (weekday 3 = Thursday)
                    thursday = target_date - timedelta(days=target_date.weekday()) + timedelta(days=3)
                    
                    # Set time to midnight
                    valid_from = datetime.combine(thursday.date(), datetime.min.time())
                    valid_to = datetime.combine((valid_from + timedelta(days=6)).date(), datetime.max.time())
                    
                    # Format date components
                    year_short = str(thursday.year)[2:]
                    month = f"{thursday.month:02d}"
                    day = f"{thursday.day:02d}"
                    
                    # Try both 'm' and 'p' suffixes for each date
                    for suffix in ['m', 'p']:
                        # Generate URL in format: YYMMDD-1-spar-szorolap-[m/p]
                        catalog_id = f"{year_short}{month}{day}-1-spar-szorolap-{suffix}"
                        url = f"https://www.spar.hu/ajanlatok/spar/{catalog_id}"
                        
                        # Validate URL
                        if not self.validate_url(url):
                            logger.debug(f"Skipping invalid URL: {url}")
                            continue
                        
                        catalog = {
                            'url': url,
                            'valid_from': valid_from.isoformat(),
                            'valid_to': valid_to.isoformat(),
                            'last_updated': datetime.now().isoformat(),
                        }
                        
                        catalogs.append(catalog)
                        logger.debug(f"Created catalog entry: {catalog}")
                    
                except Exception as e:
                    logger.error(f"Error processing week offset {week_offset}: {e}")
                    continue
            
            logger.info(f"Generated {len(catalogs)} catalog entries")
            return catalogs
            
        except Exception as e:
            logger.error(f"Error generating SPAR catalogs: {e}")
            return [] 