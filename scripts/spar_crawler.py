from datetime import datetime
import logging
from typing import List, Dict, Any
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from .base_crawler import BaseCrawler
import re

logger = logging.getLogger(__name__)

class SparCrawler(BaseCrawler):
    def __init__(self):
        super().__init__("SPAR")
        self.base_url = "https://www.spar.hu/ajanlatok"

    def get_catalog_info(self) -> List[Dict[str, Any]]:
        catalogs = []
        
        try:
            # Set up Chrome options
            chrome_options = Options()
            chrome_options.add_argument('--headless')  # Run in headless mode
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--window-size=1920,1080')
            chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')

            # Initialize the driver
            driver = webdriver.Chrome(options=chrome_options)
            
            try:
                # Visit the page
                driver.get(self.base_url)
                
                # Wait for flyers wrapper to load
                wait = WebDriverWait(driver, 10)
                wrapper = wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'flyer-teaser__wrapper')))
                
                # Find all flyers within the wrapper
                flyers = wrapper.find_elements(By.CLASS_NAME, 'flyer-teaser__teaser')
                
                for flyer in flyers:
                    try:
                        # Debug logging for caption
                        caption_element = flyer.find_element(By.CLASS_NAME, 'flyer-teaser__caption')
                        caption = ' '.join(caption_element.text.split()).strip()
                        logger.debug(f"Cleaned caption text: '{caption}'")
                        
                        if not caption:
                            logger.warning(f"Empty caption found, skipping flyer")
                            continue
                            
                        if caption != "SPAR szórólap":
                            logger.debug(f"Skipping non-SPAR szórólap: {caption}")
                            continue
                            
                        # Get store type
                        store = flyer.find_element(By.CLASS_NAME, 'flyer-teaser__teaser-type-header').text.strip()
                        
                        # Get validity period
                        validity = flyer.find_element(By.CLASS_NAME, 'flyer-teaser__valid').text.strip()
                        
                        # Extract dates using more robust parsing
                        # Find the date part that matches the pattern "MM.DD. - MM.DD."
                        date_match = re.search(r'(\d{2}\.\d{2}\.)\s*-\s*(\d{2}\.\d{2}\.)', validity)
                        if not date_match:
                            raise ValueError(f"Could not find date range in: {validity}")
                            
                        start_date, end_date = date_match.groups()
                        
                        # Convert dates to datetime
                        current_year = datetime.now().year
                        
                        # Parse start date (format: "MM.DD.")
                        start_month, start_day = map(int, start_date.strip('.').split('.'))
                        valid_from = datetime(current_year, start_month, start_day)
                        
                        # Parse end date (format: "MM.DD.")
                        end_month, end_day = map(int, end_date.strip('.').split('.'))
                        valid_to = datetime(current_year, end_month, end_day)
                        
                        # Get link and image URL
                        link_element = flyer.find_element(By.CLASS_NAME, 'flyer-teaser__teaser-inner')
                        url = link_element.get_attribute('href')
                        
                        image_element = flyer.find_element(By.CLASS_NAME, 'flyer-teaser__image')
                        image_url = image_element.get_attribute('src')
                        
                        catalog = {
                            'title': caption,
                            'url': url,
                            'image_url': image_url,
                            'valid_from': valid_from.isoformat(),
                            'valid_to': valid_to.isoformat(),
                            'last_updated': datetime.now().isoformat()
                        }
                        
                        catalogs.append(catalog)
                        
                    except Exception as e:
                        logger.error(f"Error processing flyer: {e}")
                        continue
                
                logger.info(f"Found {len(catalogs)} catalogs")
                return catalogs
                
            finally:
                driver.quit()
            
        except Exception as e:
            logger.error(f"Error fetching SPAR catalogs: {e}")
            return [] 