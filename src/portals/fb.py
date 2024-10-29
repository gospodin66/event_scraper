from botconfigs import COMMON
import logging
from interactor import Interactor

class Fb():
    base_domain = COMMON.get('host')

    def __init__(self):
        self.logger = logging.getLogger(__name__)


    def start_requests(self) -> dict:
        pages = {
            'Attack': 'akc.attack',
            'TDK': 'infamousTDKM',
            'Mocvara': 'mochvara',
            'Klaonica': 'ReciKlaonica',
            "Stara Skola": 'StaraSkolaNM',
            'Boogaloo': 'boogaloozgb',
            'Masters': 'masters.zagreb',
        }

        interactor = Interactor()
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
