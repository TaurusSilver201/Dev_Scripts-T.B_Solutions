import requests
import json
import random
import csv
import re
from datetime import datetime
from bs4 import BeautifulSoup
import config
import utils
from concurrent.futures import ThreadPoolExecutor
import pandas as pd
from tenacity import retry
from collections import defaultdict
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException
from fake_useragent import UserAgent
import time
session = requests.Session()
delay_range = config.delay_range
proxies = utils.get_proxies()
threads = config.threads  # Number of threads for ThreadPoolExecutor
full_report = config.full_report
max_retries = config.max_retries
skip_file = config.skip_file
max_bid = config.max_bid
retries = defaultdict(int)
headers_list = [
    {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:86.0) Gecko/20100101 Firefox/86.0',
     'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
     'Accept-Language': 'en-US,en;q=0.5',
     'Connection': 'keep-alive',
     'Upgrade-Insecure-Requests': '1',
     'Cache-Control': 'max-age=0'},
    {'sec-ch-ua': '"Google Chrome";v="89", "Chromium";v="89", ";Not A Brand";v="99"',
     'sec-ch-ua-mobile': '?0',
     'upgrade-insecure-requests': '1',
     'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) '
                   'Chrome/89.0.4389.82 Safari/537.36',
     'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,'
               'image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
     'sec-fetch-site': 'none',
     'sec-fetch-mode': 'navigate',
     'sec-fetch-user': '?1',
     'sec-fetch-dest': 'document',
     'accept-language': 'en-US,en;q=0.9'},
    {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36',
     'Accept-Encoding': 'gzip, deflate',
     'Accept': '*/*',
     'Connection': 'keep-alive'}
]

def generating_data(searched_word):
    print(f'Keywords = {searched_word} Retry: {retries[searched_word]} \n')

    if retries[searched_word] >= max_retries:
        print("Max no of retries reached for ", searched_word)
        return None

    retries[searched_word] += 1
    proxy = {"http": proxies[(random.randrange(len(proxies)))]}
    headers = headers_list[(random.randrange(len(headers_list)))]

    source = ''
    bidders = ''
    current_bid = ''
    current_bid_int = 0
    notes = ''
    active_auction = False
    inventoryType = ""
    isReserveMet = ""
    gdurl = (f'https://auctions.godaddy.com/trpItemListing.aspx?domain={searched_word}')
    print(f'!!! BREAK for few SECONDS !!!!\n')
    time.sleep(random.uniform(config.delay_range[0], config.delay_range[1]))
    res = session.get(gdurl, headers=headers, proxies=proxy)
    soup2 = BeautifulSoup(res.text, 'html.parser')

    try:
        rare_page = soup2.find('span', id='spanDomainName').text.strip()
    except:
        rare_page = False

    if rare_page:
        print('Checking Rare Page...\n')
        buyitnow = ""
        try:
            buyitnow = soup2.find('div', id='divBuyNowSection').text.strip()
        except:
            buyitnow = False

        if buyitnow:
            print('No Auction ! \n')
            source = "0"
        else:
            print('Accessing Rare Page...\n')
            source = 'G'

            bidders_data = soup2.find_all('div', id='auction-listing-details')

            for data in bidders_data:
                divData = data.find_all('div')
                bidders = divData[0].text.replace('Bids/Offers: ', '')

            current_bid = soup2.find('input', attrs={'class': 'form-control pull-right'}).get('value').replace(
                ' or more', '').replace('Bid ', '')
            if current_bid:
                current_bid_int = int(current_bid.replace("$", ""))

    else:
        print('Not Rare Page.. \n')

        page_title = soup2.find('title').text.strip()

        if page_title == 'Domain Auction | Buy & Sell Distinctive Domains - GoDaddy':
            print('No Auction ! \n')
            source = "0"

        else:
            print('Found the auction ..')
            source = 'G'
            get_page_api = re.match('.*?([0-9]+)$', res.url).group(1)
            page_api = (f'https://www.godaddy.com/domain-auctions/api/listing/{get_page_api}/')
            try:
                res = session.get(page_api, headers=headers, proxies=proxy)
                data_json = json.loads(res.text)
                bidders = data_json.get('biddersCount')
                current_bid_ori = data_json['currentPrice'][0]['cost']
                if "inventoryType" in data_json:
                    inventoryType = data_json["inventoryType"]
                count_current_bid = str(current_bid_ori)

                if "isReserveMet" in data_json:
                    isReserveMet = data_json["isReserveMet"]

                if len(count_current_bid) == 7:
                    current_bid = str('$') + count_current_bid[:1]
                elif len(count_current_bid) == 8:
                    current_bid = str('$') + count_current_bid[:2]
                elif len(count_current_bid) == 9:
                    current_bid = str('$') + count_current_bid[:3]
                elif len(count_current_bid) == 10:
                    current_bid = str('$') + count_current_bid[:4]
                elif len(count_current_bid) == 11:
                    current_bid = str('$') + count_current_bid[:5]
                elif len(count_current_bid) == 12:
                    current_bid = str('$') + count_current_bid[:6]
                elif len(count_current_bid) == 13:
                    current_bid = str('$') + count_current_bid[:7]
                elif len(count_current_bid) == 14:
                    current_bid = str('$') + count_current_bid[:8]
                elif len(count_current_bid) == 15:
                    current_bid = str('$') + count_current_bid[:9]
                elif len(count_current_bid) == 16:
                    current_bid = str('$') + count_current_bid[:10]
                if current_bid:
                    current_bid_int = int(current_bid.replace("$", ""))
            except:
                pass

    if skip_file and (source == 'G') and (current_bid_int < max_bid) and current_bid != '':
        chrome_options = Options()
        chrome_options.add_argument('user-agent={}'.format(UserAgent().random))
        chrome_options.add_argument('--ignore-certificate-errors')
        chrome_options.add_argument('--incognito')
        chrome_options.add_argument("--headless")
        driver = Chrome(options=chrome_options)
        driver.set_window_size(1200 + random.uniform(-100, 100), 800 + random.uniform(-100, 100))
        driver.set_page_load_timeout(5)
        try:
            driver.get("http://" + searched_word)
            time.sleep(5)
            skip_soup = BeautifulSoup(driver.page_source, 'html.parser')
            req_div = skip_soup.select("div#domainInfo")
            if len(req_div) > 0:
                req_div = req_div[0]
                if "godaddy auctions" in req_div.text.lower():
                    active_auction = True
            domain_object = {
                "searched_word": searched_word,
                "source" : source,
                "bidders": bidders,
                "current_bid": current_bid,
                "notes": notes,
                "active_auction": active_auction,
                "current_bid_int": current_bid_int,
                "inventoryType": inventoryType
            }
            print(domain_object)
            return domain_object
                    
        except TimeoutException:
            pass
        except:
            pass

def write_searched_words(good_domains):
    today = datetime.today()
    with open(f"good_{today.strftime('%Y%d%m_%H%M%S')}.txt", "w") as file:
        for domain_object in good_domains:
            file.write(domain_object["searched_word"] + "\n")

def main():
    domains = utils.get_terms()
    good_domains = []

    with ThreadPoolExecutor(max_workers=threads) as executor:
        for result in executor.map(generating_data, domains):
            if result:
                good_domains.append(result)

    write_searched_words(good_domains)


if __name__ == '__main__':
    main()