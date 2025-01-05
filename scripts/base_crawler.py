from datetime import datetime
import json
import logging
from typing import Optional, List, Dict, Any
import os

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)

class BaseCrawler:
    def __init__(self, store_name: str):
        self.store_name = store_name
    
    def get_catalog_info(self) -> List[Dict[str, Any]]:
        """
        Fetch and parse catalog information.
        Should be implemented by child classes.
        """
        raise NotImplementedError
    
    def update_index_file(self, new_catalogs: List[Dict[str, Any]]):
        """Update the store-specific index file with new catalog data."""
        index_file = f'data/index-{self.store_name.lower()}.json'
        logger.info(f"Updating index file: {index_file}")
        
        os.makedirs('data', exist_ok=True)
        
        existing_catalogs = []
        if os.path.exists(index_file):
            with open(index_file, 'r', encoding='utf-8') as f:
                try:
                    data = json.load(f)
                    for catalog in data:
                        catalog['valid_from'] = self.parse_date(catalog['valid_from']) if catalog.get('valid_from') else None
                        catalog['valid_to'] = self.parse_date(catalog['valid_to']) if catalog.get('valid_to') else None
                        catalog['last_updated'] = datetime.fromisoformat(catalog['last_updated']) if catalog.get('last_updated') else None
                    existing_catalogs = data
                    logger.debug(f"Loaded {len(existing_catalogs)} existing catalogs")
                except json.JSONDecodeError:
                    logger.error("Error reading existing file, starting fresh")
        
        # Create a set of URLs from new catalogs for faster lookup
        new_urls = {catalog['url'] for catalog in new_catalogs}
        
        # Keep only existing catalogs that:
        # 1. Are not in new catalogs
        # 2. Have valid dates
        updated_catalogs = [
            catalog for catalog in existing_catalogs 
            if catalog['url'] not in new_urls 
            and catalog.get('valid_from') 
            and catalog.get('valid_to')
        ]
        
        # Add all new catalogs (we already filtered them for valid dates)
        updated_catalogs.extend(new_catalogs)
        
        # Sort by valid_from date (newest first)
        def sort_key(x):
            valid_from = x.get('valid_from')
            return valid_from if valid_from is not None else datetime.min
        
        updated_catalogs.sort(
            key=sort_key,
            reverse=True
        )
        
        logger.info(f"Writing {len(updated_catalogs)} catalogs to index file")
        with open(index_file, 'w', encoding='utf-8') as f:
            json.dump(updated_catalogs, f, cls=DateTimeEncoder, ensure_ascii=False, indent=2)
    
    @staticmethod
    def parse_date(date_str: str) -> Optional[datetime]:
        """Parse date string to datetime object."""
        try:
            return datetime.strptime(date_str, '%Y.%m.%d')
        except (ValueError, TypeError):
            return None
    
    def run(self):
        """Execute the crawler."""
        try:
            logger.info(f"Starting {self.store_name} catalog crawler")
            catalogs = self.get_catalog_info()
            self.update_index_file(catalogs)
            logger.info("Finished successfully")
        except Exception as e:
            logger.error(f"Error: {e}", exc_info=True) 