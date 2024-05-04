from collections import defaultdict
import os 
dir_path = os.path.dirname(os.path.realpath(__file__))

TERMS_FILE = dir_path + "\\terms_domains.txt"
exception_words = ["the", "a", "by", "and", "for"]


def get_terms():
    with open(TERMS_FILE, "r") as f:
        return [term.strip().replace("\n", "") for term in f.readlines()]


def get_match(term, s, i):
    
    k=0
    for j in range(i, len(s)):
        if s[j].lower() == term[k].lower():
            k+=1
        elif (s[j] == " ") or (s[j] == "-"):
            continue
        else:
            return False
        
        if (k==len(term)):
            if ((j+1==len(s)) or (not s[j+1].isalnum())):
                return s[i:j+1]
            else:
                return False
    
    return False


def merge(spaced_term, capitalized_term):
    capitalized_term = capitalized_term.replace(" ", "")
    ans = ""
    j=0
    for i in range(len(spaced_term)):
        if spaced_term[i]==" ":
            ans+=" "
        else:
            ans+=capitalized_term[j]
            j+=1
    return ans


def get_result_term(term, s):
    while '-' in s:
        s = s.replace('-', ' ')
    
    while '  ' in s:
        s = s.replace('  ', ' ')
    
    # if term.lower() in s.lower():
    #     print(term, "\n", s)
    matches = defaultdict(int)
    spaced_dict = defaultdict(int)
    capped_dict = defaultdict(int)
    # print(s)
    for i in range(len(s)):
        if s[i].lower()==term[0].lower():
            match = get_match(term, s, i)
            if match:
                # print(match)
                matches[match] +=1
                if " " in match:
                    spaced_dict[match] = match.count(" ")
                
                if any(ch.isupper() for ch in match):
                    capped_dict[match] = len([ch for ch in match if ch.isupper()])
                

    # print(spaced_dict)
    # print(capped_dict)
    spaced_term = ""
    capped_term = ""

    if len(list(spaced_dict.keys()))>0:
        spaced_term = max(spaced_dict.keys(), key = lambda ky: spaced_dict[ky])
    
    if len(list(capped_dict.keys()))>0:
        capped_term = max(capped_dict.keys(), key = lambda ky: capped_dict[ky])
    
    # print("terms", spaced_term, capped_term)

    ans = ""
    if spaced_term and capped_term:
        ans = merge(spaced_term, capped_term.replace(" ", ""))

    elif spaced_term or capped_term:
        ans = spaced_term+capped_term
    
    return ans
    # print(matches)
    
    # for key in matches.keys():
    #     matches[key] = [matches[key]]
    #     matches[key].append(key.count(" "))
    #     matches[key].append(len([letter for letter in key if letter.isupper()]))
    
    # # print(matches)
    # if len(list(matches.keys()))>0:
    #     mx = max(matches.keys(), key = lambda ky: matches[ky])
    #     # print(mx)
    #     return mx
    
    # return False



def exception_words_processing(term):
    for word in exception_words:
        if word.lower() in term.lower():
            term_list = term.split()
            for i in range(len(term_list)):
                if term_list[i]==word:
                    term_list[i] = term_list[i][0].upper() + term_list[i][1:]

                    if i>0:
                        term_list[i-1] = term_list[i-1][0].upper() + term_list[i-1][1:]
                    
                    if i<len(term_list)-1:
                        term_list[i+1] = term_list[i+1][0].upper() + term_list[i+1][1:]
                    
            term = " ".join(term_list)
    return term


def capitalize(term, capitalized_term):
    ans = ""
    i=0
    j=0

    while i<len(term):
        if (j<len(capitalized_term)) and (term[i].lower()==capitalized_term[j].lower()):
            ans+=capitalized_term[j]
            i+=1
            j+=1
        else:
            ans+=term[i].lower()
            i+=1
    
    return ans
    # for c in term:
    #     if (i==len(capitalized_term)) or (not c.isalnum()):
    #         ans+=c
    #     else:
    #         ans+=capitalized_term[i]
    #         i+=1


def reshape_terms(terms, sz):
    ans = []
    start = 0
    end = sz
    
    while True:
        ans.append(terms[start : min(end, len(terms))])

        if end>=len(terms):
            break

        start = end
        end+=sz
    
    return ans