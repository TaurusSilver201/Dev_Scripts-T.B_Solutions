import utils
import config
from http.client import FORBIDDEN
import requests
from requests.packages import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
import json, time, random, html
import csv
import re
import datetime
import itertools
import threading
from concurrent.futures import ThreadPoolExecutor
import ast
from bs4 import BeautifulSoup
from collections import defaultdict
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
from time import sleep
from fake_useragent import UserAgent
import country_converter as coco
# import undetected_chromedriver as uc
# chrome_options = Options()
# # chrome_options.add_argument('user-agent={}'.format(UserAgent().random))
# # chrome_options.add_argument('--proxy-server=%s' % proxy)
# chrome_options.add_argument('--ignore-certificate-errors')
# chrome_options.add_argument('--incognito')
# chrome_options.add_argument("--headless")
# driver = uc.Chrome(options=chrome_options)
# import nltk
# nltk.download('stopwords')
import math
import pandas as pd
import http.client
import json
import tldextract
import cloudscraper
import httpx
import os

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

# headers = random.choice(headers_list)
proxies = utils.get_proxies()
good_proxy = []
def extract(proxy):
    #this was for when we took a list into the function, without conc futures.
    #proxy = random.choice(proxylist)
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:80.0) Gecko/20100101 Firefox/80.0'}
    try:
        #change the url to https://httpbin.org/ip that doesnt block anything
        r = requests.get('https://httpbin.org/ip', headers=headers, proxies={'http' : proxy,'https': proxy}, timeout=2)
        print(r.json(), ' | Works')
        good_proxy.append(proxy)
    except: 
        pass

with ThreadPoolExecutor() as executor:
    executor.map(extract, proxies)

proxies = good_proxy

all_results = defaultdict(lambda: defaultdict(dict))
our_stop_words = utils.get_stop_words()
keywords = set(utils.get_keywords())
all_terms_score = []
all_keywords_score = []


def easyCounter(domains):
    for searched_word in domains:
        print('EasyCounter ', searched_word)
        proxy = random.choice(proxies)
        headers = random.choice(headers_list)

        ec_url = (f'https://www.easycounter.com/report/{searched_word}')
        ec_url2 = (f'https://www.easycounter.com/get/{searched_word}/metadata')
        session = requests.Session()
        sleep(random.uniform(config.delay_range[0], config.delay_range[1]))
        res_ec = session.get(ec_url, headers=headers, proxies={'http' : proxy,'https': proxy})

        soup1 = BeautifulSoup(res_ec.text, 'html.parser')

        article = soup1.find('article', attrs={"itemscope": "itemscope"})
        article2 = article.find('section', class_='content').text.strip()
        ec = 0
        title_ec = ''
        desc_ec = ''
        country_ec = ''
        traffic = ''
        social_signal = ''
        category = ''
        found = False
        if article2 == 'Nothing found':
            print(f'{searched_word}, EasyCounter = No Data! \n')
        else:
            ec = 0.5
            print(f'{searched_word}, EasyCounter = Found!')
            found = True
            try: 
                sleep(random.uniform(config.delay_range[0], config.delay_range[1]))
                res2 = requests.get(ec_url2, headers=headers, proxies={'http' : proxy,'https': proxy})
                datas = res2.json()
            except:
                pass

            try:
                title = soup1.find_all('div', class_='description_text left')
                title_ec  = title[1].find('h2').text.strip()
            except:
                title_ec = ''

            try:
                desc_ec = datas['title']
            except:
                desc_ec = ''

            try:
                categories = soup1.find_all('table', class_='rating_site')
                category_list = categories[1].find_all('tr')
                if category_list:
                    category = category_list[3].find_all('td')[-1].text.strip()
                else:
                    category = ''
            except:
                category = ''
        
            try:
                countries = soup1.find('div', class_='table-medium -t-countries')
                countries2 = countries.find('span', class_='flag_icon')
                country_ec = countries2['title']
            except:
                country_ec = ''

            try:
                traffics = soup1.find('div', class_='diagram_img -d-first').find('script')
                p = re.compile('var values = (.*);') 
                traffic_search = p.search(traffics.string)
                traffic_lists = traffic_search.group(1)
                lst = ast.literal_eval(traffic_lists)
                def Average(lst):
                    return sum(lst) / len(lst)
                
                traffic2 = Average(lst)
                traffic = int(traffic2)
            except:
                traffic = ''

            
            try:
                social = []
                for value in  soup1.find('div', class_='social_icons').find_all('p'):
                    if value.text.strip() != '':
                        value2 = value.text.strip()
                        if value2 != '0' and  value2 != '-':
                            social.append(value2)

                for value in  soup1.find('div', class_='row_social').find_all('p'):
                    if value != '':
                        if value != '0':
                            value2 = value.text.strip()
                            if value2 != '0' and  value2 != '-':
                                social.append(value2)

                social_signal = len(social)
            except:
                social_signal = ''


            if searched_word in title_ec:
                title_ec = ''
                desc_ec = ''
            else:
                pass

            temp = ([searched_word, title_ec, desc_ec, country_ec, traffic])
            print(f'EasyCounter Result = {temp} \n')
        all_results[searched_word]["EC"] = {"domain": searched_word, "title": title_ec, "desc": desc_ec, "country": country_ec, "traffic": traffic, "found": found}
        # return [searched_word, title_ec, desc_ec, country_ec, traffic]

def owler(domains):
    for searched_word in domains:
        print('Owler ', searched_word)
        proxy = random.choice(proxies)
        headers = random.choice(headers_list)
        ow_url = (f'http://54.67.24.38/a/v1/pb/basicSearchInternal?searchTerm={searched_word}')
        # ow_url = (f'http://13.57.167.118/a/v1/pb/basicSearchInternal?searchTerm={searched_word}')
        # ow_url = (f'https://www.owler.com/a/v1/pb/basicSearchInternal?searchTerm={searched_word}')
        sleep(random.uniform(config.delay_range[0], config.delay_range[1]))
        scraper = cloudscraper.create_scraper()
        res_ow = scraper.get(ow_url, proxies={'http' : proxy,'https': proxy})
        # res_ow = requests.get(ow_url, headers=headers, proxies={'http' : proxy,'https': proxy})
        
        jdata = res_ow.json()
        # print(jdata)
        company_name = ""
        country = ""
        found = False
        try:
            if jdata["hits"] > 0:
                # if 'name' in jdata['results'][0]:
                print(f'{searched_word}, Owler = Found!')
                found = True
                if jdata['results'] == []:
                    print(f'{searched_word}, No Company name!\n')
                    ow = 0
                    title_ow = ""
                else:
                    print(f'{searched_word}, Company name found !')            
                    company_name = jdata['results'][0]['name']
                    ow = 1.5


                    json_data = {
                        'companyId': jdata['results'][0]['id'],
                        'components': [
                            'company_info',
                            'keystats',
                        ],
                        'section': 'cp',
                    }
                    sleep(random.uniform(config.delay_range[0], config.delay_range[1]))
                    response = requests.post('https://www.owler.com/iaApp/fetchCompanyProfileData.htm', json=json_data)
                    country = response.json()["company_info"]["company_details"]["hqAddress"]["country"]
                    
            else:
                print(f'{searched_word}, Owler = No Data! \n')
                ow = 0
                title_ow = ""
            
            title_ow = company_name

            if title_ow == "":
                pass
            else:
                temp = ([searched_word, title_ow, country])
                print(f'Owler Result = {temp} \n')
            
            all_results[searched_word]["OW"] =  {"domain": searched_word, "title": title_ow, "country": country, "found": found, "desc": ""}

        except:
            print("Site issues ! Skipped")
        
        # return [searched_word, title_ow, country]



# def siteLink(domains):
# # try:
#     for domain in domains:
#         print("Sitelink ", domain)
#         base_url = "https://www.sitelike.org/similar/"
        
#         title = ''
#         desc = ''
#         main_terms = ''
#         similar = []
#         similar_terms = ''
#         found = False
#         domain_dict = defaultdict(int)
#         # proxy = get_proxy()
#         # if domain=='landsharkhockey.com':
#         #     raise Exception()
#         # headers = {
#         #     "user-agent": UserAgent().random
#         # }
#         # headers = random.choice(headers_list)
#         # print(headers)
#         # scraper = cloudscraper.create_scraper()
#         # proxy = get_proxy()
#         # release_proxy(proxy)
#         chrome_options = Options()
#         chrome_options.add_argument('user-agent={}'.format(UserAgent().random))
#         # chrome_options.add_argument('--proxy-server=%s' % proxy)
#         chrome_options.add_argument('--ignore-certificate-errors')
#         chrome_options.add_argument('--incognito')
#         chrome_options.add_argument("--headless")
#         driver = Chrome(options=chrome_options)
        
#         # driver.set_page_load_timeout(5)
#         try:
#             sleep(random.uniform(config.delay_range[0], config.delay_range[1]))
#             # page = scraper.get(base_url+domain, proxies={"http": proxy}, headers=headers)
#             driver.get(base_url+domain)
#             sleep(5)
#             # soup = BeautifulSoup(page.text, 'lxml')
#             soup = BeautifulSoup(driver.page_source, 'lxml')
#             # with open('readme.html', 'w', encoding="utf-8") as f:
#             #     f.write(driver.page_source)
#             page_title = soup.find("title").text.strip()
#             # print(page_title)
#             if page_title.startswith("Top"):
#                 found = True
#                 no_of_results = int(page_title.split()[1])
#                 title_desc = soup.select("span#MainContent_lblDescription")
#                 if len(title_desc)>0:
#                     title_desc = title_desc[0].get_text(strip=True, separator='\n').splitlines()
                
#                 if len(title_desc)>0:
#                     title = title_desc[0]
#                 if len(title_desc)>1:
#                     desc = title_desc[1]
                
#                 main_terms_el = soup.select("span#MainContent_lblKeywords")
#                 if len(main_terms_el)>0:
#                     main_terms = main_terms_el[0].text.lower().split("topics:")[1].strip()
#                 # similar = no_of_results
#                 # print(similar)
#                 if no_of_results>0:
#                     panels = soup.select("div.panel.panel-default.rowP")
#                     # print(len(panels))
#                     for panel in panels:
#                         span = panel.select("span.wordwrap")
#                         tmp_dct = {}
#                         if len(span)>0:
#                             span_title = ""
#                             span_desc = ""
#                             span_title_desc_list = span[0].get_text(strip=True, separator='\n').splitlines()
#                             if len(span_title_desc_list)>0:
#                                 span_title = span_title_desc_list[0].lower().replace("-", " ").replace("'", "").strip()
#                                 span_title = "".join([ch if (ch.isalnum() or ch==" ") else " " for ch in span_title])
#                                 tmp_dct["title"] = span_title
                            
#                             if len(span_title_desc_list)>1:
#                                 span_desc = span_title_desc_list[1].lower().replace("-", " ").replace("'", "").strip()
#                                 span_desc = "".join([ch if (ch.isalnum() or ch==" ") else " " for ch in span_desc])
#                                 tmp_dct["desc"] = span_desc
                        
#                         if len(tmp_dct.keys())>0:
#                             similar.append(tmp_dct)
#         except:
#             pass                        
#         print(domain, title, desc, main_terms, similar)
#         all_results[domain]["SL"] =  {"domain": domain, "title": title, "desc": desc, "main_terms": main_terms, "similar": similar, "found": found}
#         # print("SitelInkhhhhhhh", all_results[domain]["SL"])
#         # return (domain, title, desc, main_terms, similar)

def siteIndices(domains):
    for searched_word in domains:
        print('SiteIndices ', searched_word)
        proxy = random.choice(proxies)
        headers = random.choice(headers_list)
        si_url = (f'https://{searched_word}.siteindices.com')
        sleep(random.uniform(config.delay_range[0], config.delay_range[1]))
        res_si = requests.get(si_url, headers=headers, proxies={'http' : proxy,'https': proxy})
        
        soup3 = BeautifulSoup(res_si.text, 'html.parser')

        page_title = soup3.find('title').text.strip()
        si = 0
        title_si = ""
        desc_si = ""
        country_si = ''
        price1 = ''
        traffic = 0
        found = False
        if page_title == 'HTTP Status 404 – Not Found':
            print(f'{searched_word}, SiteIndices = No Data! \n')
        else:
            found = True
            si = 1
            print(f'{searched_word}, SiteIndices = Found!')
            # price = soup3.find('div', id='valuation').text.strip()
            # price1 = price[3:].replace(",","")

            table = soup3.find_all('table', class_='table table-bordered')
            # print(table[6])
            rows = table[6].find_all('tr')
            for row in rows:
                cols = row.find_all('td')
                if cols[0].text == "Daily Unique Visitors":
                    trf = cols[1].text
                    traffic1 = re.sub(r'\W+', '', trf)
                    traffic = int(traffic1)
                    break
            # print(traffic)
            # for t in table:
            #     print(t)
            table_data = []
            # rows = table[7].find_all('tr')
            # for row in rows:
            #     cols = row.find_all('td')
            #     cols = [ele.text.strip() for ele in cols]
            #     table_data.append([ele for ele in cols if ele]) 

            # country_si = table_data[2][1]
            # if country_si == 'N/A':
            #     country_si = ''

            table_data = []
            rows = table[1].find_all('tr')
            for row in rows:
                cols = row.find_all('td')
                cols = [ele.text.strip() for ele in cols]
                table_data.append([ele for ele in cols if ele])
            
            title_si = table_data[0][1]
            desc_si = table_data[1][1]
            if desc_si == 'N/A':
                desc_si = ''
            
            temp = ([searched_word, title_si, desc_si, traffic])
            print(f'SiteIndices Result = {temp} \n')
        all_results[searched_word]["SI"] = {"domain": searched_word, "title": title_si, "desc": desc_si, "traffic": traffic, "found": found}
        # return ([searched_word, title_si, desc_si, traffic])


def yellowPages(domains):
    for domain in domains:
        print('YellowPages ', domain)
        proxy = random.choice(proxies)
        headers = random.choice(headers_list)
        url = "https://www.yellowpages.net/listing/places/?q="+domain
        sleep(random.uniform(config.delay_range[0], config.delay_range[1]))
        res = requests.get(url, headers=headers, proxies={'http' : proxy,'https': proxy})
        
        soup = BeautifulSoup(res.text, 'html.parser')
        divs = soup.select("div.cc-content")
        # print(len(divs))
        title = ""
        stats = ""
        category = ""
        country = ""
        desc = ""
        found = False
        if len(divs)>0:
            found = True
            url = divs[0].select("h2.card__title a")[0]['href']
            # print(url)
            sleep(random.uniform(config.delay_range[0], config.delay_range[1]))
            res = requests.get(url, headers=headers, proxies={'http' : proxy,'https': proxy})
            soup = BeautifulSoup(res.text, 'html.parser')
            title_div = soup.select("div.company-main-info")
            if len(title_div)>0:
                h1 = title_div[0].select("h1")
                if len(h1)>0:
                    title = h1[0].text
                # print(title)
            stats_divs = soup.select("div.one-rating div.flex-wrapper")
            if len(stats_divs)>0:
                tmp_lst = []
                for div in stats_divs:
                    tmp_lst.append(" ".join(div.text.split()[1:]))

                stats = ",".join(tmp_lst)
            
            category_lis = soup.select("li.breadcrumb-item a")
            if len(category_lis)>0:
                category = category_lis[1].text.split(" in ")[0].strip()
                country = category_lis[1].text.split(" in ")[1].strip()
            
            desc_div = soup.select("div.card__primary div.card-description")
            desc_ps = desc_div[0].select("p")
            for p in desc_ps:
                desc+=p.text.strip() + " "
            desc=desc.replace("\n", " ").strip()
        
        print("YelloPages", domain, title, stats, category, country, desc)

        all_results[domain]["YP"] =  {"domain": domain, "title": title, "stats": stats, "category": category, "country": country, "desc": desc, "found": found}
        # return [domain, title, stats, category, country, desc]


def couponBirds(domains):
    for domain in domains:
        print('CouponBirds ', domain)
        # proxy = random.choice(proxies)
        # params = {
        #     'source': 'search',
        #     'query': domain,
        # }
        # scraper = cloudscraper.create_scraper()
        # res = scraper.get(ow_url, proxies={'http' : proxy,'https': proxy})
        # sleep(random.uniform(config.delay_range[0], config.delay_range[1]))
        # res = scraper.get('https://www.couponbirds.com/codes/'+domain, params=params)
        # print(res)
        url = 'https://www.couponbirds.com/codes/'+domain
        data = ""

        if os.path.isfile(config.paid_api_results_folder+"serper-cb-"+domain+".json"):
            print("result for "+url+" found in paid_api_results/serper-cb-"+domain+".json")
            text_file = open(config.paid_api_results_folder+"serper-cb-"+domain+".json", "r", encoding="utf-8")
            data = text_file.read()
            text_file.close()
        
        if len(data)==0:
            print("result for "+url+" not found in paid_api_results/serper-cb")

            conn = http.client.HTTPSConnection("google.serper.dev")
            payload = json.dumps({
                "q": "site:couponbirds.com \""+domain+"\"",
                "gl": "us",
                "hl": "en",
                "autocorrect": False,
                "page": 1,
                "type": "search"
            })
            headers = {
                'X-API-KEY': config.serper_api,
                'Content-Type': 'application/json'
            }
            conn.request("POST", "/search", payload, headers)
            res = conn.getresponse()
            data = res.read()
            with open(config.paid_api_results_folder+"serper-cb-"+domain+".json", "w", encoding="utf-8") as f:
                f.write(data.decode("utf-8"))
        # with open("test.html", "w") as f:
        #     f.write(data.decode("utf-8"))
        
        results_serper = json.loads(data)
        # print(results_serper)
        # if ("organic" in results_serper) and (len(results_serper["organic"])>0):
        if ("organic" in results_serper):
            for organic in results_serper["organic"]:
                # organic = results_serper["organic"][0]
                if ("link" in organic) and (organic["link"]==url):
                    print("CB", domain, "!!!!!!!!")
                    response_txt = ""
                    if os.path.isfile(config.paid_api_results_folder+"zenrows-cb-"+domain+".txt"):
                        print("result for "+url+" found in paid_api_results/zenrows-cb"+domain+".txt")
                        text_file = open(config.paid_api_results_folder+"zenrows-cb-"+domain+".txt", "r", encoding="utf-8")
                        response_txt = text_file.read()
                        text_file.close()
                    
                    if len(response_txt)==0:
                        print("result for "+url+" not found in paid_api_results/zenrows-cb")
                    
                        proxy = config.zenrows_proxy
                        proxies = {"http": proxy, "https": proxy}
                        res = requests.get(url, proxies=proxies, verify=False)
                        response_txt = res.text

                        with open(config.paid_api_results_folder+"zenrows-cb-"+domain+".txt", "w", encoding="utf-8") as f:
                            f.write(response_txt)
                    
                    
                    soup = BeautifulSoup(response_txt, 'html.parser')

                    # soup = BeautifulSoup(res.text, 'html.parser')
                    # title = soup.find_all("a", {"class": ["js-common-log-click", "go-store", "d-md-brand-none"]})

                    found = False
                    title = ""
                    rating = ""
                    coupons = ""
                    title_link = soup.find_all("a", {"href": "/out/"+domain})
                    if len(title_link)>0:
                        found = True
                        title_link[0].find("svg").decompose()
                        # print(title_link[0].text.split("Shop ")[1].strip())
                        title = title_link[0].text.split("Shop ")[1].strip()
                        # rating_div = soup.find_all("div", {"itemprop": "aggregateRating"})
                        # print(rating_div)
                        ratingValue_p = soup.find_all("p", {"itemprop": "ratingValue"})
                        if len(ratingValue_p)>0:
                            # print(ratingValue_p[0].text)
                            rating += ratingValue_p[0].text
                        
                        ratingCount_p = soup.find_all("p", {"itemprop": "ratingCount"})
                        if len(ratingCount_p)>0:
                            # print(ratingCount_p[0].text)
                            rating += "/"+ratingCount_p[0].text
                        # print(rating)

                        coupon_div = soup.find_all("div", {"class": "coupon-info"})
                        if len(coupon_div)>0:
                            coupon_p = coupon_div[0].find("p", {"class": "title"})
                            # print(coupon_p.text.split(",")[1].strip().split()[0])
                            coupons = coupon_p.text.split(",")[1].strip().split()[0]

                    print("CouponBirds", domain, title, rating, coupons)
                    all_results[domain]["CB"] =  {"domain": domain, "title": title, "rating": rating, "coupons": coupons, "found": found}
                    break
                            
        





# def siteLinkThread(domains):
#     for domain in domains:
#         siteLink(domain)



def get_substr(s, imp_ky):
    word = " "
    lst = [0]
    for match in re.finditer(word, s):
        lst.append(match.end())
    lst.append(len(s))
    sbstr_set = {s[lst[i]: lst[j]].strip() for i in range(len(lst)-1) for j in range(i+1, min(i+config.max_words+1, len(lst))) if " " in s[lst[i]: lst[j]].strip()}
    sbstr_set = {wrd for wrd in sbstr_set if any(ky in wrd for ky in imp_ky)}

    return sbstr_set

def main():
    domains = utils.get_terms()
    # domains = ["amazon.com", "jmlbooks.com", "flipkart.com"]
    # domains = ["corporatequest.org", "google.com"]
    # domains = ["agmhomestore.com"]
    results = []
    with ThreadPoolExecutor(max_workers=5) as executor:
    #     # executor.submit(siteLink, domains)
        executor.submit(easyCounter, domains)
        executor.submit(owler, domains)
        executor.submit(siteIndices, domains)
        executor.submit(yellowPages, domains)
        executor.submit(couponBirds, domains)
    # for domain in domains:
    
    # couponBirds(domains)
    # # return
    # easyCounter(domains)
    # # owler(domains)
    # # siteLink(domains)
    # siteIndices(domains)
    # yellowPages(domains)
    # service_count = defaultdict(int)
    # siteLink_domains = []
    # for domain in domains:
    #     s_cnt = 0
    #     for service in all_results[domain]:
    #         if all_results[domain][service]["found"]:
    #             s_cnt+=1
    #     if s_cnt>=config.smart_check_services_threshold:
    #         siteLink_domains.append(domain)
    
    # siteLink(siteLink_domains)

    
    final_result = []
    print(all_results)
    for domain in domains:
        row_dct = defaultdict(int)
        row_dct["domain"] = domain
        country_dct = defaultdict(int)
        for service in all_results[domain]:
            if all_results[domain][service]["found"]:
                if service == "YP":
                    row_dct["country"] = all_results[domain][service]["country"]
                    row_dct["YP.category"] = all_results[domain][service]["category"]
                    if all_results[domain][service]["desc"].lower().startswith("the industry in which"):
                        all_results[domain][service]["desc"] = ""

                if "country" in all_results[domain][service]:
                    try:
                        cntry = coco.convert(names=all_results[domain][service]["country"], to='ISO2')
                        if cntry!='not found':
                            country_dct[cntry]+=1
                    except:
                        pass
                row_dct[service] = "Yes" 
                # row_dct[service] = all_results[domain][service] 
                row_dct["services_count"] += 1

                if "title" not in row_dct:
                    row_dct["title"] = all_results[domain][service]["title"]
                row_dct["title"] = row_dct["title"] if len(row_dct["title"])>=len(all_results[domain][service]["title"]) else all_results[domain][service]["title"]

                if "desc" in all_results[domain][service]:
                    if "desc" not in row_dct:
                        row_dct["desc"] = all_results[domain][service]["desc"]
                    row_dct["desc"] = row_dct["desc"] if len(row_dct["desc"])>=len(all_results[domain][service]["desc"]) else all_results[domain][service]["desc"]

                if service == "CB":
                    row_dct[service] = "Yes-" + all_results[domain][service]["rating"] + "-" + all_results[domain][service]["coupons"]


            # else:
            #     row_dct[service] = False
        mx = 0
        cmax = ""
        for country in country_dct:
            if country_dct[country]>mx:
                mx=country_dct[country]
                cmax=country
        if (mx>1) or ("country" not in row_dct) or (len(row_dct["country"])==0):
            row_dct["country"] = cmax
        

        if row_dct["services_count"]>=config.services_count_for_yelp:
            # imp_ky_terms = gatherKeywords(row_dct["title"], row_dct["desc"], domain)
            # if len(imp_ky_terms["imp_keywords"])>0:
            #     row_dct["important_keywords"] = imp_ky_terms["imp_keywords"]

            # for i in range(len(imp_ky_terms["imp_terms"])):
            #     row_dct["term"+str(i+1)+" - term"+str(i+1)+".Score"] = imp_ky_terms["imp_terms"][i][0] + " - " + str(round(imp_ky_terms["imp_terms"][i][1], 2))
            #     row_dct["term"+str(i+1)] = imp_ky_terms["imp_terms"][i][0]
            data = ""
            if os.path.isfile(config.paid_api_results_folder+"serper-yelp-"+domain+".json"):
                print("result for "+domain+" found in paid_api_results/serper-yelp-"+domain+".json")
                text_file = open(config.paid_api_results_folder+"serper-yelp-"+domain+".json", "r", encoding="utf-8")
                data = text_file.read()
                text_file.close()
            
            if len(data)==0:
                print("result for "+domain+" not found in paid_api_results/serper-yelp")

                conn = http.client.HTTPSConnection("google.serper.dev")
                payload = json.dumps({
                    "q": "site:yelp.com \""+domain+"\"",
                    "gl": "us",
                    "hl": "en",
                    "autocorrect": False,
                    "page": 1,
                    "type": "search"
                })
                headers = {
                    'X-API-KEY': config.serper_api,
                    'Content-Type': 'application/json'
                }
                conn.request("POST", "/search", payload, headers)
                res = conn.getresponse()
                data = res.read()
                with open(config.paid_api_results_folder+"serper-yelp-"+domain+".json", "w", encoding="utf-8") as f:
                    f.write(data.decode("utf-8"))
                
            # with open("test.html", "w") as f:
            #     f.write(data.decode("utf-8"))
            results_serper = json.loads(data)
            # results_serper = json.loads(data.decode("utf-8"))
            # print(results_serper)
            yelp = ""
            # if ("organic" in results_serper) and (len(results_serper["organic"])>0):
            if ("organic" in results_serper):
                for organic in results_serper["organic"]:
                    # organic = results_serper["organic"][0]
                    if (domain.lower() in organic["title"].lower()) or (domain.lower() in organic["snippet"].lower()):
                        if "link" in organic:
                            yelp = "Yes"
                        
                        if "ratingCount" in organic:
                            if organic['ratingCount']>0:
                                yelp+=" - "+str(organic['ratingCount'])
                                # yelp+=" - Yelp.reviews"
                        break

            # print(yelp)
            row_dct["yelp"] = yelp

            for kwd in keywords:
                if (("desc" in row_dct) and (kwd.lower() in row_dct["desc"].lower())) or (("title" in row_dct) and (kwd.lower() in row_dct["title"].lower())) or (("YP.category" in row_dct) and (kwd.lower() in row_dct["YP.category"].lower())):
                    row_dct["notes"] = "KW"
                    break
            # imp_terms_output = []
            
            # for i in range(len(imp_ky_terms["imp_terms"])):
            #     imp_terms_output_dct = {}
            #     tmp_term = imp_ky_terms["imp_terms"][i][0]
            #     imp_terms_output_dct["term"] = tmp_term
            #     imp_terms_output_dct["score"] = round(imp_ky_terms["imp_terms"][i][1], 2)
                
            #     my_data = {
            #         'country': row_dct["country"],
            #         'currency': 'USD',
            #         'dataSource': 'gkp',
            #         'kw[]': [tmp_term]
            #     }
            #     my_headers = {
            #         'Accept': 'application/json',
            #         'Authorization': 'Bearer '+config.kweverywhere_api
            #     }

            #     response = requests.post('https://api.keywordseverywhere.com/v1/get_keyword_data', data=my_data, headers=my_headers)
            #     if response.status_code == 200:
            #         # print(response.content.decode('utf-8'))
            #         tmp_data = json.loads(response.content.decode('utf-8'))
            #         if ("data" in tmp_data) and (len(tmp_data["data"])>0):
            #             if "cpc" in tmp_data["data"][0]:
            #                 imp_terms_output_dct["cpc"] = float(tmp_data["data"][0]["cpc"]["value"])
            #                 # if i<3:
            #                 #     cpc+=float(tmp_data["data"][0]["cpc"]["value"])
            #                 #     row_dct["cpc"+str(i+1)] = float(tmp_data["data"][0]["cpc"]["value"])
            #             if "competition" in tmp_data["data"][0]:
            #                 imp_terms_output_dct["comp"] = tmp_data["data"][0]["competition"]
            #                 # if i<3:
            #                 #     comp+=tmp_data["data"][0]["competition"]
            #                 #     row_dct["comp"+str(i+1)] = tmp_data["data"][0]["competition"]
                    
            #         # with open('readme.txt', 'w', encoding="utf-8") as f:
            #         #     f.write(response.content.decode('utf-8'))
            #     else:
            #         print("An error occurred\n\n", response.content.decode('utf-8'))
            #     imp_terms_output.append(imp_terms_output_dct)
            
            # if len(imp_terms_output)>0:
            #     row_dct["important_terms"] = imp_terms_output
            #     top_3_terms_output = []
            #     for i in range(min(10, len(imp_terms_output))):
            #         # print(imp_terms_output[i]["comp"])
            #         if (imp_terms_output[i]["comp"]>=config.comp_thresehold):
            #             top_3_terms_output_dct = imp_terms_output[i].copy()
            #             top_3_terms_output_dct["score2"] = top_3_terms_output_dct["score"] * top_3_terms_output_dct["cpc"] * top_3_terms_output_dct["comp"]
            #             top_3_terms_output.append(top_3_terms_output_dct)
            #             # print("top_3_terms_output_dct", top_3_terms_output_dct)
                
            #     # print("top_3_terms_output", top_3_terms_output)
                
            #     if len(top_3_terms_output)>0:
            #         top_3_terms_output = sorted(top_3_terms_output, key=lambda d: d['score2'], reverse=True)
            #         # print("top_3_terms_output", top_3_terms_output)
            #         cpc = 0
            #         comp = 0
            #         for i in range(min(3, len(top_3_terms_output))):
            #             cpc+=top_3_terms_output[i]["cpc"]
            #             comp+=top_3_terms_output[i]["comp"]
            #             row_dct["cpc"+str(i+1)] = top_3_terms_output[i]["cpc"]
            #             row_dct["comp"+str(i+1)] = top_3_terms_output[i]["comp"]
            #             row_dct["term"+str(i+1)+" - term"+str(i+1)+".Score"] = top_3_terms_output[i]["term"] + " - " + str(round(top_3_terms_output[i]["score"], 2))
            #             row_dct["term"+str(i+1)] = top_3_terms_output[i]["term"]
                    
            #         row_dct["avg_cpc"] = round(cpc/min(3, len(top_3_terms_output)), 2)
            #         row_dct["avg_comp"] = round(comp/min(3, len(top_3_terms_output)), 2)

            
            # if len(imp_ky_terms["imp_terms"])>0:
            #     row_dct["avg_cpc"] = round(cpc/len(imp_ky_terms["imp_terms"]), 2)
            #     row_dct["avg_comp"] = round(comp/len(imp_ky_terms["imp_terms"]), 2)


        final_result.append(row_dct)
    
    report_df = pd.DataFrame(final_result)
    # full_report_df = pd.DataFrame(final_result)
    # regular_report_df = full_report_df.copy()
    # cols = [cols for cols in list(full_report_df.columns) if cols not in ["term1", "term2", "term3"]]
    # full_report_df = full_report_df[cols]
    report_columns = ['domain', 'EC', 'SI', 'OW', 'YP', 'CB', 'yelp', 'title', 'desc', 'country', "YP.category", "notes"]
    # full_columns = ['domain', 'EC', 'SI', 'OW', 'SL', 'YP', 'yelp', 'title', 'desc', 'country', "YP.category", 'important_keywords', 'important_terms', "term1 - term1.Score", "cpc1", "comp1", "term2 - term2.Score", "cpc2", "comp2", "term3 - term3.Score", "cpc3", "comp3"]
    # for col in full_columns:
    #     if col not in list(full_report_df.columns):
    #         full_report_df[col] = ''
    
    for col in report_columns:
        if col not in list(report_df.columns):
            report_df[col] = ''
    # cols = [col for col in full_columns if col in list(full_report_df.columns)]
    # full_report_df = full_report_df[cols]
    report_df = report_df[report_columns]
    # full_report_df = full_report_df[full_columns]
    # if config.full_report:
    #     full_report_df.to_csv("full_report_" + datetime.datetime.today().strftime('%Y%d%m_%H%M%S') + ".csv", index=False)
    report_df.to_csv("report_" + datetime.datetime.today().strftime('%Y%d%m_%H%M%S') + ".csv", index=False)

    # cols = ["domain", "services_count", "title", "desc", "country"]
    # cols = [cols for cols in list(regular_report_df.columns) if cols not in ["SL", "SI", "EC", "OW", "YP", "important_keywords", "term1 - term1.Score", "term2 - term2.Score", "term3 - term3.Score"]]
    # regular_columns = ["domain", "services_count", "yelp", "title", "desc", "country", "YP.category", "avg_cpc", "avg_comp", "term1", "term2", "term3"]
    # for col in regular_columns:
    #     if col not in list(regular_report_df.columns):
    #         regular_report_df[col] = ''
    # # cols = [col for col in regular_columns if col in list(regular_report_df.columns)]
    # # regular_report_df = regular_report_df[cols]
    # regular_report_df = regular_report_df[regular_columns]
    # regular_report_df.to_csv("regular_report_" + datetime.datetime.today().strftime('%Y%d%m_%H%M%S') + ".csv", index=False)

    # if config.score_report:
    #     kywrd_df = pd.DataFrame(all_keywords_score)
    #     kywrd_df.to_csv("keywords_score_" + datetime.datetime.today().strftime('%Y%d%m_%H%M%S') +  ".csv", index=False)
    #     trm_df = pd.DataFrame(all_terms_score)
    #     trm_df.to_csv("terms_score_" + datetime.datetime.today().strftime('%Y%d%m_%H%M%S') +  ".csv", index=False)
        
    
    # print(all_results)
    # print(final_result)

main()



# def gatherKeywords(title, desc, domain):
#     conn = http.client.HTTPSConnection("google.serper.dev")
#     # "domain" -inurl:domain -inurl:siteindices.com -inurl:cutestat.com -inurl:sitelike.org -inurl:allbiz.com -inurl:buzzfile.com -inurl:yellowpages -inurl:zoominfo.com -inurl:linkedin
#     gq = '"' + domain + '" -inurl:' + domain + ' -inurl:siteindices.com -inurl:cutestat.com -inurl:sitelike.org -inurl:allbiz.com -inurl:buzzfile.com -inurl:yellowpages -inurl:zoominfo.com -inurl:linkedin'
#     # print("Google Query : ", gq)
#     payload = json.dumps({
#         "q": gq,
#         "gl": "us",
#         "hl": "en",
#         "autocorrect": False
#     })

#     headers = {
#         'X-API-KEY': config.serper_api,
#         'Content-Type': 'application/json'
#     }

#     conn.request("POST", "/search", payload, headers)
#     res = conn.getresponse()
#     data = res.read()
#     # with open("test.html", "w") as f:
#     #     f.write(data.decode("utf-8"))
#     results = json.loads(data.decode("utf-8"))
#     # print(results)
#     if "organic" in results:
#         results = results["organic"]
#     else:
#         results = []
#     serper_dct = defaultdict(lambda: defaultdict(str))

#     for tmp_result in results:
#         if "link" in tmp_result:
#             tsd, td, tsu = tldextract.extract(tmp_result["link"])
#             domain2 =(td + '.' + tsu).lower()
#             # domain = domain.replace("-", "")
#             serper_dct[domain2]["title"] +=  " " + tmp_result["title"]
#             serper_dct[domain2]["snippet"] +=  " " + tmp_result["snippet"]


#     main_terms = ""
#     if "main_terms" in all_results[domain]["SL"]:
#         main_terms = all_results[domain]["SL"]["main_terms"]
    
#     similar = ""
#     if "similar" in all_results[domain]["SL"]:
#         similar = all_results[domain]["SL"]["similar"]
    
#     category = ""
#     if "category" in all_results[domain]["YP"]:
#         category = all_results[domain]["YP"]["category"] 

#     similar_lst = []
#     tmp_str = ""
#     for sm in similar:
#         s = ""
#         if "title" in sm:
#             s+=sm["title"]
#         if "desc" in sm:
#             s+=" "+sm["desc"]
#         tmp_str+=s+" "
#         similar_lst.append(s.strip())
    
#     serper_lst = []
#     for sm in serper_dct:
#         s = ""
#         if "title" in serper_dct[sm]:
#             serper_dct[sm]["title"] = serper_dct[sm]["title"].lower().replace("-", " ").replace("'", "").strip()
#             serper_dct[sm]["title"] = "".join([ch if (ch.isalnum() or ch==" ") else " " for ch in serper_dct[sm]["title"]])
#             s+=serper_dct[sm]["title"]
#         if "snippet" in serper_dct[sm]:
#             serper_dct[sm]["snippet"] = serper_dct[sm]["snippet"].lower().replace("-", " ").replace("'", "").strip()
#             serper_dct[sm]["snippet"] = "".join([ch if (ch.isalnum() or ch==" ") else " " for ch in serper_dct[sm]["snippet"]])
#             s+=" "+serper_dct[sm]["snippet"]
#         tmp_str+=s+" "
#         serper_lst.append(s.strip())

#     main_terms = main_terms.lower().replace("-", " ").replace("'", "").strip()
#     main_terms = "".join([ch if (ch.isalnum() or ch==" ") else " " for ch in main_terms])
#     tmp_str+=main_terms+" "
#     category = category.lower().replace("-", " ").replace("'", "").strip()
#     category = "".join([ch if (ch.isalnum() or ch==" ") else " " for ch in category])
#     tmp_str+=category+" "

#     title = title.lower().replace("-", " ").replace("'", "").strip()
#     title = "".join([ch if (ch.isalnum() or ch==" ") else " " for ch in title])
#     tmp_str+=title+" "
#     desc = desc.lower().replace("-", " ").replace("'", "").strip()
#     desc = "".join([ch if (ch.isalnum() or ch==" ") else " " for ch in desc])
#     tmp_str+=desc

#     tmp_str=set(tmp_str.split())

#     stopWords = set(nltk.corpus.stopwords.words("english"))
#     stopWords = stopWords.union(set(our_stop_words))
#     tmp_str = set([word for word in tmp_str if (not word.isnumeric()) and (len(word)>1) and (word not in stopWords)])
    
#     ky_dct = defaultdict(int)
#     imp_ky = defaultdict(int)

#     for w in tmp_str:
#         kywrd_score_dct = defaultdict(int)
#         kywrd_score_dct["keyword"] = w
#         if w in domain:
#             ky_dct[w]+=config.domain_score
#             kywrd_score_dct["domain_score"] = config.domain_score

#         for w1 in (title.split()+desc.split()):
#             if w1.startswith(w):
#                 ky_dct[w]+=config.title_desc_score
#                 kywrd_score_dct["title_desc_score"] = config.title_desc_score
#                 break
#         # for w1 in desc.split():
#         #     if w1.startswith(w):
#         #         ky_dct[w]+=config.title_desc_score
#         #         break
#         for w1 in category.split():
#             if w1.startswith(w):
#                 ky_dct[w]+=config.yp_category_score
#                 kywrd_score_dct["yp_category_score"] = config.yp_category_score
#                 break
        
#         cnt = 0
#         for smlr in similar_lst:
#             for w1 in smlr.split():
#                 if w1.startswith(w):
#                     cnt+=1
#                     break
#         if math.floor(len(similar_lst)/2)<=cnt:
#             ky_dct[w]+=config.sl_similar_score
#             kywrd_score_dct["sl_similar_score"] = config.sl_similar_score

#         for srpr in serper_lst:
#             for w1 in srpr.split():
#                 if w1.startswith(w):
#                     ky_dct[w]+=config.google_results_score
#                     kywrd_score_dct["google_results_score"] += config.google_results_score
#                     break
        
#         for w1 in main_terms.split():
#             if w1.startswith(w):
#                 ky_dct[w]+=config.sl_main_terms_score
#                 kywrd_score_dct["sl_main_terms_score"] = config.sl_main_terms_score
#                 break
        
#         all_keywords_score.append(kywrd_score_dct)
        
#         if ky_dct[w]>=config.imp_keyword_score_threshold:
#             imp_ky[w] = ky_dct[w]
#     # print(ky_dct)
#     # print(imp_ky)
#     imp_ky1 = [key for key in imp_ky]

#     for i in range(len(imp_ky1)):
#         for j in range(i+1, len(imp_ky1)):
#             tmp_key1 = imp_ky1[i]
#             tmp_key2 = imp_ky1[j]

#             if (len(tmp_key1.split())==len(tmp_key2.split())) and (tmp_key1.startswith(tmp_key2) or tmp_key2.startswith(tmp_key1)) and (abs(len(tmp_key1)-len(tmp_key2))<=2):
#                 dlt = tmp_key1
#                 if len(tmp_key1)<len(tmp_key2):
#                     dlt = tmp_key2
                
#                 if dlt in imp_ky:
#                     del imp_ky[dlt]
    
#     # for tmp_key1 in imp_ky1:
#     #     for tmp_key2 in imp_ky1:
#     #         if (len(tmp_key1.split())==len(tmp_key2.split())) and (tmp_key1.startswith(tmp_key2) or tmp_key2.startswith(tmp_key1)) and (abs(len(tmp_key1)-len(tmp_key2))<=2):
#     #             dlt = tmp_key1
#     #             if len(tmp_key1)<len(tmp_key2):
#     #                 dlt = tmp_key2
                
#     #             if dlt in imp_ky:
#     #                 del imp_ky



#     terms = set()

    
#     terms = terms.union(get_substr(title, imp_ky))
#     terms = terms.union(get_substr(desc, imp_ky))
#     terms = terms.union(get_substr(category, imp_ky))
#     terms = terms.union(get_substr(main_terms, imp_ky))

#     for sm in similar:
#         if "title" in sm:
#             terms = terms.union(get_substr(sm["title"], imp_ky))
#         if "desc" in sm:
#             terms = terms.union(get_substr(sm["desc"], imp_ky))




#     for sm in similar:
#         if "title" in sm:
#             terms = terms.union(get_substr(sm["title"], imp_ky))
        
#         if "desc" in sm:
#             terms = terms.union(get_substr(sm["desc"], imp_ky))

#     for sm in serper_dct:
#         if "title" in serper_dct[sm]:
#             terms = terms.union(get_substr(serper_dct[sm]["title"], imp_ky))
#         if "snippet" in serper_dct[sm]:
#             terms = terms.union(get_substr(serper_dct[sm]["snippet"], imp_ky))    

#     term_dict = defaultdict(int)
#     imp_terms = defaultdict(int)
#     for w in terms:
#         trm_score_dct = defaultdict(int)
#         trm_score_dct["term"] = w

#         if w.replace(" ", "").replace("-", "") in domain.replace("-", ""):
#             term_dict[w]+=config.domain_score
#             trm_score_dct["domain_score"] = config.domain_score

#         if w in (title+desc):
#             term_dict[w]+=config.title_desc_score
#             trm_score_dct["title_desc_score"] = config.title_desc_score
#         # for w1 in (title.split()+desc.split()):
#         #     if w1.startswith(w):
#         #         ky_dct[w]+=config.title_desc_score
#         #         break
#         # for w1 in desc.split():
#         #     if w1.startswith(w):
#         #         ky_dct[w]+=config.title_desc_score
#         #         break
#         # for w1 in category.split():
#         #     if w1.startswith(w):
#         #         ky_dct[w]+=config.yp_category_score
#         #         break
#         if w in category:
#             term_dict[w]+=config.yp_category_score
#             trm_score_dct["yp_category_score"] = config.yp_category_score

        
#         for smlr in similar:
#             f = True
#             if ("title" in smlr) and (w in smlr["title"]):
#                 f = False
#                 term_dict[w]+=config.sl_similar_score_numerator/len(similar)
#                 trm_score_dct["sl_similar_score"] += config.sl_similar_score_numerator/len(similar)


#             if f and ("desc" in smlr) and (w in smlr["desc"]):
#                 term_dict[w]+=config.sl_similar_score_numerator/len(similar)
#                 trm_score_dct["sl_similar_score"] += config.sl_similar_score_numerator/len(similar)

        
#         for srpr in serper_dct:
#             f = True
#             if ("title" in srpr) and (w in srpr["title"]):
#                 f = False
#                 term_dict[w]+=config.google_results_score
#                 trm_score_dct["google_results_score"] += config.google_results_score


#             if f and ("snippet" in srpr) and (w in srpr["snippet"]):
#                 term_dict[w]+=config.google_results_score
#                 trm_score_dct["google_results_score"] += config.google_results_score



#         if w in main_terms:
#             term_dict[w]+=config.sl_main_terms_score
#             trm_score_dct["sl_main_terms_score"] = config.sl_main_terms_score

        
#         for kwrd in keywords:
#             if kwrd.lower() in w.lower():
#                 term_dict[w]+=config.per_keywords_score
#                 trm_score_dct["bonus_score"] += config.per_keywords_score

#         all_terms_score.append(trm_score_dct)
#         if term_dict[w]>=config.imp_keyword_score_threshold:
#             imp_terms[w] = term_dict[w]
    
#     imp_terms1 = [key for key in imp_terms]

#     for i in range(len(imp_terms1)):
#         for j in range(i+1, len(imp_terms1)):
#             tmp_key1 = imp_terms1[i]
#             tmp_key2 = imp_terms1[j]

#             if (len(tmp_key1.split())==len(tmp_key2.split())) and (tmp_key1.startswith(tmp_key2) or tmp_key2.startswith(tmp_key1)) and (abs(len(tmp_key1)-len(tmp_key2))<=2):
#                 dlt = tmp_key1
#                 if len(tmp_key1)<len(tmp_key2):
#                     dlt = tmp_key2
                
#                 if dlt in imp_terms:
#                     del imp_terms[dlt]
    
#     # print(term_dict)
#     # print(imp_terms)

#     final_ky1 = sorted(zip(imp_ky.values(), imp_ky.keys()), reverse=True)
#     final_ky = []
#     # for i in range(min(5, len(final_ky))):
#     #     final_ky[final_ky1[i][1]] = final_ky1[i][0]

#     for i in range(min(15, len(final_ky1))):
#         tmp_lst = []
#         tmp_lst.append(final_ky1[i][1])
#         tmp_lst.append(final_ky1[i][0])
#         final_ky.append(tmp_lst)

#     final_terms1 = sorted(zip(imp_terms.values(), imp_terms.keys()), reverse=True)
#     final_terms = []
#     # for i in range(min(5, len(final_ky))):
#     #     final_ky[final_ky1[i][1]] = final_ky1[i][0]

#     for i in range(min(15, len(final_terms1))):
#         tmp_lst = []
#         tmp_lst.append(final_terms1[i][1])
#         tmp_lst.append(final_terms1[i][0])
#         final_terms.append(tmp_lst)

#     # print(final_ky)
#     # print(final_terms)

#     return {"imp_keywords": final_ky, "imp_terms": final_terms}
    