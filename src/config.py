import logging
    
BROWSER_BINARY_PATH = '/usr/bin/firefox'
WAIT_TIMEOUT = 15

config = {
    'logger': {
        'format': '[%(asctime)s][%(levelname)s][%(name)s]: %(message)s',
        'level': logging.INFO
    },
}

COMMON = {
    'host': 'facebook.com',
    'scheme': 'https',
    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36',
}

event_hosts = [
    'akc.attack',
    'infamousTDKM',
    'mochvara',
    'boogaloozgb',
    'ReciKlaonica',
    #'StaraSkolaNM',
    #'masters.zagreb',
]
