from abc import ABC, abstractmethod
from config import BINARY_NAME, BROWSER_BINARY_PATH, COMMON, WAIT_TIMEOUT
import logging
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
import shutil
from enum import Enum

class BrowserType(Enum):
    CHROME = "chrome"
    FIREFOX = "firefox"

class Browser(ABC):
    def __init__(self, browser_type: BrowserType) -> None:
        self.logger = logging.getLogger(__name__)
        self.browser_type = browser_type
        self.driver = self.init_driver()
        if self.driver:
            self.driver.set_page_load_timeout(float(WAIT_TIMEOUT))
            self.driver.implicitly_wait(float(WAIT_TIMEOUT))

    def is_browser_installed(self) -> bool:
        try:
            return bool(shutil.which(BINARY_NAME))
        except Exception as e:
            self.logger.error(f"Unknown exception raised: {e.args[::-1]}")
            return False

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
    def __init__(self):
        super().__init__(BrowserType.CHROME)

    def init_driver(self) -> webdriver.Chrome:
        if not self.is_browser_installed():
            self.logger.error(f'Error: {BINARY_NAME} binary not found.')
            return None

        return webdriver.Chrome(
            options=self.init_options(),
            service=ChromeService(),
        )

    def init_options(self) -> webdriver.ChromeOptions:
        options = webdriver.ChromeOptions()
        options.add_argument("--incognito")
        options.add_argument("--disable-extensions")
        options.add_argument('--ignore-certificate-errors')
        options.add_argument(f"user-agent={COMMON.get('user_agent')}")
        options.add_argument("--headless=new")
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        return options


class FirefoxBrowser(Browser):
    def __init__(self):
        super().__init__(BrowserType.FIREFOX)

    def init_driver(self) -> webdriver.Firefox:
        if not self.is_browser_installed():
            self.logger.error(f'Error: {BINARY_NAME} binary not found.')
            return None

        return webdriver.Firefox(
            options=self.init_options(),
            service=FirefoxService(),
        )

    def init_options(self) -> webdriver.FirefoxOptions:
        options = webdriver.FirefoxOptions()
        options.add_argument("--incognito")
        options.add_argument("--disable-extensions")
        options.add_argument('--ignore-certificate-errors')
        options.add_argument("--headless")
        options.add_argument(f"user-agent={COMMON.get('user_agent')}")
        return options


# Factory to create browser instances
class BrowserFactory:
    @staticmethod
    def create_browser(browser_type: BrowserType) -> Browser:
        if browser_type == BrowserType.CHROME:
            return ChromeBrowser()
        elif browser_type == BrowserType.FIREFOX:
            return FirefoxBrowser()
        else:
            raise ValueError(f"Unsupported browser type: {browser_type}")