from config import COMMON, WAIT_TIMEOUT, WEBDRIVER_FIREFOX_WAIT_TIMEOUT
import logging
import time
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By
from selenium.common.exceptions import (
    TimeoutException,
    StaleElementReferenceException,
)
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium import webdriver


def init_firefox_driver() -> webdriver.Firefox:
    service = Service()
    options = webdriver.FirefoxOptions()
    options.add_argument("--incognito")
    options.add_argument("--disable-extensions")
    options.add_argument('--ignore-certificate-errors')
    options.add_argument("--headless")
    options.add_argument(f"user-agent={COMMON.get('user_agent')}")
    return webdriver.Firefox(
        firefox_binary=FirefoxBinary('/usr/bin/firefox'), 
        options=options, 
        service=service
    )


class Scraper:

    def __init__(self) -> None:
        self.driver = init_firefox_driver()
        self.driver.set_page_load_timeout(float(WEBDRIVER_FIREFOX_WAIT_TIMEOUT))
        self.driver.implicitly_wait(float(WEBDRIVER_FIREFOX_WAIT_TIMEOUT))
        self.logger = logging.getLogger(__name__)


    def scrape_events(self, event_hosts: list) -> dict:
        """
        Wrapper function for following links.
        """
        return self.follow_links(event_hosts)



    def follow_links(self, event_hosts: list) -> dict:
        """
        Follows links crafted by event host name and fb events URL.
        Extracts latest events from the events page.
        """
        events = {}
        events_final = {}
        for eh in event_hosts:
            events_final[eh] = []
            events['links'] = []
            events['titles'] = []
            page_event_url = f'https://facebook.com/{eh}/events'
            self.driver.get(page_event_url)
            self.logger.info(f"Searching for events on {eh} event page {page_event_url}")
            time.sleep(WAIT_TIMEOUT)
            try:
                links = self.driver.find_elements(By.XPATH, "//a[@role='link']")
                for link in links:
                    l = link.get_attribute('href')
                    if l in events['links']:
                        continue
                    if 'event' in l:
                        try:
                            event = link.find_element(By.XPATH, "./ancestor::div/following-sibling::div")
                        except Exception as e:
                            print(f"Exception raised for event {event}: Unable to find following <div> {e}") 
                            continue
                        if hasattr(event, 'text'):
                            if event.text:
                                events['links'].append(l)
                                events['titles'].append(event.text)
                print("\n")
                for link, title in zip(events['links'], events['titles']):
                    if title.startswith(('Mon','Tue','Wed','Thu','Fri','Sat','Sun')):
                        ev = f"{title.replace('\n', ' ')} :: {link}"
                        print(ev)
                        events_final[eh].append(ev)
                print("\n")
            except TimeoutException as e:
                ex = '{} raised on follow_links() on {}'.format(e.__class__.__name__, page_event_url)
                self.logger.error(ex)
            except StaleElementReferenceException as e:
                ex = '{} raised on follow_links() on {}'.format(e.__class__.__name__, page_event_url)
                self.logger.error(ex)
        self.logger.info("Closing browser.")
        self.driver.quit()
        return events_final