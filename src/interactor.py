from botconfigs import COMMON, WAIT_TIMEOUT, WEBDRIVER_FIREFOX_WAIT_TIMEOUT
import logging
from typing import Union, Dict
import time
from selenium.webdriver.firefox.service import Service
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException,
    StaleElementReferenceException,
)
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary

ERROR_RESPONSE_CODES = [ 
    400, 401, 403, 404, 405,
    500, 502, 503, 504, 511, 
]


def init_firefox_driver() -> webdriver.Firefox:
    service = Service()
    options = webdriver.FirefoxOptions()
    
    options.add_argument("--incognito")
    options.add_argument("--disable-extensions")
    options.add_argument('--ignore-certificate-errors')
    #options.add_argument("--headless")
    options.add_argument(f"user-agent={COMMON.get('user_agent')}")

    return webdriver.Firefox(
        firefox_binary=FirefoxBinary('/usr/bin/firefox'), 
        options=options, 
        service=service
    )


class Interactor:

    def __init__(self) -> None:
        self.host = COMMON["host"]
        self.driver = init_firefox_driver()
        self.driver.set_page_load_timeout(float(WEBDRIVER_FIREFOX_WAIT_TIMEOUT))
        self.driver.implicitly_wait(float(WEBDRIVER_FIREFOX_WAIT_TIMEOUT))
        self.logger = logging.getLogger(__name__)


    def scrape_events(
        self, 
        login_fields: Dict[str, Union[Dict[str, Union[By, str]], str]], 
        pages: Dict[str, str],
    ) -> dict:

        login_result = self.send_login_request(fields=login_fields)

        if login_result.get('exception'):
            results_login = f'Login failed - {login_result.get("exception")}'
            self.logger.error('%s -- next url: [%s]', results_login, self.driver.current_url)
            events = {}
        else:
            results_login = 'Login succeeded'
            self.logger.info('%s -- next url: [%s]', results_login, self.driver.current_url)
            events = self.follow_links(pages)
        
        self.logger.info('Closing browser.')
        self.driver.quit()

        return {
            'login': results_login,
            'events': events,
        }


    def send_login_request(self, fields: dict, attempts: int=0) -> dict:
        """
        Recursively attempt to login if failed until success or manual interrupt.
        """
        attempts += 1
        if attempts > 3:
            return { 'exception': 'Max attempts reached' }

        self.logger.info("Login attempt %d on %s", attempts, fields['login_url'])
        self.driver.get(fields['login_url'])
        
        time.sleep(10)

        try:
            # close cookies page
            WebDriverWait(driver=self.driver, timeout=float(WAIT_TIMEOUT)).until(
                EC.visibility_of_element_located(
                    (By.XPATH, "//span[text()='Decline optional cookies']")
                )
            ).click()

            # type username
            WebDriverWait(driver=self.driver, timeout=float(WAIT_TIMEOUT)).until(
                EC.visibility_of_element_located(
                    (fields['username']['locator'], fields['username']['locator_value'])
                )
            ).send_keys(fields['username']['field_value'])

            # type password
            WebDriverWait(driver=self.driver, timeout=float(WAIT_TIMEOUT)).until(
                EC.visibility_of_element_located(
                    (fields['password']['locator'], fields['password']['locator_value'])
                )
            ).send_keys(fields['password']['field_value'])

            # submit after password field is populated
            if WebDriverWait(driver=self.driver, timeout=float(WAIT_TIMEOUT)).until(
                EC.text_to_be_present_in_element_attribute(
                    locator=(fields['password']['locator'], fields['password']['locator_value']),
                    attribute_='value',
                    text_=fields['password']['field_value']
                )
            ):
                WebDriverWait(driver=self.driver, timeout=float(WAIT_TIMEOUT)).until(
                    EC.visibility_of_element_located(
                        (fields['button']['locator'], fields['button']['locator_value'])
                    )
                ).click()

            self.logger.info("Login form submitted..")

            # Wait for page to load and check current URL to verify login
            WebDriverWait(self.driver, WAIT_TIMEOUT).until(EC.url_changes(fields['login_url']))
            
            if 'login' in self.driver.current_url or 'two_step_verification' in self.driver.current_url:
                self.logger.info("Login failed")
                self.send_login_request(fields=fields, attempts=attempts)

            if '?lsrc=lb' in self.driver.current_url or 'home.php' in self.driver.current_url:
                print("Login success")

        except TimeoutException as e:
            ex = '{} raised on send_login_request() '.format(e.__class__.__name__)
            self.logger.error(ex)
            return { 'exception': ex }
            
        return {}


    def follow_links(self, pages: Dict[str, str]) -> dict:
        events = {}
        results_final = {}

        for k, p in pages.items():

            results_final[k] = []
            events['links'] = []
            events['titles'] = []

            page_event_url = f'https://facebook.com/{p}/events'
            
            self.driver.get(page_event_url)
            self.logger.info(f"Searching for events on {k} event page {page_event_url}")
            time.sleep(WAIT_TIMEOUT)

            try:
                links = self.driver.find_elements(By.XPATH, "//a[@role='link']")

                for link in links:
                    l = link.get_attribute('href')
                    if l in events['links']:
                        continue
                
                    if 'event' in l:
                        events['links'].append(l)

                        try:
                            event = link.find_element(By.XPATH, "./ancestor::div/following-sibling::div")
                        except Exception as e:
                            print(f"Exception raised for event {event}: Unable to find following <div> {e}") 
                            
                        if hasattr(event, 'text'):
                            if event.text:
                                events['titles'].append(event.text)

                for i, (link, title) in enumerate(zip(events['links'], events['titles'])):
                    if title.startswith(('Mon','Tue','Wed','Thu','Fri','Sat','Sun')):
                        results_final[k].append(f'{title.split("\n")} :: {link}')

                results_str = "\n"
                for r in results_final[k]:
                    for i, ev in enumerate(r):
                        if i < len(ev) -1:
                            results_str += f'{ev} '.rstrip('\n')
                        else:
                            results_str += f'{ev}'.rstrip('\n')
                    results_str += '\n'
                results_str += "\n"

                self.logger.info(f"Events on {k} event page:\n{results_str}") 

            except TimeoutException as e:
                ex = '{} raised on follow_links() '.format(e.__class__.__name__)
                self.logger.error(ex)
            except StaleElementReferenceException as e:
                ex = '{} raised on follow_links() '.format(e.__class__.__name__)
                self.logger.error(ex)

        return results_final