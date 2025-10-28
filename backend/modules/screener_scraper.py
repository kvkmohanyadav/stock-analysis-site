import requests
from bs4 import BeautifulSoup
import re
from typing import Dict, Optional

class ScreenerScraper:
    """Scraper to fetch stock financial data from screener.in"""
    
    def __init__(self):
        self.base_url = "https://www.screener.in"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
    
    def search_stock(self, symbol: str) -> Optional[str]:
        """Search for stock and return company URL"""
        try:
            search_url = f"{self.base_url}/search/?q={symbol}"
            response = requests.get(search_url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find first result link
            results = soup.find_all('a', class_='company-card', href=True)
            if results:
                company_path = results[0]['href']
                return f"{self.base_url}{company_path}"
            return None
        except Exception as e:
            print(f"Error searching for {symbol}: {e}")
            return None
    
    def fetch_financial_data(self, symbol: str) -> Optional[Dict]:
        """Fetch all financial metrics from screener.in"""
        try:
            # Try direct company URL first
            company_url = f"{self.base_url}/company/{symbol.upper()}/"
            response = requests.get(company_url, headers=self.headers, timeout=10)
            
            # If direct access fails, try search
            if response.status_code != 200:
                company_url = self.search_stock(symbol)
                if not company_url:
                    return None
                response = requests.get(company_url, headers=self.headers, timeout=10)
            
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            data = {
                'symbol': symbol.upper(),
                'name': self._extract_company_name(soup),
                'current_price': self._extract_price(soup),
                'market_cap': self._extract_market_cap(soup),
                'pe_ratio': self._extract_pe(soup),
                'book_value': self._extract_book_value(soup),
                'roe': self._extract_roe(soup),
                'roce': self._extract_roce(soup),
                '52w_high': self._extract_52w_high(soup),
                '52w_low': self._extract_52w_low(soup),
                'dividend_yield': self._extract_dividend_yield(soup),
                'sector': self._extract_sector(soup),
                'peer_comparison': self._extract_peer_comparison(soup)
            }
            
            return data
        except Exception as e:
            print(f"Error fetching data for {symbol} from screener.in: {e}")
            return None
    
    def _extract_company_name(self, soup):
        """Extract company name"""
        try:
            # Try h1 with class 'h2' first (current format)
            h1 = soup.find('h1', class_='h2')
            if h1:
                return h1.get_text(strip=True)
            
            # Fallback to any h1
            h1 = soup.find('h1')
            if h1:
                return h1.get_text(strip=True)
            
            # Try page-title class
            title = soup.find(class_='page-title')
            if title:
                return title.get_text(strip=True)
        except:
            pass
        return "Unknown"
    
    def _extract_price(self, soup):
        """Extract current price"""
        try:
            # Look in stats section
            for stat in soup.find_all('li', class_='flex flex-space-between'):
                label = stat.find('span', class_='name')
                if label and 'Current Price' in label.get_text():
                    value_span = stat.find('span', class_='value')
                    if value_span:
                        price_text = value_span.get_text(strip=True)
                        # Extract number (could be "₹493" or "493")
                        # Remove currency symbols and commas
                        cleaned = price_text.replace('₹', '').replace(',', '').strip()
                        match = re.search(r'[\d]+\.?\d*', cleaned)
                        if match:
                            return float(match.group())
        except:
            pass
        return 0
    
    def _extract_market_cap(self, soup):
        """Extract market cap"""
        try:
            # Find market cap in stats
            for stat in soup.find_all('li', class_='flex flex-space-between'):
                label = stat.find('span', class_='name')
                if label and 'Market Cap' in label.get_text():
                    value_span = stat.find('span', class_='value')
                    if value_span:
                        return value_span.get_text(strip=True)
        except:
            pass
        return "0"
    
    def _extract_pe(self, soup):
        """Extract P/E ratio"""
        try:
            for stat in soup.find_all('li', class_='flex flex-space-between'):
                label = stat.find('span', class_='name')
                if label and 'Stock P/E' in label.get_text():
                    value_span = stat.find('span', class_='value')
                    if value_span:
                        pe_text = value_span.get_text(strip=True)
                        match = re.search(r'[\d,]+\.?\d*', pe_text.replace(',', ''))
                        if match:
                            return float(match.group())
        except:
            pass
        return 0
    
    def _extract_book_value(self, soup):
        """Extract book value"""
        try:
            for stat in soup.find_all('li', class_='flex flex-space-between'):
                label = stat.find('span', class_='name')
                if label and 'Book Value' in label.get_text():
                    value_span = stat.find('span', class_='value')
                    if value_span:
                        bv_text = value_span.get_text(strip=True)
                        match = re.search(r'[\d,]+\.?\d*', bv_text.replace(',', ''))
                        if match:
                            return float(match.group())
        except:
            pass
        return 0
    
    def _extract_roe(self, soup):
        """Extract ROE"""
        try:
            for stat in soup.find_all('li', class_='flex flex-space-between'):
                label = stat.find('span', class_='name')
                if label and 'ROE' in label.get_text():
                    value_span = stat.find('span', class_='value')
                    if value_span:
                        roe_text = value_span.get_text(strip=True)
                        match = re.search(r'[\d,]+\.?\d*', roe_text.replace(',', ''))
                        if match:
                            return float(match.group())
        except:
            pass
        return 0
    
    def _extract_roce(self, soup):
        """Extract ROCE"""
        try:
            for stat in soup.find_all('li', class_='flex flex-space-between'):
                label = stat.find('span', class_='name')
                if label and 'ROCE' in label.get_text():
                    value_span = stat.find('span', class_='value')
                    if value_span:
                        roce_text = value_span.get_text(strip=True)
                        match = re.search(r'[\d,]+\.?\d*', roce_text.replace(',', ''))
                        if match:
                            return float(match.group())
        except:
            pass
        return 0
    
    def _extract_52w_high(self, soup):
        """Extract 52 week high"""
        try:
            for stat in soup.find_all('li', class_='flex flex-space-between'):
                label = stat.find('span', class_='name')
                if label and 'High / Low' in label.get_text():
                    value_span = stat.find('span', class_='value')
                    if value_span:
                        hl_text = value_span.get_text(strip=True)
                        # Format: "123 / 456"
                        parts = hl_text.split('/')
                        if len(parts) >= 1:
                            high = parts[0].strip()
                            match = re.search(r'[\d,]+\.?\d*', high.replace(',', ''))
                            if match:
                                return float(match.group())
        except:
            pass
        return 0
    
    def _extract_52w_low(self, soup):
        """Extract 52 week low"""
        try:
            for stat in soup.find_all('li', class_='flex flex-space-between'):
                label = stat.find('span', class_='name')
                if label and 'High / Low' in label.get_text():
                    value_span = stat.find('span', class_='value')
                    if value_span:
                        hl_text = value_span.get_text(strip=True)
                        # Format: "123 / 456"
                        parts = hl_text.split('/')
                        if len(parts) >= 2:
                            low = parts[1].strip()
                            match = re.search(r'[\d,]+\.?\d*', low.replace(',', ''))
                            if match:
                                return float(match.group())
        except:
            pass
        return 0
    
    def _extract_dividend_yield(self, soup):
        """Extract dividend yield"""
        try:
            for stat in soup.find_all('li', class_='flex flex-space-between'):
                label = stat.find('span', class_='name')
                if label and 'Dividend Yield' in label.get_text():
                    value_span = stat.find('span', class_='value')
                    if value_span:
                        div_text = value_span.get_text(strip=True).replace('%', '')
                        match = re.search(r'[\d,]+\.?\d*', div_text.replace(',', ''))
                        if match:
                            return float(match.group())
        except:
            pass
        return 0
    
    def _extract_sector(self, soup):
        """Extract sector - look for common Indian market sectors"""
        try:
            # Common sector keywords in Indian markets
            sectors = ['IT Services', 'Software', 'Information Technology', 'Technology Services',
                      'Beverages', 'Banking', 'Financial Services', 'Private Banks', 'Public Sector Banks',
                      'Pharmaceuticals', 'Automobiles', 'Telecom', 'Energy', 'FMCG', 'Metals', 
                      'Capital Goods', 'Healthcare', 'Textiles', 'Chemicals', 'Retail', 
                      'Real Estate', 'Power', 'Sugar', 'Breweries & Distilleries', 'Oil & Gas', 
                      'Infrastructure', 'Media']
            
            text = soup.get_text()
            
            # Find which sector appears in the page
            for sector in sectors:
                # Look for sector in context near "Peer comparison" or similar
                lines = text.split('\n')
                for i, line in enumerate(lines):
                    if sector in line:
                        # Check if this is in a meaningful context (not just in title)
                        # Usually sector appears after "Peer comparison" heading
                        if i > 0:
                            prev_lines = lines[max(0, i-10):i]
                            if any('Peer' in pl or 'comparison' in pl for pl in prev_lines):
                                return sector
            
            return "Unknown"
        except:
            pass
        return "Unknown"
    
    def _extract_peer_comparison(self, soup):
        """Extract peer comparison table from screener.in"""
        try:
            # Find the h2 with "Peer comparison" text
            peer_h2 = None
            for h2 in soup.find_all('h2'):
                if 'Peer' in h2.get_text():
                    peer_h2 = h2
                    break
            
            if not peer_h2:
                return None
            
            # Look for all tables and find the one near the peer h2
            all_tables = soup.find_all('table')
            peer_table = None
            
            # Find which table is closest after the peer_h2
            for table in all_tables:
                # Check if this table is after peer_h2 in document order
                if table.find_previous('h2') == peer_h2:
                    # This table comes after the peer h2
                    # Verify it's in a reasonable distance (not too far)
                    parent = table.find_parent()
                    if parent and peer_h2 in parent.find_all('h2'):
                        peer_table = table
                        break
            
            if not peer_table:
                # Fallback: just take the first table after the h2
                elements_after_h2 = []
                for element in soup.descendants:
                    if element == peer_h2:
                        found_h2 = True
                        continue
                    if 'found_h2' in locals() and hasattr(element, 'name') and element.name == 'table':
                        peer_table = element
                        break
                
            if not peer_table:
                return None
            
            # Extract headers
            headers = []
            thead = peer_table.find('thead')
            if thead:
                header_row = thead.find('tr')
                if header_row:
                    for th in header_row.find_all(['th', 'td']):
                        headers.append(th.get_text(strip=True))
            
            # Extract rows
            rows = []
            tbody = peer_table.find('tbody')
            if tbody:
                for tr in tbody.find_all('tr'):
                    row_data = []
                    for td in tr.find_all(['td', 'th']):
                        text = td.get_text(strip=True)
                        row_data.append(text)
                    if row_data:
                        rows.append(row_data)
            
            return {
                'headers': headers,
                'rows': rows
            }
        except Exception as e:
            print(f"Error extracting peer comparison: {e}")
            return None

