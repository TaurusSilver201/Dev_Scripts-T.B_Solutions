import dns.resolver as dnsresolver
import pandas as pd
from collections import defaultdict
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

def get_terms():
    with open("test_domains.txt", "r") as f:
        return [term.strip().replace("\n", "") for term in f.readlines()]

def get_dns_engines():
    with open("dns_engines.txt", "r") as f:
        return [term.strip().replace("\n", "") for term in f.readlines()]

domains = get_terms()

def dnsResults(dns):  
    res = []
    for domain in domains:
        # print(dns, domain)
        ans = defaultdict(float)  
        ans["addrs"] = ",".join(dns)
        ans["domain"] = domain
        start_time = time.time()
        try:
            resolver = dnsresolver.Resolver()
            resolver.nameservers = dns
            # resolver.port = 8443
            result = resolver.resolve(domain, 'A')
            # print(type(result))
            ips = set([ip.to_text() for ip in result])
            ans["ip"] = ",".join(ips)
            # print(ips)
            result = resolver.resolve(domain, 'NS')
            nameservers = set([ns.to_text() for ns in result])
            ans["nameservers"] = ",".join(nameservers)
            
            # print(nameservers)
            # return True
        except dnsresolver.NXDOMAIN:
            # print("dns.resolver.NXDOMAIN")
            ans["dns.resolver.NXDOMAIN"]+=1
            # return False
        except dnsresolver.LifetimeTimeout:
            # print("timeout")
            ans["dnsresolver.LifetimeTimeout"]+=1
            # return False
        except ValueError:
            # print("value error")
            ans["ValueError"]+=1
            # return False
        except dnsresolver.NoNameservers:
            # print("dns.resolver.NoNameservers")
            ans["dnsresolver.NoNameservers"]+=1
            # return False
        except dnsresolver.NoAnswer:
            # print("dns.resolver.NoAnswer")
            ans["dns.resolver.NoAnswer"]+=1
            # return False
        ans["time"] = time.time()-start_time
        res.append(ans)
    return res


# print(dnsResults(["8.8.8.8", "8.8.4.4"]))
def main():
    dns_engines = get_dns_engines()
    # df = pd.read_csv("dns_engines_final.csv")
    results = []
    executor = ThreadPoolExecutor(max_workers=100)
    # for result in executor.map(dnsResults, [val.split(",") for val in df["addrs"].values]):
    for result in executor.map(dnsResults, [val.split(",") for val in dns_engines]):
        results+=result


    # print(results)
    df2 = pd.DataFrame(results)
    # df = pd.merge(df, df2, on='addrs', how='inner')
    # cols = list(df.columns)
    # cols.remove("description")
    # cols.append("description")
    # df = df[cols]
    # df = pd.concat([df, df2], axis=1)
    # print(df)
    df2.to_csv("dns_engines_test_"+datetime.today().strftime('%Y%d%m_%H%M%S')+".csv", index=False)


if __name__ == '__main__':
    main()