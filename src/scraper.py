from datetime import datetime
from browser import BrowserFactory, BrowserType
from config import BROWSER_BINARY_PATH, COMMON, WAIT_TIMEOUT, LOGIN_ATTEMPTS, config
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
            print(f"Login page detected ({i}). Retrying...")
            self.browser.driver.get(url)
            i += 1 

        if 'login' in self.browser.driver.current_url:
            print("Login page detected after multiple attempts. Exiting...")
            return []
        
        # in headless mode, the page may not load properly, so we need to reload it
        if idx == 0 and ('--headless' in self.browser.browser_opts or '--headless=new' in self.browser.browser_opts):
            print("Headless mode detected. Reloading page.")
            self.browser.driver.get(url)

        try:
            print("Closing cookies popup.")
            WebDriverWait(self.browser.driver, WAIT_TIMEOUT).until(
                EC.element_to_be_clickable((By.XPATH, "//span[text()='Decline optional cookies']"))
            ).click()
        except Exception as e:
            print(f"Popup doesn't exist.")
        
        try:
            print("Closing login popup.")
            WebDriverWait(self.browser.driver, WAIT_TIMEOUT).until(
                EC.element_to_be_clickable((By.XPATH, "//div[contains(@aria-label, 'Close')]"))
            ).click()
        except Exception as e:
            print(f"Popup doesn't exist.")


        print("Locating event containers...")
        event_containers = self.browser.driver.find_elements(By.XPATH, "//div[.//img and .//a and .//span]")
        # exactly 14 classes in the class attribute list indicates an event container
        event_containers = [ event for event in event_containers if len(event.get_attribute('class').split()) == 14 ]
        print(f"Found {len(event_containers)} events.")

        for event in event_containers:
            link = event.find_element(By.XPATH, config['href']).get_attribute('href')
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
            for event in e:
                evts += f"{event['venue']} :: {event['where']} :: {event['when']} :: {event['link']}\n"
            
        self.logger.info(evts)

        if not dict_vals_exist(config['smtp']):
            self.logger.error("Error: SMTP is not configured.")
            return 1
        
        if SMTP().notify_email() != 0:
            self.logger.error("Error: Failed to send email notification.")
            return 1
        
        return 0


    def parse_event(self, event_text: str, link: str) -> dict:
        event_data = {}
        formatted_date = None

        lines = event_text.strip().split("\n")

        if "Happening now" in lines[0]:
            event_data["when"] = lines[0]
        else: 
            date_match = search(r"EVENT:\s+(.*)", lines[0])
            date_str = date_match.group(1) if date_match else lines[0]
            date_str = date_str.replace("\u202f", " ").replace(' at', '').strip()
            date_str_clean = sub(r"\s[A-Z]+$", "", date_str)
            try:
                formatted_date = datetime.strptime(date_str_clean, '%a, %b %d %Y %I:%M %p')\
                                         .strftime('%a, %b %d %Y, %I:%M %p')
            except ValueError:
                try:
                    # If parsing with the year fails, try without the year and assume the current year
                    formatted_date = datetime.strptime(date_str_clean, '%a, %b %d %I:%M %p')\
                                             .replace(year=datetime.now().year)\
                                             .strftime('%a, %b %d %Y, %I:%M %p')
                except ValueError as e:
                    self.logger.error(f"Date parsing error: {e}")

            event_data["when"] = formatted_date
        
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
        print(f'Script is running on {str(self.browser.browser_type).split(".")[1].lower()} browser')

        events = {}

        try:
            for i, host in enumerate(self.hosts):
                events[host] = []
                page_event_url = str(config['event_url']).replace(COMMON['url_placeholder'], host)
                self.logger.info(f"Searching for events on {host} event page {page_event_url}")
                events[host] = self.get_events(page_event_url, i)
                if not events[host]:
                    self.logger.error(f"No events found for {host}.")
                
        finally:
            self.browser.close_browser()
        return events