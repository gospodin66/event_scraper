from common import convert_time
from logging import getLogger
from time import time
from scraper import Scraper
from subprocess import run as subprocess_run, SubprocessError
from platform import system

logger = getLogger(__name__)

def is_behind_vpn() -> bool:
    """
    Check if the user is behind a VPN by checking if gateway IP address is assigned. 
    If the gateway IP address is assigned, the user is behind a VPN. 
    Otherwise, the user is not behind a VPN. Supported on Windows OS only.
    """
    try:
        if system() == "Windows":
            result = subprocess_run(['ipconfig'], capture_output=True, text=True)
            lines = result.stdout.splitlines()

            for i, line in enumerate(lines):
                if "NordLynx" in line:
                    vpn_info = lines[i:i+7]
                    break

            if not vpn_info:
                logger.error("VPN interface not found")
                return False
                
            gateway = vpn_info[-1].strip().split(':')[-1].strip()
            return True if gateway else False
        
        else:
            logger.warning("Linux OS VPN check not supported - skipping")
            return True

    except SubprocessError as e:
        logger.error(f"Error checking VPN status: {e}")
        return False

def main():
    start = time()

    if not is_behind_vpn():
        logger.error("Error: Not behind a VPN. Please connect to a VPN and try again.")
        return 1

    s = Scraper()

    try:
        if s.print_and_notify_on_events(s.run_program()) != 0:
            logger.error("Error fetching events or sending email notification.")
            return 1
    except KeyboardInterrupt:
        logger.warning("Keyboard interrupt.")
        return 1

    logger.info(f"Time: {convert_time(time() - start)}")
    return 0

if __name__ == '__main__':
    exit(main())