from config import COMMON
import logging
from scraper import Scraper

class Fb():
    base_domain = COMMON.get('host')

    def __init__(self) -> None:
        self.logger = logging.getLogger(__name__)


    def start_requests(self) -> None:
        event_hosts = [
            'akc.attack',
            'infamousTDKM',
            'mochvara',
            'boogaloozgb',
            'ReciKlaonica',
            #'StaraSkolaNM',
            #'masters.zagreb',
        ]
        self.logger.info("Fetching events..")
        events = Scraper().scrape_events(event_hosts)
        self.logger.info(f"Events:") 
        e = '\n'
        for host, evs in events.items():
            e += f'{host}:\n'
            for ev in evs:
                e += f'{ev}\n'
            e += '\n'
        self.logger.info(e)
