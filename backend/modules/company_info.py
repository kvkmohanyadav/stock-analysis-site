import requests
from bs4 import BeautifulSoup
import re
import xml.etree.ElementTree as ET
import os

class CompanyInfo:
    def __init__(self):
        # Twitter API v2 Bearer Token - set via environment variable TWITTER_BEARER_TOKEN
        self.twitter_bearer_token = os.getenv('TWITTER_BEARER_TOKEN', '')
        self.twitter_api_base = "https://api.twitter.com/2"
    
    def get_annual_reports_and_news(self, symbol):
        """
        Fetch news and Twitter feeds for a company
        """
        try:
            news = self._get_company_news(symbol)
            twitter_feeds = self._get_twitter_feeds(symbol)
            
            return {
                "news": news,
                "twitter": twitter_feeds
            }
        except Exception as e:
            print(f"Error fetching company info: {e}")
            return {"news": [], "twitter": []}
    
    
    def _get_company_news(self, symbol):
        """
        Generate news links for the company
        """
        # Generate links to financial news sources
        news_sources = [
            {
                "title": f"{symbol} News - Economic Times",
                "link": f"https://economictimes.indiatimes.com/topic/{symbol}",
                "source": "Economic Times"
            },
            {
                "title": f"{symbol} News - Moneycontrol",
                "link": f"https://www.moneycontrol.com/india/stockpricequote/informationtechnology/{symbol}",
                "source": "Moneycontrol"
            },
            {
                "title": f"{symbol} Analysis - Bloomberg",
                "link": f"https://www.bloomberg.com/quote/{symbol}:IN",
                "source": "Bloomberg"
            },
            {
                "title": f"{symbol} News - Business Standard",
                "link": f"https://www.business-standard.com/topic/{symbol.lower()}",
                "source": "Business Standard"
            },
            {
                "title": f"{symbol} Updates - Yahoo Finance",
                "link": f"https://finance.yahoo.com/quote/{symbol}.NS",
                "source": "Yahoo Finance"
            }
        ]
        return news_sources
    
    def _get_twitter_feeds(self, symbol):
        """
        Fetch tweets about the company from Twitter handles
        Note: This requires Twitter API v2 access. For now, returns structure ready for API integration.
        """
        twitter_feeds = []
        
        handles = [
            {
                "handle": "@REDBOXINDIA",
                "name": "Red Box India"
            },
            {
                "handle": "@ETMarkets",
                "name": "ET Markets"
            }
        ]
        
        # Fetch tweets for each handle
        for handle_info in handles:
            tweets = self._fetch_tweets_from_handle(handle_info["handle"], symbol)
            twitter_feeds.append({
                "handle": handle_info["handle"],
                "name": handle_info["name"],
                "tweets": tweets
            })
        
        return twitter_feeds
    
    def _fetch_tweets_from_handle(self, handle, symbol):
        """
        Fetch recent tweets from a handle mentioning the symbol using Twitter API v2
        """
        try:
            handle_name = handle.replace('@', '')
            tweets = []
            
            # Check if Twitter API Bearer Token is configured
            if not self.twitter_bearer_token:
                print(f"Twitter API Bearer Token not configured. Please set TWITTER_BEARER_TOKEN environment variable.")
                return []
            
            # Step 1: Verify user exists (optional - API will handle invalid users)
            # Step 2: Search for tweets from this user mentioning the symbol
            try:
                # Twitter API v2 search query: tweets from user containing symbol
                query = f"from:{handle_name} ({symbol} OR {symbol}.NS)"
                search_url = f"{self.twitter_api_base}/tweets/search/recent"
                headers = {
                    'Authorization': f'Bearer {self.twitter_bearer_token}'
                }
                params = {
                    'query': query,
                    'max_results': 15,
                    'tweet.fields': 'created_at,text,public_metrics',
                    'user.fields': 'username',
                    'expansions': 'author_id'
                }
                
                response = requests.get(search_url, headers=headers, params=params, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    if 'data' in data and isinstance(data['data'], list) and len(data['data']) > 0:
                        tweet_data = data['data']
                        for tweet in tweet_data:
                            if 'text' in tweet:
                                tweets.append({
                                    "text": tweet['text'][:280],
                                    "author": handle_name
                                })
                        print(f"Found {len(tweets)} tweets for {symbol} from {handle_name} via Twitter API v2")
                    else:
                        print(f"No tweets found for {symbol} from {handle_name}")
                elif response.status_code == 401:
                    print("Twitter API authentication failed. Please check your Bearer Token.")
                    return []
                elif response.status_code == 429:
                    print("Twitter API rate limit exceeded. Please wait before trying again.")
                    return []
                else:
                    print(f"Error fetching tweets: {response.status_code} - {response.text[:200]}")
                    return []
                    
            except Exception as e:
                print(f"Error searching tweets from {handle_name} for {symbol}: {e}")
                import traceback
                traceback.print_exc()
                return []
            
            return tweets[:15]
            
        except Exception as e:
            print(f"Error fetching tweets from {handle} for {symbol}: {e}")
            import traceback
            traceback.print_exc()
            return []
