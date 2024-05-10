import pdb

try:
    from .config import wait_time, delay_between_terms
    from .utils import get_terms
except:
    from config import wait_time, delay_between_terms
    from utils import get_terms

try:
    # from .utils import *
    from . import config
    from . import utils
except:
    # from utils import *
    import utils
    import config
from warnings import filterwarnings

filterwarnings('ignore')
import re, csv
from time import sleep
from datetime import datetime
import os
import requests
import json
import random
import logging
from concurrent.futures import ThreadPoolExecutor


logging.basicConfig(format='%(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)
dir_path = os.path.dirname(os.path.realpath(__file__))
results_final = []



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


def find_numbers(text):
    """
    Function to find the numbers from the given text

    input:
        123,000 results

    output:
        123000
    """
    try:
        return int(
            re.findall(r'[-]?[0-9]+[0-9]?[0-9]?[0-9]?[,]?[0-9]?[0-9]?[0-9]?[,]?[0-9]?[0-9]?[0-9]?', text)[0].replace(
                ',', ''))
    except:
        return 0


def write_csv(data, output_file):
    with open(output_file, 'a', newline='', encoding='utf-8') as outfile:
        writer = csv.writer(outfile)
        writer.writerow(data)

def get_json(response):
    return json.loads(response.text)


def get_request(term, retries=3):
    try:
        proxies = utils.get_proxies()
        proxy_string = proxies[random.randrange(0, len(proxies))]

        headers = {
            'authority': 'www.crunchbase.com',
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 OPR/105.0.0.0',
            'x-cb-client-app-instance-id': '27312099-2d14-4d28-a1af-5ccb4db77652',
            'x-requested-with': 'XMLHttpRequest',
        }

        params = {
            'query': f'"{term}"',
            'collection_ids': 'organizations',
            'limit': '25',
            'source': 'topSearch',
        }

        proxy = {
            'http': proxy_string,
            'https': proxy_string
        }

        response = requests.get('https://www.crunchbase.com/v4/data/autocompletes', params=params, headers=headers,
                                proxies=proxy, verify=False)

        return response
    except Exception as W:
            print('Exception occured Sleep For Retry: {}'.format(retries))
            sleep(delay_between_terms)
            if retries > 0:
                return get_request(term, retries=retries - 1)


def crawler(term, csv_file, i, total_terms):
    if term.strip() == '':
        return term, 0

    term_count = 0

    logger.info(f"checking term \"{term}\" ({i}/{total_terms}) on CrunchBase.com")


    response = get_request(term)

    if response.status_code != 200:
        response = get_request(term)

    body = get_json(response)

    result_boxes = body['entities']
    for result in result_boxes:
        try:
            title = result['identifier']['value']
            description = result['short_description']
        except IndexError:
            title = ''
            description = ''

        if title.lower().startswith(term.lower()) or description.lower().startswith(term.lower()):
            term_count += 1

        if title.lower().startswith("the " + term.lower()) or description.lower().startswith("the " + term.lower()):
            term_count += 1
    return term_count


def main(data):
    if (data) and ("TERMS_FILE" in data.keys()):
        utils.TERMS_FILE = data["TERMS_FILE"]
    terms = get_terms()
    total_terms = len(terms)
    today = datetime.today()

    csv_file = f"{dir_path}/crunch_base_{today.strftime('%Y%d%m_%H%M%S')}.csv"
    write_csv(['term', 'CB.score'], csv_file)
    results_ = []


    def process_term(term):
        i = terms.index(term) + 1
        term = term.strip()
        #is_camel = any(is_camel_case(trm) for trm in term.split())
        
        is_camel = is_camel_case(term)

        if is_camel and '-' not in term:
            term1 = ''.join(re.sub('([A-Z][a-z]+)', r' \1', re.sub('([A-Z]+)', r' \1', term)).split())
            term2 = ' '.join(re.sub('([A-Z][a-z]+)', r' \1', re.sub('([A-Z]+)', r' \1', term)).split())

            count1 = crawler(term1, csv_file, i, total_terms)


            count2 = crawler(term2, csv_file, i, total_terms)

            count = count1 + count2
            #write_csv([term, count], csv_file)
            lst = []
            lst.append(term)
            lst.append(count)
            results_.append(lst)
        elif ' ' in term:
            term1 = term
            term2 = ''.join(re.sub('([A-Z][a-z]+)', r' \1', re.sub('([A-Z]+)', r' \1', term)).split(' '))

            count1 = crawler(term1, csv_file, i, total_terms)

            count2 = crawler(term2, csv_file, i, total_terms)
            count = count1 + count2
            #write_csv([term, count], csv_file)
            lst = []
            lst.append(term)
            lst.append(count)
            results_.append(lst)
        elif '-' in term:
            term1 = term.replace('-', ' ').strip()
            count1 = crawler(term1, csv_file, i, total_terms)

            #write_csv([term, count], csv_file)
            lst = []
            lst.append(term)
            lst.append(count1)
            results_.append(lst)
        else:
            count = crawler(term, csv_file, i, total_terms)
            #write_csv([term, count], csv_file)
            lst = []
            lst.append(term)
            lst.append(count)
            results_.append(lst)

    with ThreadPoolExecutor(max_workers=4) as executor:
        executor.map(process_term, terms)
    
    for term in terms:
        # Find the count for the term in results_
        count = next((item[1] for item in results_ if item[0] == term), 0)
        write_csv([term, count], csv_file)

    return results_


if __name__ == '__main__':
    main({})

    print("Completed...")