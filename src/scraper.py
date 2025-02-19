from browser import (BrowserFactory, BrowserType)
from config import BROWSER_BINARY_PATH, COMMON, config, WAIT_TIMEOUT
from common import dict_vals_exist
from logging import getLogger
from selenium.common.exceptions import (TimeoutException, StaleElementReferenceException, WebDriverException)
import sys
from time import sleep
from smtp import SMTP
import os  # Add this import

class Scraper():

    def __init__(self):
        self.logger = getLogger(__name__)
        browser = BrowserType.FIREFOX if 'firefox' in BROWSER_BINARY_PATH else BrowserType.CHROME
        self.browser = BrowserFactory.create_browser(browser)
        
        # Check if the browser binary exists
        if not os.path.exists(BROWSER_BINARY_PATH):
            raise FileNotFoundError(f"Error: {BROWSER_BINARY_PATH} binary not found.")
        
        self.hosts = self.get_event_hostlist()
        if not self.hosts:
            raise ValueError("No hosts found. Please check your configuration.")
        self.progbar_width = 50
        self.progbar_step = round(self.progbar_width / len(self.hosts))



    def get_event_hostlist(self) -> list:
        return [eh for eh in config['hostlist'] if eh and not str(eh).startswith(('#', '\n'))]
    

    def print_and_notify_on_events(self, events: dict) -> int:
        evts = '\n'
        for host, evs in events.items():
            if len(evs) > 0:
                evts += f'{host}:\n'
                for ev in evs:
                    evts += f'{ev}\n'
                evts += '\n'

        self.logger.info(evts)

        if not dict_vals_exist(config['smtp']):
            self.logger.error("Error: SMTP is not configured.")
            return 1
        
        _smtp = SMTP()
        if _smtp.notify_email() != 0:
            self.logger.error("Error: Failed to send email notification.")
            return 1
        
        return 0


    def spawn_progbar(self):
        # '0.00%' has 5 characters
        percentage_offset = 5
        sys.stdout.write("\n0.00%{}".format(" " * (self.progbar_width - percentage_offset)))
        # return to start of line
        sys.stdout.write("\b" * (self.progbar_width +1)) 
        sys.stdout.flush()


    def update_progbar(self, cycle: int):
        percentage = (cycle / len(self.hosts)) * 100
        # '100.00%' has 7 characters
        percentage_offset = 6 if cycle < len(self.hosts) else 7
        sys.stdout.write(f'\r{str("=" * (self.progbar_step * cycle - percentage_offset))}{percentage:.2f}%')
        sys.stdout.flush()
        

    def run_program(self) -> dict:
        """
        Wrapper for fetch_events() to ensure browser is closed after program execution.
        """
        print(f'Script is running on {str(self.browser.browser_type).split(".")[1].lower()} browser')
        try:
            events = self.fetch_events()
        finally:
            self.browser.close_browser()
        return events


    def fetch_events(self) -> dict:
        """
        Follows links crafted by event host name and fb events URL.
        Extracts latest events from the events page.
        """
        events = {}
        self.spawn_progbar()

        for i, host in enumerate(self.hosts):
            events[host] = []
            page_event_url = str(config['event_url']).replace(COMMON['url_placeholder'], host)

            try:
                self.browser.driver.get(page_event_url)
            except TimeoutException as e:
                self.logger.error(f'{e.__class__.__name__} exception raised: {page_event_url}: {e.args[::-1]}')
                continue
            #except Exception as e:
            #    self.logger.error(f'Unknown exception raised: {page_event_url}: {e.args[::-1]}')
            #    continue

            self.logger.debug(f"Searching for events on {host} event page {page_event_url}")
            sleep(WAIT_TIMEOUT)

            try:
                for link in self.browser.driver.find_elements(
                    by=config['link_selector'][0],
                    value=config['link_selector'][1]
                ):
                    href = link.get_attribute('href')
                    if href in events[host]:
                        continue

                    if 'event' in href:
                        event = link.find_element(
                            by=config['event_selector'][0],
                            value=config['event_selector'][1]
                        )
                        if hasattr(event, 'text') and event.text != '':
                            title = event.text.replace('  · ', '').strip()

                            if title.startswith(('Mon','Tue','Wed','Thu','Fri','Sat','Sun')):
                                events[host].append(f"{title.replace('\n', ' ')} :: {href}")

                self.update_progbar(i+1)

            except (TimeoutException, StaleElementReferenceException, WebDriverException) as e:
                self.logger.error(f'{e.__class__.__name__} exception raised: Failed to fetch events for {page_event_url}: {e.args[::-1]}')
            except Exception as e:
                self.logger.error(f"Unknown exception raised: Unable to find html element: {e.args[::-1]}") 
        
        sys.stdout.write('\n')
        sys.stdout.flush()

        return events
        

    def fetch_events_details(self):
        pass