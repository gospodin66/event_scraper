from config import config, event_hosts
import datetime
import logging
import time
import sys

from scraper import Scraper

logging.basicConfig(
    level=config['logger']['level'],
    format=config['logger']['format'],
    handlers=[
        logging.FileHandler(datetime.datetime.now().strftime('%Y-%m-%d-%H-%M') + "-events.log"),
        logging.StreamHandler(sys.stdout)
    ]
)


def convert_time(seconds: float) -> str:
    if seconds >= 60:
        minutes = seconds // 60
        remaining_seconds = round(seconds % 60, 2)
        return f"{minutes} minutes and {remaining_seconds} seconds"
    else:
        return f"{seconds} seconds"
    

def main():
    logger = logging.getLogger(__name__)
    startt = time.time()
    try:
        logger.info("Fetching events..")
        events = Scraper().fetch_events(event_hosts)
        evts = '\n'
        for host, evs in events.items():
            evts += f'{host}:\n'
            for ev in evs:
                evts += f'{ev}\n'
            evts += '\n'
        logger.info(f"Events: {evts}")
    except KeyboardInterrupt:
        logger.warning("Keyboard interrupt.")
        return 1
    logger.info("Time: {}".format(convert_time(time.time() - startt)))
    return 0

if __name__ == '__main__':
    exit(main())
