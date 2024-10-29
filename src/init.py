from portals.fb import Fb
from botconfigs import config, convert_time
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
    portal = Fb
    results = []
    startt = time.time()
    p = portal()
    try:
        result = p.start_requests()
    except KeyboardInterrupt:
        logger.warning("Keyboard interrupt.")
        return 1
    test_time = time.time() - startt
    logger.info("Time: {}".format(convert_time(test_time)))
    results.append({
        'portal': p.__class__.__name__,
        'time': test_time,
        'results': result,
    })
    print(f"\nTime: {convert_time(time.time() - startt)}")
    return 0

if __name__ == '__main__':
    exit(main())
