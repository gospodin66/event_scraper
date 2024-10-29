import logging
from scraper import Scraper
from config import event_hosts

class Fb():

    def __init__(self) -> None:
        self.logger = logging.getLogger(__name__)


    def start_requests(self) -> dict:
        self.logger.info("Fetching events..")
        return Scraper().scrape_events(event_hosts)
