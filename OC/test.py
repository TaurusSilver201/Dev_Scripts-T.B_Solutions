import httpx
from bs4 import BeautifulSoup

import requests

cookies = {
    '_openc_session': 'dDJRN2oySk1BWUR4MnZwUWZ3NFluTFhIYTRaMGE5SDR2cXdEajBDNnFRWG9rRThFeGNpMzM3em1RbUdDUjRJQkhpSnRyWFVQbGdkWmFGS3E4bGxaZzlyelltakYweVc4UDVyMjhmNEtJU0t4Q2pZWXZVbmtpWHNzUzJ2MUZjT0NtU1lPeDR0N1FQdk8wcnd4UURwQkxMaHVPZWVDZjFzUFRpSk40bWZYVDFvODJUQXVxemx4Q1ZkV1NacXE3Nk92elMzeWdMQ2VGR09QcmtxRzhvbU1ocEtGb1J1L0VGQ0pseUJ6dis4V0ZUZnpLV0RZSDdlOG9kUys4SUVRblRTMk05V1VqV05PU2F6c1Y1TC80dm5zYXc9PS0tZVcraTBhUDR0WVExVnZ3YlpGekxwZz09--a2a030f14532f25361f4460ae564f8831f2ab659',
    'KEY': '1024357*1082681:435700994:747822414:1',
}

headers = {
    'authority': 'opencorporates.com',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'accept-language': 'en-US,en;q=0.9',
    'cache-control': 'max-age=0',
    # Requests sorts cookies= alphabetically
    # 'cookie': '_gcl_au=1.1.1191478180.1666622579; _ga=GA1.2.1793871176.1666622579; _gid=GA1.2.1728325934.1666622579; user_name=Tom+Bran; delay_popup=delay_popup; survey_sparrow=6lmkC0mxASAin%2ByH; _openc_session=dDJRN2oySk1BWUR4MnZwUWZ3NFluTFhIYTRaMGE5SDR2cXdEajBDNnFRWG9rRThFeGNpMzM3em1RbUdDUjRJQkhpSnRyWFVQbGdkWmFGS3E4bGxaZzlyelltakYweVc4UDVyMjhmNEtJU0t4Q2pZWXZVbmtpWHNzUzJ2MUZjT0NtU1lPeDR0N1FQdk8wcnd4UURwQkxMaHVPZWVDZjFzUFRpSk40bWZYVDFvODJUQXVxemx4Q1ZkV1NacXE3Nk92elMzeWdMQ2VGR09QcmtxRzhvbU1ocEtGb1J1L0VGQ0pseUJ6dis4V0ZUZnpLV0RZSDdlOG9kUys4SUVRblRTMk05V1VqV05PU2F6c1Y1TC80dm5zYXc9PS0tZVcraTBhUDR0WVExVnZ3YlpGekxwZz09--a2a030f14532f25361f4460ae564f8831f2ab659; KEY=1024357*1082681:435700994:747822414:1',
    'referer': 'https://opencorporates.com/companies?utf8=%E2%9C%93&q=cedar&commit=Go&jurisdiction_code=&utf8=%E2%9C%93&button=&controller=searches&action=search_companies&mode=best_fields&search_fields%5B%5D=name&search_fields%5B%5D=previous_names&search_fields%5B%5D=company_number&search_fields%5B%5D=other_company_numbers&branch=&nonprofit=&order=',
    'sec-ch-ua': '"Chromium";v="106", "Google Chrome";v="106", "Not;A=Brand";v="99"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'same-origin',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36',
}

params = [
    ('utf8', '✓'),
    ('q', 'cedar'),
    ('commit', 'Go'),
    ('jurisdiction_code', ''),
    ('utf8', '✓'),
    ('button', ''),
    ('controller', 'searches'),
    ('action', 'search_companies'),
    ('mode', 'best_fields'),
    ('search_fields[]', 'name'),
    ('search_fields[]', 'previous_names'),
    ('search_fields[]', 'company_number'),
    ('search_fields[]', 'other_company_numbers'),
    ('branch', ''),
    ('nonprofit', ''),
    ('order', ''),
]

page = requests.get('https://opencorporates.com/companies', params=params, cookies=cookies)

soup = BeautifulSoup(page.text, 'lxml')
ans = soup.select("div.span7 h2")
print(ans)