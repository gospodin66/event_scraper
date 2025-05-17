from common import fread, get_random_user_agent
from datetime import datetime
from io import TextIOWrapper
import logging
from os import chdir, access, W_OK
from pathlib import Path
from platform import system
from selenium.webdriver.common.by import By
from shutil import which
from sys import stdout

# set borwser for scraping (chrome|firefox)
BROWSER = 'chrome'

LOG_LEVEL = logging.INFO

# Default timeout for waiting for elements and pages to load
WAIT_TIMEOUT = 5
# Maximum number of login attempts before returning exception
LOGIN_ATTEMPTS = 3
# CLASS_NUM_INDICATOR: exactly 14 classes in the class attribute list indicates an event container
CLASS_NUM_INDICATOR = 14

COMMON = {
    'host': 'facebook.com',
    'scheme': 'https',
    'url_placeholder': '<event_host_name>',
    'user_agent': get_random_user_agent(),
}

# Windows/Linux platform compatibility for chrome/firefox
if system() == "Windows":
    if BROWSER == 'chrome':
        app_path = Path('C:\\Program Files\\Google\\Chrome\\Application')
        binary_name = Path('chrome.exe')
    elif BROWSER == 'firefox':
        app_path = Path('C:\\Program Files\\Mozilla Firefox')
        binary_name = Path('firefox.exe')
        # init geckodriver path
        geckodriver = 'X:\\Geckodriver\\geckodriver.exe'
    else:
        print("Error: Unrecognized browser.")
        exit(1)

    chdir(app_path)
    BROWSER_BINARY_PATH = f'{app_path}\\{binary_name}'

else:
    if BROWSER == 'chrome':
        binary_name = Path('google-chrome')
    elif BROWSER == 'firefox':
        binary_name = Path('firefox')
        # init geckodriver path
        geckodriver = '/usr/local/bin/geckodriver'
    else:
        print("Error: Unrecognized browser.")
        exit(1)
    
    BROWSER_BINARY_PATH = which(binary_name)

auth_dir = Path(__file__).resolve().parent.parent / '.auth'
smtp_config_path = Path(f'{auth_dir}/.smtp.txt')

hosts_path = Path(auth_dir) / '.hosts.txt'
if not hosts_path.exists():
    raise FileNotFoundError(f"Hosts file not found: {hosts_path}")

config = {
    'encoding': 'utf-8',
    'logger': {
        'format': '%(message)s',
        'level': LOG_LEVEL,
        'log_ts': datetime.now().strftime('%Y-%m-%d-%H-%M')
    },
    'hostlist': fread(hosts_path).split('\n'),
    'event_url': f'https://{COMMON["host"]}/{COMMON["url_placeholder"]}/upcoming_hosted_events',
    'cookies_popup_selector': (By.XPATH, "//span[text()='Decline optional cookies']"),
    'login_popup_selector': (By.XPATH, "//div[contains(@aria-label, 'Close')]"),
    'event_container_selector': (By.XPATH, "//div[.//img and .//a and .//span]"),
    'href_selector': (By.XPATH, ".//a[@href]"),
}

if smtp_config_path.exists():

    recipients_path = Path(auth_dir) / '.recipients.txt'
    if not recipients_path.exists():
        raise FileNotFoundError(f"Recipients file not found: {recipients_path}")

    smtp = fread(smtp_config_path).split('\n')

    if len(smtp) < 2:
        raise ValueError("SMTP configuration is incomplete. Need both host and user details.")

    smtp_host = smtp[0].split(':') if smtp[0] else []
    smtp_user = smtp[1].split(':') if smtp[1] else []

    if not smtp_host or len(smtp_host) != 2:
        raise ValueError("SMTP host must be in format 'host:port'")
    if not smtp_user or len(smtp_user) != 2:
        raise ValueError("SMTP user must be in format 'username:password'")

    config['smtp'] = {
        'server': smtp_host[0],
        'port': smtp_host[1],
        'sender': smtp_user[0],
        'app_passkey': smtp_user[1],
        'recipients': fread(recipients_path).split('\n'),
        'mime_type': 'plain',
    }
else: 
    config['smtp'] = {}

log_dir = Path(__file__).resolve().parent.parent / 'logs'
log_dir.mkdir(exist_ok=True)
if not access(log_dir, W_OK):
    raise PermissionError(f"Log directory is not writable: {log_dir}")

config['logger']['log_file'] = log_dir / f"{config['logger']['log_ts']}-events.log"

logging.basicConfig(
    level=config['logger']['level'],
    format=config['logger']['format'],
    handlers=[
        logging.FileHandler(config['logger']['log_file'], encoding=config['encoding']),
        logging.StreamHandler(TextIOWrapper(stdout.buffer, encoding=config['encoding']))
    ]
)
