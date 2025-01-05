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
                
                # Wait for flyers wrapper to load and find ALL wrappers
                wait = WebDriverWait(driver, 10)
                wrappers = wait.until(EC.presence_of_all_elements_located(
                    (By.CLASS_NAME, 'flyer-teaser__wrapper--grouped')))
                
                logger.info(f"Found {len(wrappers)} flyer wrapper sections")
                
                # Process all flyers from all wrappers
                for wrapper in wrappers:
                    flyers = wrapper.find_elements(By.CLASS_NAME, 'flyer-teaser__teaser')
                    logger.debug(f"Found {len(flyers)} flyers in wrapper")
                    
                    for flyer in flyers:
                        try:
                            # Only process flyers with data-region="Spar"
                            if flyer.get_attribute('data-region') != 'Spar':
                                continue
                                
                            # Get caption from within the current flyer context
                            caption_element = flyer.find_element(By.CLASS_NAME, 'flyer-teaser__caption')
                            caption = ' '.join(caption_element.get_attribute('innerHTML').split()).strip()
                            logger.debug(f"Raw caption element HTML: {caption_element.get_attribute('innerHTML')}")
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
                            validity_element = flyer.find_element(By.CLASS_NAME, 'flyer-teaser__valid')
                            validity = validity_element.get_attribute('textContent').strip()
                            logger.debug(f"Raw validity element HTML: {validity_element.get_attribute('innerHTML')}")
                            logger.debug(f"Validity text: '{validity}'")
                            
                            if not validity:
                                logger.warning("Empty validity period found, skipping flyer")
                                continue

                            # Extract dates using more robust parsing
                            # Find the date part that matches the pattern "MM.DD. - MM.DD."
                            date_match = re.search(r'(\d{2}\.\d{2}\.)\s*-\s*(\d{2}\.\d{2}\.)', validity)
                            if not date_match:
                                logger.error(f"Could not find date range in: '{validity}'")
                                continue
                                
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