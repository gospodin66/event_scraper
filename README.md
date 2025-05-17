## Python event scraper

Script is navigating events pages for `event_hosts` specified in `config.py` file. User controls wtich event pages is bot fetching by updating `event_hosts` list which consists of event host names that are used in fb URL (user can get it by manually navigating to event host's page on fb and copying the name from URL). 

**Notice**: This implementation is compatible `Firefox` and `Chrome` drivers and Windows and Linux platforms.

### Configuration
To be able to use the scripts, user needs to have `python3` and Google Chrome or Mozilla Firefox browser installed on the system.

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
pip install selenium webdriver-manager
```

Create ./auth dir and config files (each line represents entity separated by newline `\n`)
```bash
vi .hosts.txt
# add hosts slugs (fetched from URL)

#
# (Optional) If using SMTP
#
vi .recipients
# add recipients emails  
vi .smtp.txt
# Add SMTP server (smtp.gmail.com:587)
# Add SMTP user (<email>:<app_key>)
```

Set browser constant in `config.py` (possible values: `firefox` | `chrome`):
```bash
vi config.py
BROWSER='chrome'
```

To be able to run in firefox browser, selenium module requires geckodriver to be installed on the system and referenced in Browser class:
```powershell
# download and unzip geckodriver from official mozilla repository:
curl -v -L -o geckodriver-v0.36.0-win64.zip https://github.com/mozilla/geckodriver/releases/download/v0.36.0/geckodriver-v0.36.0-win64.zip
# unzip geckodriver to prefered path
mkdir X:\Geckodriver
"X:\7-Zip\7z.exe" x geckodriver-v0.36.0-win64.zip -o"%cd%\Geckodriver"
# set geckodriver parent dir to PATH
set PATH=%PATH%X:\Geckodriver
```

### Runtime
Open any terminal, navigate to directory where event_scraper is downloaded and execute the script: 
```bash
cd event_scraper/src
python init.py
```
