import requests
import json, time, random
import csv
import re
from datetime import datetime
from bs4 import BeautifulSoup
import config
import utils
from concurrent.futures import ThreadPoolExecutor
import cloudscraper
import pandas as pd

delay_range = config.delay_range
proxies = utils.get_proxies()
threads = config.threads
full_report = config.full_report
headers_list = [
    # 1. Headers
    {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:86.0) Gecko/20100101 Firefox/86.0', 
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Cache-Control': 'max-age=0'},
    # 2. Headers
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
    # 3 header
    {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36', 'Accept-Encoding': 'gzip, deflate', 'Accept': '*/*', 'Connection': 'keep-alive'}
]

headers = random.choice(headers_list)

def generating_data(searched_word):
    # proxy = {"http": proxies[(random.randrange(len(proxies)))]}

    print(f'Keywords = {searched_word}\n')
    source = ''
    preorder_price = float('nan')
    order_by_date = ''
                
    # session = requests.Session(proxies=proxy)

    # res = session.get(gdurl, headers=headers, proxies=proxy)      
    scraper = cloudscraper.create_scraper(browser={'browser': 'firefox','platform': 'linux','mobile': False})
    njurl = "https://www.namejet.com/domain/"+searched_word+".action"
    res = scraper.get(njurl)
    # print(res)
    soup = BeautifulSoup(res.text, 'html.parser')
    preorder_div = soup.find_all(attrs={"class": "bidBoxTopInfo"})
    preorder_div = preorder_div[0].find_all(attrs={"class": "bidBoxCategory"})
    if preorder_div[0].text.strip()=="Pre-order price:":
        preorder_price = float(soup.find_all(attrs={"itemprop": "minPrice"})[0].text)
    
    try:
        order_by_date = soup.find_all(attrs={"itemprop": "validThrough"})[0].text
    except:
        pass
    left_half = soup.find_all(attrs={"class": "half_left leftDetails margin-top"})[0]
    table = left_half.find_all("table")[0]
    source=""
    # print(table.find_all("tr"))
    for tr in table.find_all("tr"):
        # print(tr.find_all("td")[0].text)
        if tr.find_all("td")[0].text.strip()=="Source:":
            source = tr.find_all("td")[1].text.strip()
    # print(source)
    # print(preorder_price)
    # print(order_by_date)
    print("NJ Auction", searched_word, source, preorder_price, order_by_date)
    return [searched_word, source, preorder_price, order_by_date]
    # auc_type = soup.find('span', id='ctl00_ContentPlaceHolder1_lblType').text.strip()

    # if auc_type == 'Wish List - No Current Auction':
    #     print('No Auction ! \n')
    #     source = '0'
    # else:
    #         print('Found the auction..\n')
    #         source = 'N'
    #         try :
    #             bidders_unproced = soup.find('span', id='ctl00_ContentPlaceHolder1_lblBidHistory').text.strip()
    #             bidders = re.sub(r'(bids|bid)', '', bidders_unproced).strip()
    #         except:
    #             bidders_unproced = soup.find('span', id='ctl00_ContentPlaceHolder1_lblBidders').text.strip()
    #             bidder = re.match(r'(^\d+)', bidders_unproced)
    #             bidders = bidder.group(0)

    #         try :
    #             current_bid = soup.find('span', id='ctl00_ContentPlaceHolder1_lblCurrentBid').text.replace('USD','').strip()
    #         except:
    #             current_bid = soup.find('span', id='ctl00_ContentPlaceHolder1_LabelCurrentBid').text.replace('USD','').strip()


    #         if current_bid == 'No Bids':
    #             current_bid = 0

    #         try:
    #             notes = soup.find('span', id='ctl00_ContentPlaceHolder1_lblReserveRange').text.strip()
    #             if notes:
    #                 notes = 'Reserve'
    #         except:
    #             notes = ""

    # temp = ([searched_word, source, bidders, current_bid, notes])
    # print(f'Result = {temp}')

    # print(f'!!! BREAK for few SECONDS !!!!\n')
    # time.sleep(random.uniform(config.delay_range[0], config.delay_range[1]))


    # return [searched_word, source, bidders, current_bid, notes]

    

def main():
    Details = ['Domain', 'Source', 'Preorder Price', 'Order by Date']
    domains = utils.get_terms()
    # domains = ["katmoviehds.com", "syscomsrv.com"]
    rows = []
    executor = ThreadPoolExecutor(max_workers=threads)
    for result in executor.map(generating_data, domains):
        rows.append(result)
    # for domain in domains:
    #     rows.append(generating_data(domain))
    today = datetime.today()
    df = pd.DataFrame(rows, columns=Details)
    df.loc[(df["Source"]=='') | (df["Source"]=='Private Seller') | (df["Preorder Price"].isna()) | (df["Preorder Price"]>=100) | (df["Order by Date"]==''), 'Domain'].to_csv(f"remove_{today.strftime('%Y%d%m_%H%M%S')}.txt", index=False, header=False)

    if full_report:
        df.to_csv(f"full_report_{today.strftime('%Y%d%m_%H%M%S')}.csv", index=False)
    # else:
    #     df[df["Source"]!='0'].to_csv(f"report_{today.strftime('%Y%d%m_%H%M%S')}.csv", index=False)

    # with open(f"report_{today.strftime('%Y%d%m_%H%M%S')}.csv", 'w', newline='') as f: 
    #     write = csv.writer(f) 
    #     write.writerow(Details) 
    #     write.writerows(rows)



if __name__ == '__main__':
    main()