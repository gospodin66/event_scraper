from selenium.webdriver.common.by import By
from botconfigs import COMMON, FB
from interactor import Interactor

import logging

class Fb():
    base_domain = COMMON.get('host')
    start_url = FB.get('start_url', '')
    authenticated_url = FB.get('authenticated_url', '')


    def __init__(self):
        self.user = FB['login']['username']
        self.login_username = FB['login']['username']
        self.login_password = FB['login']['password']
        self.logger = logging.getLogger(__name__)


    def start_requests(self) -> dict:
        login_fields = {
            'username': {
                'locator': By.XPATH,
                'locator_value': '//input[@name="email"]',
                'field_value': self.login_username,
            },
            'password': {
                'locator': By.XPATH,
                'locator_value': '//input[@name="pass"]',
                'field_value': self.login_password,
            },
            'button': {
                'locator': By.XPATH,
                'locator_value': '//button[@type="submit"]',
            },
            'login_url': self.start_url,
            'homepage': self.authenticated_url,
        }

        pages = {
            'TDK': 'infamousTDKM',
            'Attack': 'akc.attack',
            'Klaonica': 'ReciKlaonica',
            'Mocvara': 'mochvara',
            "Stara Skola": 'StaraSkolaNM',
            'Boogaloo': 'boogaloozgb',
            'Masters': 'masters.zagreb',
        }

        interactor = Interactor()
        events = interactor.scrape_events(login_fields, pages)

        return events
