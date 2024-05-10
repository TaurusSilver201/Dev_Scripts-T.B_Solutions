import utils
import config
from collections import defaultdict
import time
from tldextract import extract
import dns.resolver as dnsresolver
import pandas as pd
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
import requests
import json

mode = config.mode
tlds1_threshold = config.tlds1_threshold
full_report = config.full_report
threads = config.threads
delay_range = config.delay_range
timeout = config.timeout
tlds_time_analysis = config.tlds_time_analysis
dns_engines_analysis = config.dns_engines_analysis
whois_taken_threshold = config.whois_taken_threshold
whois_api_key = config.whois_api_key
whois_tlds = utils.get_whois_tlds()
domains = utils.get_domains()
old_domains = utils.get_old_domains()
domains = [domain for domain in domains if domain not in old_domains]
dns_engines = set(utils.get_dns_engines())
dns_in_use = dns_engines.copy()
max_retries = 0
retries = defaultdict(int)
tlds1_list = []
tlds2_list = []
errors = 0


if mode=="smart_check":
    tlds1_list = utils.get_tlds1()
    tlds2_list = utils.get_tlds2()
else:
    tlds1_list = utils.get_tlds()

def get_dns():
    global dns_engines
    global dns_in_use
    # if len(dns_engines)==0:
    #     dns_engines=dns_in_use
    dns = ""
    while dns=="":
        try:
            dns = dns_engines.pop()
        except KeyError:
            pass
            # dns_engines = dns_in_use
    # while True:
        # dns = dns_engines[random.randrange(0, len(dns_engines))]
    # try:
    #     dns = dns_engines.pop()
    # except KeyError:
    #     dns_engines = dns_in_use
    #     return get_dns()

        # if dns not in dns_in_use:
    # dns_in_use.add(dns)
            # dns_in_use.append(dns)
            # break
    return dns

def release_dns(dns):
    if dns:
        global dns_engines
        dns_engines.add(dns)


# @retry
def query_domain(domain, tld, dns1, recheck, tm):
    resolver = dnsresolver.Resolver()
    resolver.timeout = tm
    resolver.lifetime = tm
    # dns1 = dns_engines[random.randrange(0, len(dns_engines))]
    # dns2 = dns1
    # while dns2==dns1:
    #     dns2 = dns_engines[random.randrange(0, len(dns_engines))]
    
    # dns1 = dns1.split(",")
    # dns2 = dns2.split(",")
    # dns = dns1+dns2
    global errors
    # dns = dns.split(",")

    # res = []
    tsd, td, org_tld = extract(domain)
    
    # ips = set()
    # nameservers = set()
    
    
    # for tld in set(tlds_list)-{org_tld}:
    # print("Searching : ", td+"."+tld)

    ans = defaultdict(float)
    if recheck:
        ans["recheck"] = "Yes"
    if not td:
        return ans
    
    dns = dns1
    while dns==dns1:
        release_dns(dns)
        dns = get_dns()
    resolver.nameservers = dns.split(",")
    ans["domain"] = domain

    ans["dns"] = dns
    ans["td"] = td
    ans["tld"] = tld
    start_time = time.time()
    try:
        # time.sleep(random.uniform(config.delay_range[0], config.delay_range[1]))
        result = resolver.resolve(td+"."+tld, 'A')
        # print(type(result))
        ips = set([ip.to_text() for ip in result])
        ans["ips"] = ips
        # print(ips)
        # if full_report:
        # time.sleep(random.uniform(config.delay_range[0], config.delay_range[1]))
        # result = resolver.resolve(td+"."+tld, 'NS')
        # nameservers = set([ns.to_text() for ns in result])
        # ans["nameservers"] = nameservers
        
        # print(nameservers)
        # return True
    except dnsresolver.NXDOMAIN:
        # print("dns.resolver.NXDOMAIN")
        ans["ip.dns.resolver.NXDOMAIN"]+=1
        errors+=1
        # return False
    except dnsresolver.LifetimeTimeout:
        ans["ip.dnsresolver.LifetimeTimeout"]+=1
        errors+=1
        if not recheck:
            release_dns(dns)
            return ans
        # print("timeout")
        # if retries[domain]>=max_retries:
        #     ans["ip.dnsresolver.LifetimeTimeout"]+=1
        # else:
        #     retries[domain]+=1
        #     raise Exception("Exception")
        # return False
    except ValueError:
        # print("value error")
        ans["ip.ValueError"]+=1
        errors+=1
        # return False
    except dnsresolver.NoNameservers:
        # print("dns.resolver.NoNameservers")
        ans["ip.dnsresolver.NoNameservers"]+=1
        errors+=1
        # return False
    except dnsresolver.NoAnswer:
        # print("dns.resolver.NoAnswer")
        ans["ip.dns.resolver.NoAnswer"]+=1
        errors+=1
        # return False
    
    try:
        # time.sleep(random.uniform(config.delay_range[0], config.delay_range[1]))
        # result = resolver.resolve(td+"."+tld, 'A')
        # # print(type(result))
        # ips = set([ip.to_text() for ip in result])
        # ans["ips"] = ips
        # print(ips)
        # if full_report:
        # time.sleep(random.uniform(config.delay_range[0], config.delay_range[1]))
        result = resolver.resolve(td+"."+tld, 'NS')
        nameservers = set([ns.to_text() for ns in result])
        ans["nameservers"] = nameservers
        
        # print(nameservers)
        # return True
    except dnsresolver.NXDOMAIN:
        # print("dns.resolver.NXDOMAIN")
        ans["ns.dns.resolver.NXDOMAIN"]+=1
        errors+=1
        # return False
    except dnsresolver.LifetimeTimeout:
        # print("timeout")
        ans["ns.dnsresolver.LifetimeTimeout"]+=1
        errors+=1
        # return False
    except ValueError:
        # print("value error")
        ans["ns.ValueError"]+=1
        errors+=1
        # return False
    except dnsresolver.NoNameservers:
        # print("dns.resolver.NoNameservers")
        ans["ns.dnsresolver.NoNameservers"]+=1
        errors+=1
        # return False
    except dnsresolver.NoAnswer:
        # print("dns.resolver.NoAnswer")
        ans["ns.dns.resolver.NoAnswer"]+=1
        errors+=1
        # return False
    
    ans["time"] = time.time()-start_time
    release_dns(dns)
    return ans

def search_domain(input):
    domain = input[0]
    tld = input[1]
    print(domain, tld)
    ans = {}
    ans = query_domain(domain, tld, "", False, timeout)

    if "ip.dnsresolver.LifetimeTimeout" in ans:
        # print("ip.dnsresolver.LifetimeTimeout")
        ans = query_domain(domain, tld, ans["dns"], True, 2*timeout)
    
    elif ("ips" not in ans) and ("nameservers" not in ans):
        # print("no ip no nameserver")
        ans = query_domain(domain, tld, ans["dns"], True, 2*timeout)

    # print(ans)
    # res.append(ans)
    return ans


def process_domain(res):
    # print(res)
    domain = res[0]["domain"]
    # res = search_domain(domain, tlds1_list)
    # print(res)
    networks = set()
    tlds1 = 0
    ips1 = 0
    not_taken_domain_tlds = []
    # ips_list = set()
    nameservers_list = set()
    tld_time = defaultdict(lambda: defaultdict(float))
    dns_engine_time = defaultdict(lambda: defaultdict(float))
    for r in res:
        # print(r)
        tld_time[r["tld"]]["time"]+=r["time"]
        dns_engine_time[r["dns"]]["time"]+=r["time"]

        if ("ips" in r) or ("nameservers" in r):
            tlds1+=1
        else:
            not_taken_domain_tlds.append(r["tld"])
        
        ips_flag = False
        if "ips" in r:
            for ip in r["ips"]:
                # ips_list.add(ip)
                n = ".".join(ip.split(".")[:2])
                # print(n)
                if n not in networks:
                    networks.add(n)
                    ips_flag=True
            # if ips_flag:
            #     ips1+=1
        ns_flag = False
        if "nameservers" in r:
            for ns in r["nameservers"]:
                if ns.lower() not in nameservers_list:
                    nameservers_list.add(ns.lower())
                    ns_flag = True
        
        # if ips_flag and ns_flag:
        #     ips1+=1
        if (ips_flag and ns_flag) or (("ips" not in r) and ns_flag) or (("nameservers" not in r) and ips_flag):
            ips1+=1
        
        if "ns.dns.resolver.NXDOMAIN" in r:
            tld_time[r["tld"]]["ns.dns.resolver.NXDOMAIN"]+=1
            dns_engine_time[r["dns"]]["ns.dns.resolver.NXDOMAIN"]+=1
        if "ip.dns.resolver.NXDOMAIN" in r:
            tld_time[r["tld"]]["ip.dns.resolver.NXDOMAIN"]+=1
            dns_engine_time[r["dns"]]["ip.dns.resolver.NXDOMAIN"]+=1
        
        if "ns.dnsresolver.LifetimeTimeout" in r:
            tld_time[r["tld"]]["ns.dnsresolver.LifetimeTimeout"]+=1
            dns_engine_time[r["dns"]]["ns.dnsresolver.LifetimeTimeout"]+=1
        if "ip.dnsresolver.LifetimeTimeout" in r:
            tld_time[r["tld"]]["ip.dnsresolver.LifetimeTimeout"]+=1
            dns_engine_time[r["dns"]]["ip.dnsresolver.LifetimeTimeout"]+=1
        
        if "ns.ValueError" in r:
            tld_time[r["tld"]]["ns.ValueError"]+=1
            dns_engine_time[r["dns"]]["ns.ValueError"]+=1
        if "ip.ValueError" in r:
            tld_time[r["tld"]]["ip.ValueError"]+=1
            dns_engine_time[r["dns"]]["ip.ValueError"]+=1
        
        if "ns.dnsresolver.NoNameservers" in r:
            tld_time[r["tld"]]["ns.dnsresolver.NoNameservers"]+=1
            dns_engine_time[r["dns"]]["ns.dnsresolver.NoNameservers"]+=1
        if "ip.dnsresolver.NoNameservers" in r:
            tld_time[r["tld"]]["ip.dnsresolver.NoNameservers"]+=1
            dns_engine_time[r["dns"]]["ip.dnsresolver.NoNameservers"]+=1
        
        if "ns.dns.resolver.NoAnswer" in r:
            tld_time[r["tld"]]["ns.dns.resolver.NoAnswer"]+=1
            dns_engine_time[r["dns"]]["ns.dns.resolver.NoAnswer"]+=1
        if "ip.dns.resolver.NoAnswer" in r:
            tld_time[r["tld"]]["ip.dns.resolver.NoAnswer"]+=1
            dns_engine_time[r["dns"]]["ip.dns.resolver.NoAnswer"]+=1
        
    
    # print(networks, ips1, tlds1, ips_list, nameservers_list, tld_time)

    # res2 = []
    # if (mode=="smart_check") and (tlds1>=tlds1_threshold):
    #     res2 = search_domain(domain, tlds2_list)
    
    # for r in res2:
    #     # print("tlds2", r)
    #     tld_time[r["tld"]]+=r["time"]
    #     if ("ips" in r) or ("nameservers" in r):
    #         tlds1+=1
        
    #     if "ips" in r:
    #         u = False
    #         for ip in r["ips"]:
    #             # ips_list.add(ip)
    #             n = ".".join(ip.split(".")[:2])
    #             # print(n)
    #             if n not in networks:
    #                 networks.add(n)
    #                 u=True
    #         if u:
    #             ips1+=1
        
    #     # if "nameservers" in r:
    #     #     for ns in r["nameservers"]:
    #     #         nameservers_list.add(ns)
    
    # # print(networks, ips1, tlds1, ips_list, nameservers_list, tld_time)
    # res+=res2    

    return {"domain": domain, "TLDs": tlds1, "IPs": ips1, "tld_time": tld_time, "dns_engine_time": dns_engine_time, "not_taken_domain_tlds": not_taken_domain_tlds}


def full_report_thread(data):
    networks = set()
    nameservers_list = set()
    ans_list = []
    for res in data:
        dct = {}

        ips_flag = False
        if "ips" in res:
            for ip in res["ips"]:
                # ips_list.add(ip)
                n = ".".join(ip.split(".")[:2])
                # print(n)
                if n not in networks:
                    networks.add(n)
                    ips_flag=True
            # if ips_flag:
            #     ips1+=1
        ns_flag = False
        if "nameservers" in res:
            for ns in res["nameservers"]:
                if ns.lower() not in nameservers_list:
                    nameservers_list.add(ns.lower())
                    ns_flag = True
        
        # if ips_flag and ns_flag:
        #     dct["unique"] = "Yes"
        if (ips_flag and ns_flag) or (("ips" not in res) and ns_flag) or (("nameservers" not in res) and ips_flag):
            dct["unique"] = "Yes"
        

        dct["domain"] = res["td"] + "." + res["tld"]
        dct["dns_engine"] = res["dns"]
        if "ips" in res:
            dct["IP"] = ",".join(res["ips"])
        if "nameservers" in res:
            dct["nameserver"] = ",".join(res["nameservers"])
        
        if "ns.dns.resolver.NXDOMAIN" in res:
            dct["ns.dns.resolver.NXDOMAIN"] = "Yes"
        if "ip.dns.resolver.NXDOMAIN" in res:
            dct["ip.dns.resolver.NXDOMAIN"] = "Yes"
        
        if "ns.dnsresolver.LifetimeTimeout" in res:
            dct["ns.dnsresolver.LifetimeTimeout"] = "Yes"
        if "ip.dnsresolver.LifetimeTimeout" in res:
            dct["ip.dnsresolver.LifetimeTimeout"] = "Yes"
        
        if "ns.ValueError" in res:
            dct["ns.ValueError"] = "Yes"
        if "ip.ValueError" in res:
            dct["ip.ValueError"] = "Yes"
        
        if "ns.dnsresolver.NoNameservers" in res:
            dct["ns.dnsresolver.NoNameservers"] = "Yes"
        if "ip.dnsresolver.NoNameservers" in res:
            dct["ip.dnsresolver.NoNameservers"] = "Yes"
        
        if "ns.dns.resolver.NoAnswer" in res:
            dct["ns.dns.resolver.NoAnswer"] = "Yes"
        if "ip.dns.resolver.NoAnswer" in res:
            dct["ip.dns.resolver.NoAnswer"] = "Yes"
        
        if "recheck" in res:
            dct["recheck"] = res["recheck"]
        ans_list.append(dct)
    return ans_list
        

def whois_api(input):
    domain = input[0]
    tld = input[1]
    print("WHOIS API", domain, tld)
    tsd, td, org_tld = extract(domain)
    ans = defaultdict(float)

    ans["domain"] = domain
    ans["td"] = td
    ans["tld"] = tld

    whois_url = "https://api.apilayer.com/whois/check?domain="+td+"."+tld
    # print(whois_url)

    payload = {}
    headers = {
        "apikey": whois_api_key
    }

    try:

        response = requests.request("GET", whois_url, headers=headers, data = payload)

        status_code = response.status_code
        result = json.loads(response.text)
        # print(result)
        if response.status_code==429:
            print(result["message"])
        elif result["result"]=="registered":
            ans["ips"] = ["whois"]
            ans["nameservers"] = ["whois"]

        # print(ans)
        return ans
    except:
        return ans

    # {
    # "result": "registered"
    # }
    # {
    # "result": "available"
    # }


def main():
    start_time =  time.time()
    # domains = ["abc.net"]
    results = defaultdict(list)
    
    domain_tld = []
    for domain in domains:
        tsd, td, org_tld = extract(domain)
        for tld in [tmp_tld for tmp_tld in tlds1_list if tmp_tld!=org_tld] :
            domain_tld.append([domain, tld])
    executor = ThreadPoolExecutor(max_workers=threads)
    for result in executor.map(search_domain, domain_tld):
        results[result["domain"]].append(result)
    

    
    # print(results)
    # for d_t in domain_tld:
    #     results.append(search_domain(d_t))
    
    # print(results)

    results2 = defaultdict()
    executor = ThreadPoolExecutor(max_workers=threads)
    for result in executor.map(process_domain, [results[domain] for domain in domains]):
        results2[result["domain"]] = result
    
    # print(results2)

    if mode=="smart_check":
        domain_tld = []
        for domain in domains:
            if results2[domain]["TLDs"]>=tlds1_threshold: 
                tsd, td, org_tld = extract(domain)
                for tld in [tmp_tld for tmp_tld in tlds2_list if tmp_tld!=org_tld] :
                    domain_tld.append([domain, tld])
        executor = ThreadPoolExecutor(max_workers=threads)
        for result in executor.map(search_domain, domain_tld):
            results[result["domain"]].append(result)
        
        # results2 = []
        results2 = defaultdict()
        executor = ThreadPoolExecutor(max_workers=threads)
        for result in executor.map(process_domain, [results[domain] for domain in domains]):
            # results2.append(result)
            results2[result["domain"]] = result
        
    domains_whois = [domain for domain in domains if results2[domain]["TLDs"]>=whois_taken_threshold]
    domain_whois_tld = []
    for domain in domains_whois:
        tsd, td, org_tld = extract(domain)
        for tld in [tmp_tld for tmp_tld in results2[domain]["not_taken_domain_tlds"] if ((tmp_tld!=org_tld) and (tmp_tld in whois_tlds))] :
            domain_whois_tld.append([domain, tld])
    # print(domain_whois_tld)
    # print(whois_api(["abc.net", "net"]))

    executor = ThreadPoolExecutor(max_workers=threads)
    for result in executor.map(whois_api, domain_whois_tld):
        # results[result["domain"]].append(result)
        for tld_result in results[result["domain"]]:
            if tld_result["tld"]==result["tld"]:
                tld_result.update(result)
                break
    
    results2 = defaultdict()
    executor = ThreadPoolExecutor(max_workers=threads)
    for result in executor.map(process_domain, [results[domain] for domain in domains]):
        # results2.append(result)
        results2[result["domain"]] = result
    


    # for domain in domains_whois:
    #     print(results2[domain]["not_taken_domain_tlds"])
        

    
    # print("\n\n\n\n")
    # print(results2)
    
    file_name = "Smart_Check_"
    if mode!="smart_check":
        file_name = "Full_Check_"
        # results2 = [results2[domain] for domain in domains]
    results2 = [results2[domain] for domain in domains]
    
    df = pd.DataFrame(results2, columns=["domain", "TLDs", "IPs"])
    df = df[df["TLDs"]>0]
    df.to_csv(file_name+datetime.today().strftime('%Y%d%m_%H%M%S')+".csv", index=False)
    
    if full_report:
        ans_list = []
        executor = ThreadPoolExecutor(max_workers=threads)
        for result in executor.map(full_report_thread, [results[domain] for domain in domains]):
            ans_list+=result
            
        df = pd.DataFrame(ans_list)
        cols = ["domain", "IP", "nameserver", "dns_engine", "recheck", "unique"] + list(set(df.columns)-{"domain", "IP", "nameserver", "dns_engine", "recheck", "unique"})
        try:
            df = df[cols]
        except:
            pass
        df.to_csv("Full_Report_"+file_name+datetime.today().strftime('%Y%d%m_%H%M%S')+".csv", index=False)

    if tlds_time_analysis:
        tlds_dict = defaultdict(lambda: defaultdict(float))
        for tmp in results2:
            for tld in tmp["tld_time"]:
                tlds_dict[tld]["#Req"]+=1
                for key1 in tmp["tld_time"][tld]:
                    tlds_dict[tld][key1]+=tmp["tld_time"][tld][key1]

                # tlds_dict[tld][0]+=tmp["tld_time"][tld]
                # tlds_dict[tld][1]+=1
        
        # tlds_list = [[key, tlds_dict[key][0], tlds_dict[key][1]] for key in tlds_dict.keys()]
        tlds_list = []
        for tld in tlds_dict:
            dct = {}
            dct["TLDs"] = tld
            for key1 in tlds_dict[tld]:
                dct[key1] = tlds_dict[tld][key1]
            tlds_list.append(dct)
        # df = pd.DataFrame(tlds_list, columns=["TLDs", "Time", "#Req"])
        df = pd.DataFrame(tlds_list)
        df["TimePerReq"] = df["time"]/df["#Req"]
        df.to_csv("TLDs_Time_Analysis_"+datetime.today().strftime('%Y%d%m_%H%M%S')+".csv", index=False)
    
    
    if dns_engines_analysis:
        dns_dict = defaultdict(lambda: defaultdict(float))
        for tmp in results2:
            for dns in tmp["dns_engine_time"]:
                dns_dict[dns]["#Req"]+=1
                for key1 in tmp["dns_engine_time"][dns]:
                    dns_dict[dns][key1]+=tmp["dns_engine_time"][dns][key1]

                # tlds_dict[tld][0]+=tmp["tld_time"][tld]
                # tlds_dict[tld][1]+=1
        
        # tlds_list = [[key, tlds_dict[key][0], tlds_dict[key][1]] for key in tlds_dict.keys()]
        dns_list = []
        for dns in dns_dict:
            dct = {}
            dct["DNS_Engine"] = dns
            for key1 in dns_dict[dns]:
                dct[key1] = dns_dict[dns][key1]
            dns_list.append(dct)
        # df = pd.DataFrame(tlds_list, columns=["TLDs", "Time", "#Req"])
        df = pd.DataFrame(dns_list)
        df["TimePerReq"] = df["time"]/df["#Req"]
        df.to_csv("DNS_Engines_Analysis_"+datetime.today().strftime('%Y%d%m_%H%M%S')+".csv", index=False)
    
    print(time.time()-start_time)


if __name__ == '__main__':
    main()