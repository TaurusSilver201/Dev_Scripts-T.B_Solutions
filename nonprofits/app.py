import pdb

try:
    from . import utils
except:
    import utils
import requests
from bs4 import BeautifulSoup
from requests_ntlm import HttpNtlmAuth
import csv
import time
from itertools import cycle
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
import atexit
import os
import re
import random

MAX_THREADS = 5  # Adjust the number of threads based on your needs
OPREATOR = ""
dir_path = os.path.dirname(os.path.realpath(__file__))

def is_camel_case(input_str):
    # Check if the string is not empty
    if not input_str:
        return False
    
    # Check if the first letter is a capital letter
    if not input_str[0].isupper():
        return False
    
    # Check if there are no spaces in the string
    if ' ' in input_str:
        return False
    

    words = input_str.split()
    if all(word.isupper() for word in words):
        return False
    

    # Check if the rest of the string has only lowercase letters
    if any(char.isupper() for char in input_str[2:]):
        return True
    
    # If all conditions are met, return True
    return False

def get_proxies_from_file(file_path):
    with open(file_path, 'r') as file:
        proxies = [line.strip() for line in file if line.strip()]
    return cycle(proxies)

def parse_proxy(proxy):
    data = proxy.split('@')[0].replace('http://','').split(':')
    username, password = data[0], data[1]
    return username, password

def match_term(term, title):
    global OPREATOR
    if title:
        term_words = term.split(' ')
        if len(term_words) == 1:
            return term.lower() == title.split(' ')[0].lower()
        else:
            OPREATOR = "*"
            flag = term.lower() == "".join(_ for _ in title)[:2].lower()
            if not flag:
                term = term.replace(' ', '')
                OPREATOR = "+"
                return term.lower() == title.split(' ')[0].lower()
            return flag
    return False

def search_propublica(term, proxies):
    count = 0
    revenue = 0

    for i in range(1, 6):  # Iterate over the first 5 pages
        base_url = f"https://projects.propublica.org/nonprofits/search?page={i}"
        #term = term.replace(' ', '+')
        search_url = f'{base_url}&q="{term}"'

        # Get the next proxy from the iterator
        proxy = proxies[random.randrange(0, len(proxies))]
        proxy_username, proxy_password = parse_proxy(proxy=proxy)
        proxie = {
            'http': f'{proxy}',
            'https': f'{proxy}'
        }
        auth = HttpNtlmAuth(proxy_username, proxy_password)
        try:
            response = requests.get(search_url, proxies=proxie, auth=auth)
            response.raise_for_status()  # Raise HTTPError for bad responses
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                results = soup.find_all('div', {'class': 'result-item'})
                if results:  # Check if results are not empty
                    for nonprofits_tab_headings in results:
                        title = nonprofits_tab_headings.find('div', {'class': 'result-item__hed'}).text.strip()
                        description = nonprofits_tab_headings.find('div', {'class': 'text-sub'}).text.strip()
                        if title.lower().startswith(term.lower()) or description.lower().startswith(term.lower()):
                            rev = nonprofits_tab_headings.select_one('.result-item-flex .metrics-wrapper .font-weight-500').get_text(strip=True).replace(',', '').replace('$', '')
                            revenue += int(rev) if not rev == 'N/A' else 0
                            count += 1
                        elif title.lower().startswith("the " + term.lower()) or description.lower().startswith("the " + term.lower()):
                            rev = nonprofits_tab_headings.select_one('.result-item-flex .metrics-wrapper .font-weight-500').get_text(strip=True).replace(',', '').replace('$', '')
                            revenue += int(rev) if not rev == 'N/A' else 0
                            count += 1 
                    print(f"{term} is scraping ({i}/5)")
                else:
                    print(f"No results found on page {i} for {term}")
                    break  # No need to try the same page again
            else:
                print(f"Error: Unable to fetch data. Status code: {response.status_code} for page {i}")
        except requests.exceptions.RequestException as e:
            print(f"Error: {e}")
            # Move to the next proxy on exception
            continue

    return [count, revenue]

def close_file():
    file.close()

def fetch_data(term):
    is_camel = is_camel_case(term)
    if is_camel and '-' not in term:
        term1 = ''.join(re.sub('([A-Z][a-z]+)', r' \1', re.sub('([A-Z]+)', r' \1', term)).split())
        term2 = ' '.join(re.sub('([A-Z][a-z]+)', r' \1', re.sub('([A-Z]+)', r' \1', term)).split())
        count1, rev1 = search_propublica(term1.strip(), proxies)
        count2, rev2 = search_propublica(term2.strip(), proxies)
        count = count1 + count2
        revenue = rev1 + rev2
        result = f"{count}--(${round(revenue / 1000000, 1)}m)"
    elif ' ' in term:
        term1 = term 
        term2 = term.replace(' ','')
        count1, rev1 = search_propublica(term1.strip(), proxies)
        count2, rev2 = search_propublica(term2.strip(), proxies)
        count = count1 + count2
        revenue = rev1 + rev2
        result = f"{count}--(${round(revenue / 1000000, 1)}m)"
    elif '-' in term:
        term1 = term.replace('-', ' ').strip()
        count, rev  = search_propublica(term1.strip(), proxies)
        result = f"{count}--(${round(rev / 1000000, 1)}m)"
    else:
        count, rev  = search_propublica(term.strip(), proxies)
        result = f"{count}--(${round(rev / 1000000, 1)}m)"
    if not result:
        result = f"0--$0m"

    return [term, result]

def main(data):
    if (data) and ("TERMS_FILE" in data.keys()):
        utils.TERMS_FILE = data["TERMS_FILE"]

    terms = utils.get_terms()
    global proxies, date_time
    proxies = utils.get_proxies()
    date_time = datetime.now()

    today = datetime.today()
    file_name = f"{dir_path}/nonprofits_{today.strftime('%Y%d%m_%H%M%S')}"
    global file
    file = open(f'{file_name}.csv', 'w', newline='')
    global csv_writer
    csv_writer = csv.writer(file)
    csv_writer.writerow(['term', 'value'])
    
    atexit.register(close_file)

    results_data = []  # To store the results data

    def process_term(term):
        term_, result = fetch_data(term)
        csv_writer.writerow([term_, result])
        lst = []
        lst.append(term_)
        lst.append(result)
        results_data.append(lst)
    
    with ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
        executor.map(process_term, terms)


    return results_data

if __name__ == '__main__':
    main({})

    print("Completed...")
