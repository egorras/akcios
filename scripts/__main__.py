from .aldi_crawler import AldiCrawler
from .lidl_crawler import LidlCrawler
from .generate_index import generate_html
import logging

logger = logging.getLogger(__name__)

def main():
    try:
        # Run crawlers
        logger.info("Starting crawlers...")
        
        aldi_crawler = AldiCrawler()
        aldi_crawler.run()
        
        lidl_crawler = LidlCrawler()
        lidl_crawler.run()
        
        # Generate index page
        logger.info("Generating index page...")
        generate_html()
        
        logger.info("All tasks completed successfully")
        
    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)

if __name__ == "__main__":
    main() 