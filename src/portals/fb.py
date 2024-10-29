from config import COMMON
import logging
from scraper import Scraper

class Fb():
    base_domain = COMMON.get('host')

    def __init__(self):
        self.logger = logging.getLogger(__name__)


    def start_requests(self) -> dict:
        pages = [
            'akc.attack',
            'infamousTDKM',
            'mochvara',
            'ReciKlaonica',
            'StaraSkolaNM',
            'boogaloozgb',
            'masters.zagreb',
        ]
        interactor = Scraper()
        self.logger.info("Fetching events..")
        events = interactor.scrape_events(pages)
        self.logger.info(f"Events:") 
        e = '\n'
        for host, evs in events.items():
            e += f'{host}:\n'
            for ev in evs:
                e += f'{ev}\n'
            e += '\n'
        self.logger.info(e)
        return events
