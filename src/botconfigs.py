import logging
from pathlib import Path


def f_read(fpath: Path) -> str:
    data = ""
    if not fpath.exists():
        return data
    with open(fpath, 'r') as f:
        data = f.read()
    return data


def convert_time(seconds: float) -> str:
    if seconds >= 60:
        minutes = seconds // 60
        remaining_seconds = round(seconds % 60, 2)
        return f"{minutes} minutes and {remaining_seconds} seconds"
    else:
        return f"{seconds} seconds"
    

# Timeout that WebDriverWait waits for DOM element to be visible on page before it raises exception
WAIT_TIMEOUT = 20

# Timeout that webdriver.Firefox waits for page to load and or as implicit wait for DOM element to be visible
WEBDRIVER_FIREFOX_WAIT_TIMEOUT = 20

config = {
    'logger': {
        'format': '[%(asctime)s][%(levelname)s][%(name)s]: %(message)s',
        'level': logging.INFO
    },
}

COMMON = {
    'host': 'facebook.com',
    'proxy': '',
    'scheme': 'https',
    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36',
}
