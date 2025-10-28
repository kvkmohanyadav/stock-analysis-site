import requests
from bs4 import BeautifulSoup

headers = {'User-Agent': 'Mozilla/5.0'}
r = requests.get('https://www.screener.in/company/TCS/', headers=headers)
soup = BeautifulSoup(r.content, 'html.parser')

print("Looking for Peer comparison section...")
peer_h2 = None
for h2 in soup.find_all('h2'):
    if 'Peer' in h2.get_text():
        peer_h2 = h2
        print(f"Found H2: {h2.get_text()}")
        break

if peer_h2:
    parent = peer_h2.find_parent()
    print(f"Parent: {parent.name if parent else 'None'}")
    
    if parent:
        # Check all tables in the document
        all_tables = soup.find_all('table')
        print(f"Total tables in page: {len(all_tables)}")
        
        # Find the nearest table after the h2
        parent_tables = parent.find_all('table', recursive=True)
        print(f"Tables in parent: {len(parent_tables)}")
