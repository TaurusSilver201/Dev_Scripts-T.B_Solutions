@echo off
python "get-pip.py"
pip install requests beautifulsoup4 selenium fake_useragent country_converter nltk pandas tldextract cloudscraper
pip install geopy
pip install playwright
pause