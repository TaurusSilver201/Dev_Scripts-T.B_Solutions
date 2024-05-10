import csv
import json
import httpx
import requests
import random
from concurrent.futures import ThreadPoolExecutor
from tenacity import retry
from collections import defaultdict
from datetime import datetime
import os
import requests

dir_path = os.path.dirname(os.path.realpath(__file__))
# from utils import (
#     get_proxies,
#     get_terms,
#     get_ignored_words
# )
try:
    # from .utils import *
    from . import config
    from . import utils
except:
    # from utils import *
    import config
    import utils

from time import sleep
# import config
from fake_useragent import UserAgent

# BASE_URL = "https://search-api.trademarkia.com/api/basic/us1"
BASE_URL = "https://search-api.trademarkia.com/api/v2/us"
results = defaultdict(str)
max_retries = config.max_retries
retries = defaultdict(int)
page_limit = config.page_limit
page_result_limit = config.page_result_limit
start_with_result_score = config.start_with_result_score
threads = config.threads
clients = []
proxies = []
ignored_words = []
no_of_rows = 10

@retry
def search_term(term):
    print("TM retry", term, retries[term])
    retries[term]+=1
    if retries[term]>max_retries:
        return ""
    term_results = defaultdict(list)

    term2 = term
    if "-" in term:
        term2 = term2.replace("-", " ")
        term2 = ''.join(ch for ch in term2 if ((ch.isalnum()) or (ch==" ")))
    else:
        term2 = ''.join(ch for ch in term2 if ch.isalnum())
    term2 = term2.lower()
    
    for i in range(page_limit):
        print("TM Searching for term : ", term, "page : ", i+1)
        # proxy_ = proxies[(random.randrange(len(proxies)))]
        # print(proxy_)
        # proxy = {
        #     "http://": proxy_
        # }
        # headers = {
        #     'user-agent': UserAgent().random
        # }
        # url = BASE_URL
        # url += "?rows=10"
        # url += "&input_query=" + term.replace(" ", "+")
        # url += "&filing_date=-1406419200,1681744927"
        # url += "&page="+str(i+1)
        # url += "&sort_by=status_date"
        # url += "&sort_asc=false"
        # url += "&status=all"
        # url += "&exact_match=false"
        # url += "&date_query=false"
        json_data = {
            'input_query': term,
            'date_query': False,
            'registration_date': [],
            'filing_date': [
                -1406419201,
                1690559787,
            ],
            'status_date': [],
            'owners': [],
            'attorneys': [],
            'law_firms': [],
            'status': [
                'all',
            ],
            'classes': [],
            'page': i+1,
            'is_search_report': False,
            'search_report': [],
        }

        data = ""
        res_tm = ""
        if os.path.isfile(config.paid_api_results_folder+"zenrows-tm-"+term+str(i+1)+".txt"):
            print("result for "+term+" found in paid_api_results/zenrows-tm-"+term+str(i+1)+".txt")
            text_file = open(config.paid_api_results_folder+"zenrows-tm-"+term+str(i+1)+".txt", "r")
            res_tm = text_file.read()
            text_file.close()
        
        if len(res_tm)==0:
            print("result for "+term+" not found in paid_api_results/zenrows-tm")
                            
            proxy = config.zenrows_proxy
            proxies = {"http": proxy, "https": proxy}
            # sleep(random.uniform(config.delay_range[0], config.delay_range[1]))
            # res = requests.get(url, proxies=proxies, verify=False)
            # res_ow = res.text
            # print(res_ow)
            # with open(config.paid_api_results_folder+"zenrows-ow-"+domain+".txt", "w") as f:
            #     f.write(res_ow)
        
            # print(res_ow)        
            # soup = BeautifulSoup(res_ow, 'html.parser')
            # with httpx.Client(headers=headers, proxies=proxy) as client:
            sleep(random.uniform(config.delay_range[0], config.delay_range[1]))
            r = requests.post(BASE_URL, proxies=proxies, verify=False, json=json_data)
            res_tm = r.text
            # print(res_ow)
            with open(config.paid_api_results_folder+"zenrows-tm-"+term+str(i+1)+".txt", "w") as f:
                f.write(res_tm)
            # r.raise_for_status()
        data = json.loads(res_tm)
        # print(data)
        if ('body' in data.keys()) and ('data' in data['body'].keys()):
            # print(True)
            data = data['body']['data']
            # print(len(data))
        else:
            # print(False)
            break

        page_names = []
        for row in data:
            # print(row)
            # name = row["mark_identification"][0].lower().strip()
            name = row["mark_identification"].lower().strip()

            owner = ""
            if "current_owner" in row.keys():
                owner = row["current_owner"].lower().strip()
            # if "current_owner" in row.keys():
            #     owner = row["current_owner"][0].lower().strip()
            # if "owners_name" in row.keys():
            #     owner = row["owners_name"][0].lower().strip()
            # print(name, owner)
            for ignored_word in ignored_words:
                # print(ignored_word)
                name = name.replace(ignored_word, "").strip()
                owner = owner.replace(ignored_word, "").strip()
                
            if "-" in term:
                name = name.replace("-", " ")
                name = ''.join(ch for ch in name if ((ch.isalnum()) or (ch==" ")))
            else:
                name = ''.join(ch for ch in name if ch.isalnum())
            owner = ''.join(ch for ch in owner if ch.isalnum())
            # print(name, owner)

            page_names.append(name)

            if owner:
                term_results[owner].append(name)

        if len(data)<no_of_rows:
            break

        good_results = 0
        for name in page_names:
            if name.startswith(term2):
                good_results+=1
        # print("good_results", good_results)
        if good_results<page_result_limit:
            break

    score = 0
    # print(term_results, term2)
    for owner in term_results:
        if term2 in term_results[owner]:
            score+=1
        elif any((name.startswith(term2) or name.startswith("the"+term2)) for name in term_results[owner]):
            score+=start_with_result_score
    
    print("TM Score of term ", term, score)

    if score==0:
        score=""
    
    return score

def main(data):
    if (data) and ("TERMS_FILE" in data.keys()):
        utils.TERMS_FILE = data["TERMS_FILE"]
    terms = utils.get_terms()
    global proxies
    proxies = utils.get_proxies()
    global ignored_words
    ignored_words = utils.get_ignored_words()

    # terms = ["tea for two"]
    results = []
    executor = ThreadPoolExecutor(max_workers=threads)
    for result in executor.map(search_term, terms):
        results.append(result)

    # for term in terms:
    #     results.append(search_term(term))

    today = datetime.today()
    with open(f"{dir_path}\\TM_report_{today.strftime('%Y%d%m_%H%M%S')}.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["term", "TM"])
        writer.writerows([[terms[i], results[i]] for i in range(len(terms))])
    return results

if __name__ == "__main__":
    main({})
