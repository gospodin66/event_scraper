from common import convert_time
import logging
import time
from scraper import Scraper

def main():
    logger = logging.getLogger(__name__)
    start = time.time()
    s = Scraper()

    try:
        if s.print_and_notify_on_events(s.run_program()) != 0:
            logger.error("Error fetching events or sending email notification.")
            return 1
    except KeyboardInterrupt:
        logger.warning("Keyboard interrupt.")
        return 1

    logger.info(f"Time: {convert_time(time.time() - start)}")
    return 0

if __name__ == '__main__':
    exit(main())