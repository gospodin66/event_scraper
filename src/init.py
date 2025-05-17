from common import convert_time
from logging import getLogger
from time import time
from scraper import Scraper
from subprocess import run as subprocess_run, SubprocessError
from platform import system

logger = getLogger(__name__)

def main():
    start = time()
    s = Scraper()
    
    try:
        s.print_and_notify_on_events(s.run_program())
    except KeyboardInterrupt:
        logger.warning("Keyboard interrupt.")
        return 1

    logger.info(f"Time: {convert_time(time() - start)}")
    return 0

if __name__ == '__main__':
    exit(main())
