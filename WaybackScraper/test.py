import requests
from bs4 import BeautifulSoup
import concurrent.futures
import datetime
import random
import time
import csv  
from config import DOMAINS_FILE, NUM_THREADS, PROXIES_FILE
from sumy.parsers.html import HtmlParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer

def read_domains(filename):
    with open(filename, 'r') as file:
        return file.read().splitlines()

def read_proxies(filename):
    with open(filename, 'r') as file:
        proxies = file.read().splitlines()
        return [proxy.split(':') for proxy in proxies]

def get_current_date():
    return datetime.datetime.now().strftime("%Y%m%d")

def get_previous_date(years):
    current_date = datetime.datetime.now()
    previous_date = current_date - datetime.timedelta(days=years*365)
    return previous_date.strftime("%Y%m%d")

def fetch_snapshot(domain, snapshot_date, proxy):
    proxy_url = f"http://{proxy[2]}:{proxy[3]}@{proxy[0]}:{proxy[1]}"
    url = f"http://web.archive.org/web/{snapshot_date}/{domain}"

    try:
        response = requests.get(url, proxies={"http": proxy_url})
        soup = BeautifulSoup(response.text, 'html.parser')
        
        redirection = "yes" if is_redirection(soup) else ""
        
        if is_good_snapshot(soup):
            title = soup.title.string.strip() if soup.title else ""
            desc = soup.find('meta', attrs={'name': 'description'})['content'].strip() if soup.find('meta', attrs={'name': 'description'}) else ""
            kw = soup.find('meta', attrs={'name': 'keywords'})['content'].strip() if soup.find('meta', attrs={'name': 'keywords'}) else ""
            content_summary = summarize_homepage_content(url)
        else:
            title = desc = kw = content_summary = ""

        return domain, title, desc, kw, content_summary, snapshot_date, redirection
    except Exception as e:
        print(f"Error scraping {url}: {e}")
        return domain, "", "", "", "", "", ""

def is_good_snapshot(soup):
    return soup.find('div', {'id': 'error404'}) is None

def is_redirection(soup):
    redirection_tag = soup.find('div', {'id': 'wm-ipp-base'})
    return redirection_tag is not None

def summarize_homepage_content(url, num_sentences=3):
    parser = HtmlParser.from_url(url, Tokenizer('english'))
    summarizer = LsaSummarizer()
    summary = summarizer(parser.document, num_sentences)
    return ' '.join(str(sentence) for sentence in summary)

def main():
    domains = read_domains(DOMAINS_FILE)
    proxies = read_proxies(PROXIES_FILE)

    current_date = get_current_date()
    previous_dates = [get_previous_date(years) for years in [1, 2.5, 4]]

    snapshot_date_options = [current_date] + previous_dates

    current_datetime = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"output_{current_datetime}.csv"

    with concurrent.futures.ThreadPoolExecutor(max_workers=NUM_THREADS) as executor:
        futures = []
        for domain in domains:
            for snapshot_date in snapshot_date_options:
                proxy = random.choice(proxies)
                futures.append(executor.submit(fetch_snapshot, domain, snapshot_date, proxy))

        with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['domain', 'title', 'desc', 'kw', 'content_summary', 'date', 'redirection']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            for future in concurrent.futures.as_completed(futures):
                snapshot_data = future.result()
                if snapshot_data[1]:  # Check if title is not empty
                    writer.writerow({
                        'domain': snapshot_data[0],
                        'title': snapshot_data[1],
                        'desc': snapshot_data[2],
                        'kw': snapshot_data[3],
                        'content_summary': snapshot_data[4],
                        'date': snapshot_data[5],
                        'redirection': snapshot_data[6]
                    })

if __name__ == "__main__":
    main()
