import requests
import random
from datetime import datetime
import json
import os
import yfinance as yf

# NSE and BSE libraries
try:
    from nsepython import nse_get_index_quote
    from nsetools import Nse
    NSE_AVAILABLE = True
except ImportError:
    NSE_AVAILABLE = False
    print("Warning: nsepython or nsetools not available. Install with: pip install nsepython nsetools")

try:
    from bsedata.bse import BSE
    BSE_AVAILABLE = True
except ImportError:
    BSE_AVAILABLE = False
    print("Warning: bsedata not available. Install with: pip install bsedata")

class DataFetcher:
    def __init__(self):
        self.cache_dir = "cache"
        os.makedirs(self.cache_dir, exist_ok=True)
        if NSE_AVAILABLE:
            try:
                self.nse = Nse()
            except:
                self.nse = None
        else:
            self.nse = None
        
        if BSE_AVAILABLE:
            try:
                self.bse = BSE()
            except:
                self.bse = None
        else:
            self.bse = None
    
    def fetch_nifty50(self):
        try:
            if NSE_AVAILABLE:
                # Try nsepython first - NIFTY 50
                try:
                    quote = nse_get_index_quote("NIFTY 50")
                    if quote and isinstance(quote, dict):
                        # nsepython returns dict with keys like 'last', 'percChange', etc.
                        # Values may have commas, so we need to clean them
                        last_str = str(quote.get('last', quote.get('lastPrice', '0'))).replace(',', '')
                        prev_close_str = str(quote.get('previousClose', '0')).replace(',', '')
                        change_pct_str = str(quote.get('percChange', quote.get('pChange', '0'))).replace(',', '')
                        
                        current = float(last_str)
                        change_pct = float(change_pct_str)
                        prev_close = float(prev_close_str)
                        change = current - prev_close if prev_close > 0 else 0
                        
                        if current > 0:
                            return {
                                "index_name": "NIFTY 50",
                                "current_value": round(current, 2),
                                "change": round(change, 2),
                                "change_percent": round(change_pct, 2),
                                "timestamp": datetime.now().isoformat()
                            }
                except Exception as e:
                    print(f"nsepython NIFTY50 error: {e}")
                
                # Try nsetools as fallback
                if self.nse:
                    try:
                        quote = self.nse.get_index_quote('NIFTY 50')
                        if quote and isinstance(quote, dict):
                            current = float(quote.get('last', quote.get('lastPrice', quote.get('value', 0))))
                            change_pct = float(quote.get('percChange', quote.get('pChange', 0)))
                            prev_close = float(quote.get('previousClose', 0))
                            change = current - prev_close if prev_close > 0 else float(quote.get('change', 0))
                            
                            if current > 0:
                                return {
                                    "index_name": "NIFTY 50",
                                    "current_value": round(current, 2),
                                    "change": round(change, 2),
                                    "change_percent": round(change_pct, 2),
                                    "timestamp": datetime.now().isoformat()
                                }
                    except Exception as e:
                        print(f"nsetools NIFTY50 error: {e}")
        except Exception as e:
            print(f"Error fetching Nifty50: {e}")
        
        # Fallback: return mock data if API fails
        return {
            "index_name": "NIFTY 50",
            "current_value": round(22000 + random.uniform(-200, 200), 2),
            "change": round(random.uniform(-200, 200), 2),
            "change_percent": round(random.uniform(-1, 1), 2),
            "timestamp": datetime.now().isoformat()
        }
    
    def fetch_sensex(self):
        try:
            # Try bsedata first for SENSEX (BSE index)
            if BSE_AVAILABLE and self.bse:
                try:
                    # Get indices from market_cap/broad category where SENSEX is located
                    data = self.bse.getIndices('market_cap/broad')
                    if data and 'indices' in data:
                        # Find SENSEX in the indices list
                        sensex_data = None
                        for idx in data['indices']:
                            if 'SENSEX' in idx.get('name', '').upper() and 'BSE SENSEX' in idx.get('name', ''):
                                sensex_data = idx
                                break
                        
                        if sensex_data:
                            # Extract values - bsedata returns values with commas
                            current_str = str(sensex_data.get('currentValue', '0')).replace(',', '')
                            change_str = str(sensex_data.get('change', '0')).replace(',', '')
                            change_pct_str = str(sensex_data.get('pChange', '0')).replace(',', '')
                            
                            current = float(current_str)
                            change = float(change_str)
                            change_pct = float(change_pct_str)
                            
                            if current > 0:
                                return {
                                    "index_name": "SENSEX",
                                    "current_value": round(current, 2),
                                    "change": round(change, 2),
                                    "change_percent": round(change_pct, 2),
                                    "timestamp": datetime.now().isoformat()
                                }
                except Exception as e:
                    print(f"bsedata SENSEX error: {e}")
            
            # Fallback: Try nsepython for SENSEX (in case it has BSE data)
            if NSE_AVAILABLE:
                sensex_names = ["S&P BSE SENSEX", "SENSEX"]
                for sensex_name in sensex_names:
                    try:
                        quote = nse_get_index_quote(sensex_name)
                        if quote and isinstance(quote, dict):
                            # Values may have commas, so we need to clean them
                            last_str = str(quote.get('last', quote.get('lastPrice', '0'))).replace(',', '')
                            prev_close_str = str(quote.get('previousClose', '0')).replace(',', '')
                            change_pct_str = str(quote.get('percChange', quote.get('pChange', '0'))).replace(',', '')
                            
                            current = float(last_str)
                            change_pct = float(change_pct_str)
                            prev_close = float(prev_close_str)
                            change = current - prev_close if prev_close > 0 else 0
                            
                            if current > 0:
                                return {
                                    "index_name": "SENSEX",
                                    "current_value": round(current, 2),
                                    "change": round(change, 2),
                                    "change_percent": round(change_pct, 2),
                                    "timestamp": datetime.now().isoformat()
                                }
                    except:
                        continue
        except Exception as e:
            print(f"Error fetching Sensex: {e}")
        
        # Fallback: return mock data if API fails
        return {
            "index_name": "SENSEX",
            "current_value": round(73000 + random.uniform(-300, 300), 2),
            "change": round(random.uniform(-300, 300), 2),
            "change_percent": round(random.uniform(-1, 1), 2),
            "timestamp": datetime.now().isoformat()
        }
    
    def fetch_historical_data(self, symbol, period="1y"):
        """
        Fetch historical price data for a stock
        period options: "1y", "3y", "5y", "max" (all time)
        """
        try:
            stock = yf.Ticker(f"{symbol}.NS")  # .NS for NSE stocks
            data = stock.history(period=period)
            
            if data.empty:
                # Try without .NS suffix
                stock = yf.Ticker(symbol)
                data = stock.history(period=period)
            
            if data.empty:
                return None
            
            # Convert to list of dictionaries with date and close price
            historical_data = []
            for date, row in data.iterrows():
                historical_data.append({
                    "date": date.strftime("%Y-%m-%d"),
                    "open": round(float(row['Open']), 2),
                    "high": round(float(row['High']), 2),
                    "low": round(float(row['Low']), 2),
                    "close": round(float(row['Close']), 2),
                    "volume": int(row['Volume'])
                })
            
            return historical_data
            
        except Exception as e:
            print(f"Error fetching historical data for {symbol}: {e}")
            return None
