from abc import ABC, abstractmethod
from platform import system
from config import binary_name, COMMON
from logging import getLogger, DEBUG 
from selenium.webdriver import FirefoxOptions, ChromeOptions, Firefox, Chrome
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
from shutil import which
from enum import Enum
from selenium.common.exceptions import TimeoutException
from subprocess import STDOUT

class BrowserType(Enum):
    CHROME = "chrome"
    FIREFOX = "firefox"

class Browser(ABC):
    def __init__(self, browser_type: BrowserType) -> None:
        self.logger = getLogger(__name__)
        self.logger.level = DEBUG
        self.browser_opts = [
            '--incognito',
            '--ignore-certificate-errors',
            '--headless' if browser_type == BrowserType.FIREFOX else \
            '--headless=new' if browser_type == BrowserType.CHROME else '',
            "--no-sandbox",
            "--disable-extensions",
            "--disable-dev-shm-usage",
            "--disable-setuid-sandbox",
            "--disable-gpu",
            '--enable-unsafe-swiftshader',
            f"user-agent={COMMON.get('user_agent')}",
        ]
        self.browser_type = browser_type
        self.driver = self.init_driver()


    def detect_browser(self) -> str:
        try:
            return which(binary_name)
        except Exception as e:
            self.logger.error(f"Unknown exception raised: {e.args[::-1]}")
            return ''


    @abstractmethod
    def init_driver(self):
        pass

    @abstractmethod
    def init_options(self):
        pass

    def close_browser(self):
        if self.driver:
            self.driver.quit()
            

class ChromeBrowser(Browser):
    """
    install chromedriver (used as a bridge between selenium and chrome)
    # apt install google-chrome chromium-chromedriver
    
    $ pip3 install selenium
    $ pip3 install webdriver-manager
    """
    def __init__(self):
        super().__init__(BrowserType.CHROME)

    def init_driver(self) -> Chrome:
        if not self.detect_browser():
            self.logger.error(f'Error: {binary_name} binary not found.')
            return None
        
        try:
            return Chrome(self.init_options(), ChromeService())
        except TimeoutException as e:
            self.logger.error(f'TimeoutException: {e}')
            return None

    def init_options(self) -> ChromeOptions:
        options = ChromeOptions()
        for o in self.browser_opts:
            options.add_argument(o)
        return options


class FirefoxBrowser(Browser):
    
    def __init__(self):
        super().__init__(BrowserType.FIREFOX)

    def init_driver(self) -> Firefox:
        from config import geckodriver

        if not self.detect_browser():
            self.logger.error(f'Error: {binary_name} binary not found.')
            return None

        try:
            return Firefox(self.init_options(), FirefoxService(executable_path=geckodriver, log_output=STDOUT))
        except TimeoutException as e:
            self.logger.error(f'TimeoutException: {e}')
            return None

    def init_options(self) -> FirefoxOptions:
        options = FirefoxOptions()
        options.binary_location = which(binary_name)
        for o in self.browser_opts:
            options.add_argument(o)
        return options


class BrowserFactory:
    @staticmethod
    def create_browser(browser_type: BrowserType) -> Browser:
        if browser_type == BrowserType.CHROME:
            return ChromeBrowser()
        elif browser_type == BrowserType.FIREFOX:
            return FirefoxBrowser()
        else:
            raise ValueError(f"Unsupported browser type: {browser_type}")
