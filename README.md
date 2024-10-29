## Python event scraper

Script is navigating fb event pages for event hosts specified in `portals/fb.py` file. User can specify which event hosts the bot needs to crawl by updating variable `pages` which consists of `key: val` where key is arbitrary name of the event host and val is event host name in fb URL. This implementation uses `Firefox` driver.

### Configuration
To be able to use the scripts, user needs to have `python3` installed on the system.

**Linux**\
If python3 is not installed, install it via package manager:
```bash
# Install python3 depending on distribution
# Fedora, CentOS, RHEL
yum update && yum install python3
# Ubuntu, Debian
apt update && apt install python3 

# Verify that python is installed
$ python --version
Python 3.12.6
```

**Windows**\
Download and install python3 for Windows platforms from [official python website](https://www.python.org/downloads/windows). \
Once installed, open powershell and verify if `python3` is installed:
```powershell
> python --version
Python 3.11.9  
```

Once `python3` is installed, it should automatically install `pip` which is python's package manager.
Verify that pip is installed:
```bash
pip --version
```

Scraper bot is based upon `selenium` library which is used for automatic and headless borwsing.
To install selenium library, run next command:
```bash
pip install selenium
```

### Runtime
Open any terminal, navigate to directory where event_scraper is downloaded and execute the script: 
```bash
cd event_scraper/src
python init.py
```
