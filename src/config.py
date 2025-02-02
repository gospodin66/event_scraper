from common import fread, get_random_user_agent
from datetime import datetime
import logging
from pathlib import Path
from sys import stdout
from selenium.webdriver.common.by import By

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
BINARY_NAME = 'google-chrome'
BROWSER_BINARY_PATH = f'/usr/bin/{BINARY_NAME}'
WAIT_TIMEOUT = 15

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

config['logger']['log_file'] = Path(f"{config['logger']['log_ts']}-events.log")

logging.basicConfig(
    level=config['logger']['level'],
    format=config['logger']['format'],
    handlers=[
        logging.FileHandler(config['logger']['log_file']),
        logging.StreamHandler(stdout)
    ]
)