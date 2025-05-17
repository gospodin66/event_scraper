from datetime import datetime
from browser import BrowserFactory, BrowserType
from config import BROWSER_BINARY_PATH, COMMON, WAIT_TIMEOUT, LOGIN_ATTEMPTS, CLASS_NUM_INDICATOR, config
from common import dict_vals_exist
from logging import getLogger
from os import path
from re import search, sub
from smtp import SMTP
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def get_event_hostlist() -> list:
    return [eh for eh in config['hostlist'] if eh and not str(eh).startswith(('#', '\n'))]


class Scraper():

    def __init__(self):
        self.logger = getLogger(__name__)
        self.browser = BrowserFactory.create_browser(
            BrowserType.FIREFOX if 'firefox' in BROWSER_BINARY_PATH else BrowserType.CHROME
        )
        
        if not path.exists(BROWSER_BINARY_PATH):
            raise FileNotFoundError(f"Error: {BROWSER_BINARY_PATH} binary not found.")

        self.hosts = get_event_hostlist()
        if not self.hosts:
            raise ValueError("No hosts found. Please check your configuration.")


    def get_events(self, url: str, idx: int) -> list:
        """
        Scrape events from the given URL.
        """
        event_list = []
        self.browser.driver.get(url)
        i = 0
        while i < LOGIN_ATTEMPTS and 'login' in self.browser.driver.current_url:
            self.logger.debug(f"Login page detected ({i}). Retrying...")
            self.browser.driver.get(url)
            WebDriverWait(self.browser.driver, WAIT_TIMEOUT).until(
                lambda driver: driver.execute_script("return document.readyState") == "complete"
            )
            i += 1 

        if 'login' in self.browser.driver.current_url:
            self.logger.error("Login page detected after multiple attempts. Exiting...")
            return []
        
        # in headless mode, the page may not load properly, so we need to reload it
        if idx == 0 and ('--headless' in self.browser.browser_opts or '--headless=new' in self.browser.browser_opts):
            self.logger.debug("Headless mode detected. Reloading page.")
            self.browser.driver.get(url)

        try:
            self.logger.debug("Closing cookies popup.")
            WebDriverWait(self.browser.driver, WAIT_TIMEOUT).until(
                EC.element_to_be_clickable((
                    config['cookies_popup_selector'][0], config['cookies_popup_selector'][1]
                ))
            ).click()
        except Exception as e:
            self.logger.debug(f"Popup doesn't exist.")
        
        try:
            self.logger.debug("Closing login popup.")
            WebDriverWait(self.browser.driver, WAIT_TIMEOUT).until(
                EC.element_to_be_clickable((
                    config['login_popup_selector'][0], config['login_popup_selector'][1]
                ))
            ).click()
        except Exception as e:
            self.logger.debug(f"Popup doesn't exist.")


        self.logger.debug("Locating event containers...")
        event_containers = self.browser.driver.find_elements(
            config['event_container_selector'][0],
            config['event_container_selector'][1]
        )
        # classes_indicator_num: exactly 14 classes in the class attribute list indicates an event container
        event_containers = [ event for event in event_containers if len(event.get_attribute('class').split()) == CLASS_NUM_INDICATOR ]
        self.logger.debug(f"Found {len(event_containers)} events.")

        for event in event_containers:
            link = event.find_element(config['href_selector'][0], config['href_selector'][1]).get_attribute('href')
            evt = self.parse_event(event.text, link)
            event_list.append(evt)
            
        return event_list


    def print_and_notify_on_events(self, events: dict) -> int:
        
        if len(events.items()) < 1:
            self.logger.error("Error: No events found - skipping sending email notification.")
            return 1

        evts = ''
        for k, e in events.items():
            evts += f"\n{k}:\n"
            if not e:
                evts += "No events found.\n"
                continue
            for event in e:
                evts += f"{event['venue']} :: {event['where']} :: {event['when']} :: {event['link']}\n"

        # write results to terminal and log file
        self.logger.info(evts)

        if not config['smtp']:
            print("SMTP not configured - skipping...")
            return 0
        
        if not dict_vals_exist(config['smtp']):
            self.logger.error("Error: SMTP is not configured.")
            return 1
        
        if SMTP().notify_email() != 0:
            self.logger.error("Error: Failed to send email notification.")
            return 1

        return 0


    def detect_date_format(self, date_string: str):
        formats = [
            # Basic numeric formats
            "%Y-%m-%d",
            "%d-%m-%Y",
            "%m-%d-%Y",
            "%Y/%m/%d",
            "%d/%m/%Y",
            "%m/%d/%Y",
            "%Y.%m.%d",
            "%d.%m.%Y",
            "%m.%d.%Y",
            # Extended formats with time
            "%Y-%m-%d %H:%M:%S",
            "%d-%m-%Y %H:%M:%S",
            "%m-%d-%Y %H:%M:%S",
            "%Y/%m/%d %H:%M:%S",
            "%d/%m/%Y %H:%M:%S",
            "%m/%d/%Y %H:%M:%S",
            "%Y.%m.%d %H:%M:%S",
            "%d.%m.%Y %H:%M:%S",
            "%m.%d.%Y %H:%M:%S",
            # Shortened year formats
            "%y-%m-%d",
            "%d-%m-%y",
            "%m-%d-%y",
            "%y/%m/%d",
            "%d/%m/%y",
            "%m/%d/%y",
            "%y.%m.%d",
            "%d.%m.%y",
            "%m.%d.%y",
            # Month names
            "%B %d, %Y",
            "%b %d, %Y",
            "%d %B %Y",
            "%d %b %Y",
            "%B %d, %y",
            "%b %d, %y",
            "%d %B %y",
            "%d %b %y",
            # Mixed separators
            "%Y %b %d",
            "%Y %B %d",
            "%d %b %Y",
            "%d %B %Y",
            # Special formats
            "%d %B, %Y",
            "%d %b, %Y",
            "%B %dth, %Y",
            "%d-%b-%Y",
            "%d-%B-%Y",
            "%b-%d-%Y",
            "%B-%d-%Y",
            # ISO formats
            "%Y-%m-%dT%H:%M:%SZ",
            "%Y-%m-%dT%H:%M:%S.%fZ",
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%dT%H:%M:%S.%f",
            # Day/Month names
            "%A, %d %B %Y",
            "%a, %d %b %Y",
            "%A, %B %d, %Y",
            "%a, %b %d, %Y",
            # New formats for missing cases
            "%a, %d %b %H:%M",
            "%A, %d %B %H:%M",
            "%a, %b %d %H:%M",
            "%A, %B %d %H:%M",
            "%d %B %H:%M",
            "%d %b %H:%M",
            "%B %d %H:%M",
            "%b %d %H:%M",
            "%d-%b %H:%M",
            "%d-%B %H:%M",
            "%b-%d %H:%M",
            "%B-%d %H:%M",
            "%d/%b %H:%M",
            "%d/%B %H:%M",
            "%b/%d %H:%M",
            "%B/%d %H:%M",
            "%d.%b %H:%M",
            "%d.%B %H:%M",
            "%b.%d %H:%M",
            "%B.%d %H:%M",
            # Full date with time and weekday
            "%a, %b %d %I:%M %p",
            "%A, %B %d %I:%M %p",
            # Custom
            '%a, %b %d %Y',
            '%a, %b %d %Y, %I:%M %p',
        ]

        # Handle date ranges like 'Fri, 23 May-24 May' or 'Mon, May 26 - Jun 1'
        if '-' in date_string:
            # Take only the first part of the range for parsing
            start = date_string.split('-')[0].strip()
            try:
                # Detect format for the start date only
                print(start)
                return self.detect_date_format(start)
            except ValueError:
                pass
        
        # Fallback to regular formats
        for fmt in formats:
            try:
                parsed_date = datetime.strptime(date_string, fmt)
                return fmt
            except ValueError:
                continue
        
        return None


    def parse_event(self, event_text: str, link: str) -> dict:
        event_data = {}
        lines = event_text.strip().split("\n")

        if "Happening now" in lines[0]:
            event_data["when"] = lines[0]
        else: 
            date_match = search(r"EVENT:\s+(.*)", lines[0])
            date_str = date_match.group(1) if date_match else lines[0]
            date_str = date_str.replace("\u202f", " ").replace(' at', '').strip()
            date_str_clean = sub(r"\s[A-Z]+$", "", date_str)
            try:
                if '-' in date_str_clean:
                    date_str_clean = f'{date_str_clean.split('-')[0].strip()} {datetime.now().year}'
                    fmt = self.detect_date_format(date_str_clean)
                    parsed_date = datetime.strptime(f'{date_str_clean}', self.detect_date_format(date_str_clean))
                else:
                    parsed_date = datetime.strptime(date_str_clean, self.detect_date_format(date_str_clean))
                    fmt = self.detect_date_format(date_str_clean)

                if parsed_date.year != datetime.now().year:
                    parsed_date = parsed_date.replace(year=datetime.now().year)

                event_data["when"] = parsed_date.strftime(fmt)

            except Exception as e:
                print(f"Error: Failed to parse date: {date_str_clean}: {e}")
                event_data["when"] = ""

        event_data["venue"] = lines[1] if len(lines) > 1 else "Unknown"
        venue_lines = [line.replace('  · ', '').strip() for line in lines if " · " in line]
        event_data["where"] = venue_lines[0] if venue_lines else "Unknown"
        organizer_match = search(r"Event by (.*)", event_text)
        event_data["event_by"] = organizer_match.group(1) if organizer_match else "Unknown"
        event_data["link"] = link
        
        return event_data


    def run_program(self) -> dict:
        """
        Wrapper for scrape_events() to ensure browser is Closingd after program execution.
        """
        self.logger.debug(f'Script is running on {str(self.browser.browser_type).split(".")[1].lower()} browser')

        events = {}

        try:
            for i, host in enumerate(self.hosts):
                events[host] = []
                page_event_url = str(config['event_url']).replace(COMMON['url_placeholder'], host)
                self.logger.debug(f"Searching for events on {host} event page {page_event_url}")
                events[host] = self.get_events(page_event_url, i)
                if not events[host]:
                    self.logger.debug(f"No events found for {host}.")
                
        finally:
            self.browser.close_browser()
        return events