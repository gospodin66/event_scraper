## Python event scraper

Script is navigating events pages for `event_hosts` specified in `portals/fb.py` file. User controls wtich events is bot fetching by updating `event_hosts` list which consists of event host names that are used in fb URL (user can get it by manually navigating to event host's page on fb and copying the name from URL). 

**Notice**: This implementation uses `Firefox` driver.

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

# Verify that python3 is installed
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
