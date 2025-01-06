from datetime import datetime, timedelta
import logging
from typing import List, Dict, Any
from .base_crawler import BaseCrawler
import requests

logger = logging.getLogger(__name__)

class TescoCrawler(BaseCrawler):
    def __init__(self):
        super().__init__("TESCO")
                    
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
                    valid_to = datetime.combine((valid_from + timedelta(days=6)).date(), datetime.max.time())
                    
                    # Format date components for URL
                    formatted_date = valid_from.strftime("%Y-%m-%d")
                    year, month, day = formatted_date.split('-')
                    
                    # Generate URLs for both hypermarket and supermarket
                    store_types = ['hipermarket']
                    
                    for store_type in store_types:
                        url = f"https://tesco.hu/katalogus-oldalak/{store_type}/tesco-ujsag-{year}-{month}-{day}/"
                        
                        catalog = {
                            'url': url,
                            'valid_from': valid_from.isoformat(),
                            'valid_to': valid_to.isoformat(),
                            'last_updated': datetime.now().isoformat(),
                            'active': True
                        }
                        
                        catalogs.append(catalog)
                        logger.debug(f"Created catalog entry: {catalog}")
                    
                except Exception as e:
                    logger.error(f"Error processing week offset {week_offset}: {e}")
                    continue
            
            logger.info(f"Generated {len(catalogs)} catalog entries")
            return catalogs
            
        except Exception as e:
            logger.error(f"Error generating Tesco catalogs: {e}")
            return [] 