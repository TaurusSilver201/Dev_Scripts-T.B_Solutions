from collections import defaultdict
from tldextract import extract
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
import csv
import http.client
import json
import re
from unidecode import unidecode
from tenacity import retry
import os 
dir_path = os.path.dirname(os.path.realpath(__file__))

# import utils
# (
#         get_terms,
#         get_match,
#         get_result_term,
#         exception_words_processing,
#         merge,
#         capitalize
#     )
try:
    # from .utils import *
    from . import utils
except:
    # from utils import *
    import utils

domain_start_words = ["the", "get"]
threads = 5
max_retries = 5
retries = defaultdict(int)

@retry
def process_term(term):
    print("Kwbreaker Processing term :", term, "retry : ", retries[term])
    if retries[term]>max_retries:
        print("kwbreaker", term, term, 0)
        return (term, term, 0)
    
    retries[term]+=1

    o_term = term
    term = term.split(".")[0]
    final_term = ""
    score = 0
    if "-" in term:
        final_term = term.replace("-", " ").title()
    elif any(char.isnumeric() for char in term):
        final_term = re.sub('(\d+(\.\d+)?)', r' \1 ', term)
        final_term = final_term.strip().title()
    else:
        # results = api(term)
        conn = http.client.HTTPSConnection("google.serper.dev")
        payload = json.dumps({
            "q": term,
            "gl": "us",
            "hl": "en",
            "autocorrect": False
        })
        headers = {
            'X-API-KEY': 'c9df3b772a1a9e6eecab51ac1e386a6b1afef530',
            'Content-Type': 'application/json'
        }
        conn.request("POST", "/search", payload, headers)
        res = conn.getresponse()
        data = res.read()
        # with open("test.html", "w") as f:
        #     f.write(data.decode("utf-8"))
        results = json.loads(data.decode("utf-8"))
        # print(results)
        results = results["organic"]
        spaced_terms = defaultdict(int)
        capitalized_terms = defaultdict(lambda: [0, 0])
        normal_terms = []
        for result in results:
            cap_score = 0
            if result["link"]:
                # print(result["link"])
                tsd, td, tsu = extract(result["link"])
                domain = td + '.' + tsu
                domain = domain.replace("-", "")
                # print("LLiinnkk", result["link"], result["link"].split("."+tsu)[1])
                if (domain.lower().startswith(term.lower())) or any(domain.lower().startswith(tmp1.lower()+term.lower()) for tmp1 in domain_start_words):
                    score+=1
                    if len(result["link"].split("."+tsu)[1])<=1:
                        cap_score=2
                    else:
                        cap_score=1
                elif len(result["link"].split("."+tsu)[1])<=1:
                    # print(result["link"].split("."+tsu)[1], result["title"])
                    tmp_term = "".join([ch for ch in term if ch.isalnum()])
                    tmp_title = "".join([ch for ch in unidecode(result["title"]) if ch.isalnum()])
                    
                    if tmp_title.lower().startswith(tmp_term.lower()):
                        score+=1
                # print(domain)
            title_snip = result["title"]+" " +result["snippet"]
            title_snip = unidecode(title_snip)
            title_snip = title_snip.replace("&", " And ")
            title_snip = "".join([ch for ch in title_snip if ((ch.isalnum()) or (ch==" ") or (ch=="-"))])
            result_term = utils.get_result_term(term, title_snip)
            # print(result["link"], result_term)
            # print(title_snip, "\n")
            # print(result_term)
            if result_term:
                if " " in result_term:
                    spaced_terms[result_term.lower()]+=1
                
                if any(letter.isupper() for letter in result_term):
                    capitalized_terms[result_term.replace(" ", "")][0]+=1
                    capitalized_terms[result_term.replace(" ", "")][1]+=cap_score
                
                if not(" " in result_term) and not(any(letter.isupper() for letter in result_term)):
                    normal_terms.append(result_term)

        for key in spaced_terms.keys():
            spaced_terms[key] = [spaced_terms[key]]
            spaced_terms[key].append(key.count(" "))
        
        for key in capitalized_terms.keys():
            # capitalized_terms[key] = [capitalized_terms[key]]
            capitalized_terms[key].append(len([letter for letter in key if letter.isupper()]))
        
        # print(spaced_terms)
        # print(capitalized_terms)
        popular_spaced_term = ""
        if len(list(spaced_terms.keys()))>0:
            popular_spaced_term = max(spaced_terms.keys(), key = lambda ky: spaced_terms[ky])
        
        popular_capitalized_term = ""
        if len(list(capitalized_terms.keys()))>0:
            popular_capitalized_term = max(capitalized_terms.keys(), key = lambda ky: capitalized_terms[ky])
            if (len(popular_capitalized_term)>5) and (popular_capitalized_term.isupper()) and (len(list(capitalized_terms.keys()))>1):
                del capitalized_terms[popular_capitalized_term]
                popular_capitalized_term = max(capitalized_terms.keys(), key = lambda ky: capitalized_terms[ky])

        
        # print(popular_spaced_term, popular_capitalized_term)

        if popular_spaced_term and popular_capitalized_term:
            final_term = utils.merge(popular_spaced_term, popular_capitalized_term)
        elif popular_spaced_term or popular_capitalized_term:
            final_term = popular_spaced_term + popular_capitalized_term
        elif len(normal_terms)>0:
            final_term = normal_terms[0]
        else:
            final_term = term
    # print(final_term)
    final_term = utils.exception_words_processing(final_term)
    final_term = final_term.split(" ")
    for i in range(len(final_term)):
        if not any(ch.isupper() for ch in final_term[i]):
            final_term[i] = final_term[i].title()
    final_term = " ".join(final_term)
    o_term = utils.capitalize(o_term, final_term.replace(" ", ""))
    print("kwbreaker", o_term, final_term, score)
    return (o_term, final_term, score)

def main():
    terms = utils.get_terms()
    # terms = ["achieves.com", "ilearn.net", "upsys", "overexposed"]
    # terms = [term.split(".")[0] for term in terms]
    # terms = ["weinundfein.com"]
    results = []
    executor = ThreadPoolExecutor(max_workers=threads)
    for result in executor.map(process_term, terms):
        results.append(result)

    today = datetime.today()
    with open(f"{dir_path}\\kwbreaker_report_{today.strftime('%Y%d%m_%H%M%S')}.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["term", "final_term", "score"])
        writer.writerows(results)
    return results

if __name__ == "__main__":
    main()
