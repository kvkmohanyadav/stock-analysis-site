import requests
from bs4 import BeautifulSoup
import re
from typing import Dict, Optional
from datetime import datetime, timedelta

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
                'peer_comparison': self._extract_peer_comparison(soup),
                'quarterly_results': self._extract_quarterly_results(soup),
                'peg_ratio': self._extract_peg(soup),
                'debt_to_equity': self._extract_debt_to_equity(soup),
                'profit_margin': self._extract_profit_margin(soup),
                'annual_results': self._extract_annual_results(soup)
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
                return []
            
            # Look for all tables and find the one near the peer h2
            all_tables = soup.find_all('table')
            peer_table = None
            
            # Find which table is closest after the peer_h2
            for table in all_tables:
                # Check if this table is after peer_h2 in document order
                if table.find_previous('h2') == peer_h2:
                    parent = table.find_parent()
                    if parent and peer_h2 in parent.find_all('h2'):
                        peer_table = table
                        break
            
            if not peer_table:
                # Fallback: find first table after h2
                found_h2 = False
                for element in soup.descendants:
                    if element == peer_h2:
                        found_h2 = True
                        continue
                    if found_h2 and hasattr(element, 'name') and element.name == 'table':
                        peer_table = element
                        break
                
            if not peer_table:
                return []
            
            # Extract headers to find column indices
            thead = peer_table.find('thead')
            header_row = None
            column_map = {}
            if thead:
                header_row = thead.find('tr')
                if header_row:
                    headers = [th.get_text(strip=True).lower() for th in header_row.find_all(['th', 'td'])]
                    # Map column names to indices
                    for idx, header in enumerate(headers):
                        if 'name' in header or 'company' in header:
                            column_map['name'] = idx
                        elif 'cmp' in header or 'current price' in header or 'price' in header:
                            column_map['cmp'] = idx
                        elif 'pe' in header and '/' not in header.split('pe')[0]:
                            column_map['pe'] = idx
                        elif 'mar' in header and 'cap' in header:
                            column_map['mar_cap'] = idx
                        elif 'div' in header and 'yld' in header:
                            column_map['div_yld'] = idx
                        elif 'roe' in header.lower() and 'roce' not in header.lower():
                            column_map['roe'] = idx
                        elif 'roce' in header.lower():
                            column_map['roce'] = idx
            
            # Extract rows from tbody
            peers = []
            tbody = peer_table.find('tbody')
            if tbody:
                for idx, tr in enumerate(tbody.find_all('tr'), 1):
                    cells = tr.find_all(['td', 'th'])
                    if len(cells) >= 5:  # At least need name, cmp, and a few metrics
                        try:
                            # Use column_map if available, otherwise use default positions
                            name_idx = column_map.get('name', 0)
                            cmp_idx = column_map.get('cmp', 1)
                            pe_idx = column_map.get('pe', 2)
                            mar_cap_idx = column_map.get('mar_cap', 3)
                            div_yld_idx = column_map.get('div_yld', 4)
                            roe_idx = column_map.get('roe', 5)
                            roce_idx = column_map.get('roce', 6)
                            
                            # Extract data using mapped indices
                            name = cells[name_idx].get_text(strip=True) if len(cells) > name_idx else ""
                            cmp_text = cells[cmp_idx].get_text(strip=True) if len(cells) > cmp_idx else "0"
                            pe_text = cells[pe_idx].get_text(strip=True) if len(cells) > pe_idx else "0"
                            mar_cap_text = cells[mar_cap_idx].get_text(strip=True) if len(cells) > mar_cap_idx else "0"
                            div_yld_text = cells[div_yld_idx].get_text(strip=True) if len(cells) > div_yld_idx else "0"
                            roe_text = cells[roe_idx].get_text(strip=True) if len(cells) > roe_idx else "0"
                            roce_text = cells[roce_idx].get_text(strip=True) if len(cells) > roce_idx else "0"
                            
                            # Parse CMP
                            cmp = re.search(r'[\d,]+\.?\d*', cmp_text.replace(',', '').replace('₹', ''))
                            cmp_value = float(cmp.group()) if cmp else 0
                            
                            # Parse P/E
                            pe = re.search(r'[\d,]+\.?\d*', pe_text.replace(',', ''))
                            pe_value = float(pe.group()) if pe else 0
                            
                            # Market Cap is already in text format (e.g., "50,000 Cr")
                            mar_cap = mar_cap_text
                            
                            # Parse Dividend Yield
                            div_yld = re.search(r'[\d,]+\.?\d*', div_yld_text.replace(',', '').replace('%', ''))
                            div_yld_value = float(div_yld.group()) if div_yld else 0
                            
                            # Parse ROE
                            roe = re.search(r'[\d,]+\.?\d*', roe_text.replace(',', '').replace('%', ''))
                            roe_value = float(roe.group()) if roe else 0
                            
                            # Parse ROCE
                            roce = re.search(r'[\d,]+\.?\d*', roce_text.replace(',', '').replace('%', ''))
                            roce_value = float(roce.group()) if roce else 0
                            
                            peers.append({
                                "sno": idx,
                                "name": name,
                                "cmp": round(cmp_value, 2),
                                "pe": round(pe_value, 2) if pe_value > 0 else None,
                                "mar_cap": mar_cap,
                                "div_yld": round(div_yld_value, 2) if div_yld_value > 0 else None,
                                "roe": round(roe_value, 2) if roe_value > 0 else None,
                                "roce": round(roce_value, 2) if roce_value > 0 else None
                            })
                        except Exception as e:
                            print(f"Error parsing peer row: {e}")
                            continue
            
            return peers
        except Exception as e:
            print(f"Error extracting peer comparison: {e}")
            return []
    
    def _extract_quarterly_results(self, soup):
        """Extract quarterly results table from screener.in with headers and rows"""
        try:
            # Find h2 with "Quarterly" or "Results" text
            quarterly_h2 = None
            for h2 in soup.find_all('h2'):
                text = h2.get_text().lower()
                if 'quarterly' in text or ('results' in text and 'quarterly' in text):
                    quarterly_h2 = h2
                    break
            
            if not quarterly_h2:
                return None
            
            # Find table after the h2
            quarterly_table = None
            found_h2 = False
            for element in soup.descendants:
                if element == quarterly_h2:
                    found_h2 = True
                    continue
                if found_h2 and hasattr(element, 'name') and element.name == 'table':
                    quarterly_table = element
                    break
            
            if not quarterly_table:
                return None
            
            # Extract headers
            headers = []
            thead = quarterly_table.find('thead')
            if thead:
                header_row = thead.find('tr')
                if header_row:
                    headers = [th.get_text(strip=True) for th in header_row.find_all(['th', 'td'])]
            
            if not headers:
                # Try to find headers in first row if no thead
                first_row = quarterly_table.find('tr')
                if first_row:
                    headers = [th.get_text(strip=True) for th in first_row.find_all(['th', 'td'])]
            
            # Extract rows
            rows = []
            tbody = quarterly_table.find('tbody')
            table_rows = tbody.find_all('tr') if tbody else quarterly_table.find_all('tr')[1:]  # Skip header row
            
            for tr in table_rows:
                cells = [td.get_text(strip=True) for td in tr.find_all(['td', 'th'])]
                if cells and len(cells) > 0:
                    rows.append(cells)
            
            if headers and rows:
                return {
                    "headers": headers,
                    "rows": rows
                }
            
            return None
        except Exception as e:
            print(f"Error extracting quarterly results: {e}")
            return None
    
    def fetch_bulk_deals(self, symbol: str, days: int = 30) -> Optional[list]:
        """Fetch bulk deals data for the last N days from screener.in"""
        try:
            # Try direct company URL first
            company_url = f"{self.base_url}/company/{symbol.upper()}/"
            response = requests.get(company_url, headers=self.headers, timeout=10)
            
            # If direct access fails, try search
            if response.status_code != 200:
                company_url = self.search_stock(symbol)
                if not company_url:
                    return []
                response = requests.get(company_url, headers=self.headers, timeout=10)
            
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            bulk_deals = []
            
            # Look for "Bulk Deals" or similar section
            # Check for h2, h3, or div with bulk deals text
            bulk_section = None
            for h2 in soup.find_all(['h2', 'h3']):
                text = h2.get_text().lower()
                if 'bulk' in text and 'deal' in text:
                    bulk_section = h2
                    break
            
            if not bulk_section:
                # Try searching in clues/tabs section
                for link in soup.find_all('a', href=True):
                    if 'bulk' in link.get_text().lower() and 'deal' in link.get_text().lower():
                        # If found a link, try to follow it
                        bulk_url = link['href']
                        if bulk_url.startswith('/'):
                            bulk_url = f"{self.base_url}{bulk_url}"
                        elif not bulk_url.startswith('http'):
                            bulk_url = f"{self.base_url}/{bulk_url}"
                        
                        try:
                            bulk_response = requests.get(bulk_url, headers=self.headers, timeout=10)
                            if bulk_response.status_code == 200:
                                soup = BeautifulSoup(bulk_response.content, 'html.parser')
                                bulk_section = soup.find('h2') or soup.find('h3')
                        except:
                            pass
                        break
            
            if not bulk_section:
                print(f"No bulk deals section found for {symbol}")
                return []
            
            # Find table near bulk section
            bulk_table = None
            found_section = False
            for element in soup.descendants:
                if element == bulk_section:
                    found_section = True
                    continue
                if found_section and hasattr(element, 'name') and element.name == 'table':
                    bulk_table = element
                    break
            
            # If no table found, try to find any table with bulk deals data
            if not bulk_table:
                all_tables = soup.find_all('table')
                for table in all_tables:
                    table_text = table.get_text().lower()
                    if 'buyer' in table_text or 'seller' in table_text or 'quantity' in table_text:
                        bulk_table = table
                        break
            
            if not bulk_table:
                print(f"No bulk deals table found for {symbol}")
                return []
            
            # Extract headers
            headers = []
            thead = bulk_table.find('thead')
            if thead:
                header_row = thead.find('tr')
                if header_row:
                    headers = [th.get_text(strip=True).lower() for th in header_row.find_all(['th', 'td'])]
            
            if not headers:
                first_row = bulk_table.find('tr')
                if first_row:
                    headers = [th.get_text(strip=True).lower() for th in first_row.find_all(['th', 'td'])]
            
            # Map column indices
            column_map = {}
            for idx, header in enumerate(headers):
                if 'date' in header:
                    column_map['date'] = idx
                elif 'buyer' in header or 'client' in header:
                    column_map['buyer'] = idx
                elif 'seller' in header:
                    column_map['seller'] = idx
                elif 'quantity' in header or 'qty' in header:
                    column_map['quantity'] = idx
                elif 'price' in header and 'rate' not in header:
                    column_map['price'] = idx
                elif 'rate' in header:
                    column_map['price'] = idx
                elif 'value' in header or 'amount' in header:
                    column_map['value'] = idx
            
            # Extract rows
            tbody = bulk_table.find('tbody')
            table_rows = tbody.find_all('tr') if tbody else bulk_table.find_all('tr')[1:]
            
            cutoff_date = datetime.now() - timedelta(days=days)
            
            for tr in table_rows:
                cells = tr.find_all(['td', 'th'])
                if len(cells) < 3:
                    continue
                
                try:
                    deal = {}
                    
                    # Extract date
                    date_idx = column_map.get('date', 0)
                    if len(cells) > date_idx:
                        date_text = cells[date_idx].get_text(strip=True)
                        # Parse date (format can vary: "30-Oct-2025", "30/10/2025", etc.)
                        date_obj = None
                        for fmt in ['%d-%b-%Y', '%d/%m/%Y', '%d-%m-%Y', '%Y-%m-%d']:
                            try:
                                date_obj = datetime.strptime(date_text, fmt)
                                break
                            except:
                                continue
                        
                        if not date_obj:
                            continue
                        
                        # Filter by date (cutoff based on days parameter)
                        if date_obj < cutoff_date:
                            continue
                        
                        deal['date'] = date_obj.strftime('%Y-%m-%d')
                        deal['date_display'] = date_obj.strftime('%d-%b-%Y')
                    else:
                        continue
                    
                    # Extract buyer
                    buyer_idx = column_map.get('buyer', 1)
                    if len(cells) > buyer_idx:
                        deal['buyer'] = cells[buyer_idx].get_text(strip=True)
                    
                    # Extract seller
                    seller_idx = column_map.get('seller', 2)
                    if len(cells) > seller_idx:
                        deal['seller'] = cells[seller_idx].get_text(strip=True)
                    
                    # Extract quantity
                    qty_idx = column_map.get('quantity', 3)
                    if len(cells) > qty_idx:
                        qty_text = cells[qty_idx].get_text(strip=True).replace(',', '')
                        qty_match = re.search(r'[\d]+', qty_text)
                        if qty_match:
                            deal['quantity'] = int(qty_match.group())
                    
                    # Extract price
                    price_idx = column_map.get('price', 4)
                    if len(cells) > price_idx:
                        price_text = cells[price_idx].get_text(strip=True).replace(',', '').replace('₹', '')
                        price_match = re.search(r'[\d]+\.?\d*', price_text)
                        if price_match:
                            deal['price'] = round(float(price_match.group()), 2)
                    
                    # Extract value
                    value_idx = column_map.get('value', 5)
                    if len(cells) > value_idx:
                        value_text = cells[value_idx].get_text(strip=True).replace(',', '').replace('₹', '')
                        value_match = re.search(r'[\d]+\.?\d*', value_text)
                        if value_match:
                            deal['value'] = round(float(value_match.group()), 2)
                    
                    if deal:
                        bulk_deals.append(deal)
                
                except Exception as e:
                    print(f"Error parsing bulk deal row: {e}")
                    continue
            
            # Sort by date descending (most recent first)
            bulk_deals.sort(key=lambda x: x.get('date', ''), reverse=True)
            
            print(f"Found {len(bulk_deals)} bulk deals for {symbol}")
            return bulk_deals[:100]  # Limit to 100 most recent deals
            
        except Exception as e:
            print(f"Error fetching bulk deals for {symbol}: {e}")
            return []
    
    def _extract_peg(self, soup):
        """Extract PEG ratio"""
        try:
            for stat in soup.find_all('li', class_='flex flex-space-between'):
                label = stat.find('span', class_='name')
                if label and 'PEG' in label.get_text():
                    value_span = stat.find('span', class_='value')
                    if value_span:
                        peg_text = value_span.get_text(strip=True)
                        match = re.search(r'[\d,]+\.?\d*', peg_text.replace(',', ''))
                        if match:
                            return float(match.group())
        except:
            pass
        return 0
    
    def _extract_debt_to_equity(self, soup):
        """Extract Debt to Equity ratio"""
        try:
            for stat in soup.find_all('li', class_='flex flex-space-between'):
                label = stat.find('span', class_='name')
                if label and ('Debt' in label.get_text() and 'Equity' in label.get_text()):
                    value_span = stat.find('span', class_='value')
                    if value_span:
                        debt_text = value_span.get_text(strip=True)
                        match = re.search(r'[\d,]+\.?\d*', debt_text.replace(',', ''))
                        if match:
                            return float(match.group())
        except:
            pass
        return 0
    
    def _extract_profit_margin(self, soup):
        """Extract Profit Margin"""
        try:
            for stat in soup.find_all('li', class_='flex flex-space-between'):
                label = stat.find('span', class_='name')
                if label and ('Profit' in label.get_text() and 'Margin' in label.get_text()):
                    value_span = stat.find('span', class_='value')
                    if value_span:
                        margin_text = value_span.get_text(strip=True).replace('%', '')
                        match = re.search(r'[\d,]+\.?\d*', margin_text.replace(',', ''))
                        if match:
                            return float(match.group())
        except:
            pass
        return 0
    
    def _extract_annual_results(self, soup):
        """Extract annual results table for historical debt analysis"""
        try:
            # Find h2 with "Annual" or "Yearly" text
            annual_h2 = None
            for h2 in soup.find_all('h2'):
                text = h2.get_text().lower()
                if 'annual' in text or 'yearly' in text or ('results' in text and 'annual' in text):
                    annual_h2 = h2
                    break
            
            if not annual_h2:
                return None
            
            # Find table after the h2
            annual_table = None
            found_h2 = False
            for element in soup.descendants:
                if element == annual_h2:
                    found_h2 = True
                    continue
                if found_h2 and hasattr(element, 'name') and element.name == 'table':
                    annual_table = element
                    break
            
            if not annual_table:
                return None
            
            # Extract headers
            headers = []
            thead = annual_table.find('thead')
            if thead:
                header_row = thead.find('tr')
                if header_row:
                    headers = [th.get_text(strip=True) for th in header_row.find_all(['th', 'td'])]
            
            if not headers:
                first_row = annual_table.find('tr')
                if first_row:
                    headers = [th.get_text(strip=True) for th in first_row.find_all(['th', 'td'])]
            
            # Extract rows
            rows = []
            tbody = annual_table.find('tbody')
            table_rows = tbody.find_all('tr') if tbody else annual_table.find_all('tr')[1:]
            
            for tr in table_rows:
                cells = [td.get_text(strip=True) for td in tr.find_all(['td', 'th'])]
                if cells and len(cells) > 0:
                    rows.append(cells)
            
            if headers and rows:
                return {
                    "headers": headers,
                    "rows": rows
                }
            
            return None
        except Exception as e:
            print(f"Error extracting annual results: {e}")
            return None

