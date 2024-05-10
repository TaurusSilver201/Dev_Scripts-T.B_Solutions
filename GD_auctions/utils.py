import os 
dir_path = os.path.dirname(os.path.realpath(__file__))
parent_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

TERMS_FILE = dir_path + "\\domains.txt"
PROXIES_FILE = parent_path + "\\proxies.txt"

def get_terms():
    with open(TERMS_FILE, "r") as f:
        return [term.strip().replace("\n", "") for term in f.readlines()]

def get_proxies():
    with open(PROXIES_FILE, "r") as f:
        proxies = []
        for proxy in f.readlines():
            raw_list = proxy.strip().replace("\n", "").split(":", 2)
            # proxies.append(raw_list[0] + ":" + raw_list[1])
            proxies.append(
                f"http://{raw_list[-1]}@{raw_list[0]}:{raw_list[1]}"
            )
        return proxies