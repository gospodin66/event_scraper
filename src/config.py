from shutil import which
from common import fread, get_random_user_agent
from datetime import datetime
import logging
from pathlib import Path
from sys import stdout
from selenium.webdriver.common.by import By
import os
import io

auth_dir = Path(__file__).resolve().parent.parent / '.auth'
smtp = fread(Path(f'{auth_dir}/.smtp.txt')).split('\n')

if len(smtp) < 2:
    raise ValueError("SMTP configuration is incomplete. Need both host and user details.")

smtp_host = smtp[0].split(':') if smtp[0] else []
smtp_user = smtp[1].split(':') if smtp[1] else []

if not smtp_host or len(smtp_host) != 2:
    raise ValueError("SMTP host must be in format 'host:port'")
if not smtp_user or len(smtp_user) != 2:
    raise ValueError("SMTP user must be in format 'username:password'")

hosts_path = Path(auth_dir) / '.hosts.txt'
if not hosts_path.exists():
    raise FileNotFoundError(f"Hosts file not found: {hosts_path}")

recipients_path = Path(auth_dir) / '.recipients.txt'
if not recipients_path.exists():
    raise FileNotFoundError(f"Recipients file not found: {recipients_path}")

LOG_LEVEL = logging.INFO

# Support both Windows and Linux paths
if os.name == 'nt':
    BINARY_NAME = 'chrome.exe' if which('chrome.exe') else \
                  'firefox.exe'
    BROWSER_BINARY_PATH = which(BINARY_NAME)
    os.chdir('C:\\Program Files\\Google\\Chrome\\Application') if 'chrome.exe' in BINARY_NAME else \
    os.chdir('C:\\Program Files\\Mozilla Firefox')
else:
    BINARY_NAME = 'google-chrome' if which('google-chrome') else \
                  'chromium-browser' if which('chromium-browser') else \
                  'firefox'
    BROWSER_BINARY_PATH = which(BINARY_NAME)

WAIT_TIMEOUT = 10

COMMON = {
    'host': 'facebook.com',
    'scheme': 'https',
    'url_placeholder': '<event_host_name>',
    'user_agent': get_random_user_agent(),
}

config = {
    'encoding': 'utf-8',
    'logger': {
        'format': '%(message)s',
        'level': LOG_LEVEL,
        'log_ts': datetime.now().strftime('%Y-%m-%d-%H-%M')
    },
    'smtp': {
        'server': smtp_host[0],
        'port': smtp_host[1],
        'sender': smtp_user[0],
        'app_passkey': smtp_user[1],
        'recipients': fread(recipients_path).split('\n'),
        'mime_type': 'plain',
    },
    'hostlist': fread(hosts_path).split('\n'),
    'event_url': f'https://{COMMON["host"]}/{COMMON["url_placeholder"]}/events',
    'link_selector': (By.XPATH, "//a[@role='link']"),
    'event_selector': (By.XPATH, "./ancestor::div/following-sibling::div"),
}

log_dir = Path(__file__).resolve().parent.parent / 'logs'
log_dir.mkdir(exist_ok=True)
if not os.access(log_dir, os.W_OK):
    raise PermissionError(f"Log directory is not writable: {log_dir}")

config['logger']['log_file'] = log_dir / f"{config['logger']['log_ts']}-events.log"

logging.basicConfig(
    level=config['logger']['level'],
    format=config['logger']['format'],
    handlers=[
        logging.FileHandler(config['logger']['log_file'], encoding=config['encoding']),
        logging.StreamHandler(io.TextIOWrapper(stdout.buffer, encoding=config['encoding']))
    ]
)
