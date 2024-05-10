import os
import config

dir_path = os.path.dirname(os.path.realpath(__file__))

DOMAINS_FILE = dir_path + "\\domains.txt"
OLD_DOMAINS_FILE = dir_path + "\\old_domains.txt"
TLDS1_FILE = ""
TLDS2_FILE = ""
TLDS_FILE = ""
DNS_ENGINES_FILE = dir_path + "\\dns_engines.txt"
WHOIS_TLDS_FILE = dir_path + "\\whois_TLDs.txt"

if config.mode=="smart_check":
    TLDS1_FILE = dir_path + "\\TLDs1.txt"
    TLDS2_FILE = dir_path + "\\TLDs2.txt"
else:
    TLDS_FILE = dir_path + "\\TLDs_full.txt"

def get_domains():
    with open(DOMAINS_FILE, "r") as f:
        return [term.strip().replace("\n", "") for term in f.readlines()]

def get_old_domains():
    with open(OLD_DOMAINS_FILE, "r") as f:
        return [term.strip().replace("\n", "") for term in f.readlines()]


def get_tlds1():
    with open(TLDS1_FILE, "r") as f:
        return [term.strip().replace("\n", "") for term in f.readlines()]

def get_tlds2():
    with open(TLDS2_FILE, "r") as f:
        return [term.strip().replace("\n", "") for term in f.readlines()]

def get_tlds():
    with open(TLDS_FILE, "r") as f:
        return [term.strip().replace("\n", "") for term in f.readlines()]

def get_dns_engines():
    with open(DNS_ENGINES_FILE, "r") as f:
        return [term.strip().replace("\n", "") for term in f.readlines()]

def get_whois_tlds():
    with open(WHOIS_TLDS_FILE, "r") as f:
        return [term.strip().replace("\n", "") for term in f.readlines()]