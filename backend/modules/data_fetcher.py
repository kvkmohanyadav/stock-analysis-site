import requests
import random
from datetime import datetime
import json
import os
import yfinance as yf

class DataFetcher:
    def __init__(self):
        self.cache_dir = "cache"
        os.makedirs(self.cache_dir, exist_ok=True)
    
    def fetch_nifty50(self):
        try:
            # Fetch real Nifty50 data from Yahoo Finance
            nifty = yf.Ticker("^NSEI")
            info = nifty.history(period="1d", interval="1m")
            
            if not info.empty:
                current = info['Close'].iloc[-1]
                prev_close = nifty.info.get('previousClose', current)
                change = current - prev_close
                change_pct = (change / prev_close) * 100
                
                return {
                    "index_name": "NIFTY 50",
                    "current_value": round(current, 2),
                    "change": round(change, 2),
                    "change_percent": round(change_pct, 2),
                    "timestamp": datetime.now().isoformat()
                }
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
            # Fetch real Sensex data from Yahoo Finance
            sensex = yf.Ticker("^BSESN")
            info = sensex.history(period="1d", interval="1m")
            
            if not info.empty:
                current = info['Close'].iloc[-1]
                prev_close = sensex.info.get('previousClose', current)
                change = current - prev_close
                change_pct = (change / prev_close) * 100
                
                return {
                    "index_name": "SENSEX",
                    "current_value": round(current, 2),
                    "change": round(change, 2),
                    "change_percent": round(change_pct, 2),
                    "timestamp": datetime.now().isoformat()
                }
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
