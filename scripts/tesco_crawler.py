from datetime import datetime, timedelta
import logging
from typing import List, Dict, Any
from .base_crawler import BaseCrawler
from .lidl_crawler import LidlCrawler

logger = logging.getLogger(__name__)

class TescoCrawler(BaseCrawler):
    def __init__(self):
        super().__init__("TESCO")
        
    def get_catalog_info(self) -> List[Dict[str, Any]]:
        catalogs = []
        
        try:
            # Get dates from Lidl crawler
            lidl_crawler = LidlCrawler()
            lidl_catalogs = lidl_crawler.get_catalog_info()
            
            if not lidl_catalogs:
                logger.warning("No Lidl catalogs found to base dates on")
                return []
            
            # Use Lidl dates to generate Tesco URLs
            for lidl_catalog in lidl_catalogs:
                try:
                    # The dates are already datetime objects, no need to parse them
                    valid_from = lidl_catalog['valid_from']
                    valid_to = lidl_catalog['valid_to']
                    
                    if isinstance(valid_from, str):
                        valid_from = datetime.fromisoformat(valid_from)
                    if isinstance(valid_to, str):
                        valid_to = datetime.fromisoformat(valid_to)
                    
                    # Format the date for Tesco URL
                    formatted_date = valid_from.strftime("%Y-%m-%d")
                    year, month, day = formatted_date.split('-')
                    
                    # Generate URLs for both hypermarket and supermarket
                    store_types = ['hipermarket']
                    
                    for store_type in store_types:
                        url = f"https://tesco.hu/katalogus-oldalak/{store_type}/tesco-ujsag-{year}-{month}-{day}/"
                        image_url = f"https://tesco.hu/img/tescoce_hu/leaflets/{year}-{month}-{day}/medium/F1.jpg"
                        
                        catalog = {
                            'url': url,
                            'image_url': image_url,
                            'valid_from': valid_from.isoformat(),
                            'valid_to': valid_to.isoformat(),
                            'last_updated': datetime.now().isoformat()
                        }
                        
                        catalogs.append(catalog)
                        logger.debug(f"Created catalog entry: {catalog}")
                    
                except Exception as e:
                    logger.error(f"Error processing date: {e}, catalog: {lidl_catalog}")
                    continue
            
            logger.info(f"Generated {len(catalogs)} catalog entries")
            return catalogs
            
        except Exception as e:
            logger.error(f"Error generating Tesco catalogs: {e}")
            return [] 