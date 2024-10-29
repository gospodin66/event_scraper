from portals.fb import Fb
from config import config, convert_time
import datetime
import logging
import time
import sys

logging.basicConfig(
    level=config['logger']['level'],
    format=config['logger']['format'],
    handlers=[
        logging.FileHandler(datetime.datetime.now().strftime('%Y-%m-%d-%H-%M') + "-events.log"),
        logging.StreamHandler(sys.stdout)
    ]
)

def main():
    logger = logging.getLogger(__name__)
    startt = time.time()
    try:
        Fb().start_requests()
    except KeyboardInterrupt:
        logger.warning("Keyboard interrupt.")
        return 1
    logger.info("Time: {}".format(convert_time(time.time() - startt)))
    return 0

if __name__ == '__main__':
    exit(main())
