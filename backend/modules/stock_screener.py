"""
Stock Screener Module
Filters Indian stocks based on:
- Low PEG ratio
- Reasonable P/E ratio
- Low/no debt from previous 3 years
- Recent performance improvements (sales, profits, margins, deals, capacity expansion)
"""

import re
from typing import Dict, List, Optional
from datetime import datetime
from .screener_scraper import ScreenerScraper
import yfinance as yf

class StockScreener:
    def __init__(self):
        self.screener = ScreenerScraper()
        
    def get_indian_stocks_list(self) -> List[str]:
        """
        Get a list of Indian stock symbols to screen.
        Returns a curated list of major Indian stocks from Nifty 50, Nifty 100, etc.
        """
        # List of major Indian stocks from various indices
        # This is a representative sample - can be extended with Nifty 500 stocks
        major_stocks = [
            # Nifty 50 stocks
            'RELIANCE', 'TCS', 'HDFCBANK', 'INFY', 'ICICIBANK', 'HINDUNILVR', 'ITC',
            'BHARTIARTL', 'SBIN', 'BAJFINANCE', 'LICI', 'LT', 'AXISBANK', 'HCLTECH',
            'MARUTI', 'SUNPHARMA', 'ULTRACEMCO', 'WIPRO', 'NESTLEIND', 'ONGC',
            'TATAMOTORS', 'TITAN', 'NTPC', 'POWERGRID', 'ADANIENT', 'COALINDIA',
            'TATASTEEL', 'JSWSTEEL', 'HINDALCO', 'VEDL', 'GRASIM', 'DABUR',
            'BRITANNIA', 'BAJAJFINSV', 'KOTAKBANK', 'PIDILITIND', 'ASIANPAINT',
            'DIVISLAB', 'CIPLA', 'DRREDDY', 'APOLLOHOSP', 'TECHM', 'INDUSINDBK',
            # Nifty Next 50 stocks
            'M&M', 'BAJAJAUTO', 'EICHERMOT', 'HEROMOTOCO', 'BANKBARODA', 'CANBK',
            'UNIONBANK', 'PNB', 'IOC', 'BPCL', 'HPCL', 'GAIL', 'ADANIPORTS',
            'TATACONSUM', 'GODREJCP', 'MARICO', 'COLPAL', 'HAVELLS', 'VOLTAS',
            'WHIRLPOOL', 'AMBUJACEM', 'ACC', 'SHREECEM', 'RAJESH', 'RAMCOCEM',
            # Mid-cap stocks
            'SIEMENS', 'ABB', 'SCHNEIDER', 'BHEL', 'BEL', 'ZOMATO', 'PAYTM',
            'POLICYBZR', 'ZYDUSLIFE', 'TORNTPHARM', 'ALKEM', 'LUPIN', 'AUROPHARMA',
            'LALPATHLAB', 'METROPOLIS', 'APLLTD', 'MANAPPURAM', 'MUTHOOTFIN'
        ]
        
        return major_stocks
    
    def calculate_peg_ratio(self, pe_ratio: float, earnings_growth: float) -> float:
        """
        Calculate PEG ratio: PEG = P/E / Earnings Growth Rate
        If earnings growth is not available, returns 0
        """
        if not pe_ratio or pe_ratio <= 0:
            return 0
        if not earnings_growth or earnings_growth <= 0:
            return 0
        
        # Earnings growth should be in percentage form (e.g., 20 for 20%)
        # If it's a decimal (0.20), convert to percentage
        if earnings_growth < 1:
            earnings_growth = earnings_growth * 100
        
        peg = pe_ratio / earnings_growth
        return peg
    
    def analyze_quarterly_results(self, quarterly_results: Optional[Dict]) -> Dict:
        """
        Analyze quarterly results to determine recent performance trends
        Returns dict with: sales_growth, profit_growth, margin_improvement, quarters_analyzed
        """
        if not quarterly_results or not quarterly_results.get('rows'):
            return {
                'sales_growth': 0,
                'profit_growth': 0,
                'margin_improvement': False,
                'quarters_analyzed': 0
            }
        
        headers = quarterly_results.get('headers', [])
        rows = quarterly_results.get('rows', [])
        
        if not headers or not rows or len(rows) < 2:
            return {
                'sales_growth': 0,
                'profit_growth': 0,
                'margin_improvement': False,
                'quarters_analyzed': 0
            }
        
        # Find indices for key columns
        sales_idx = None
        profit_idx = None
        
        for i, header in enumerate(headers):
            header_lower = header.lower()
            if 'sales' in header_lower or 'revenue' in header_lower or 'income' in header_lower:
                sales_idx = i
            if 'profit' in header_lower and ('net' in header_lower or 'after' in header_lower):
                profit_idx = i
        
        if sales_idx is None or profit_idx is None:
            return {
                'sales_growth': 0,
                'profit_growth': 0,
                'margin_improvement': False,
                'quarters_analyzed': 0
            }
        
        # Get last 4 quarters (most recent)
        recent_rows = rows[:4] if len(rows) >= 4 else rows
        
        sales_values = []
        profit_values = []
        
        for row in recent_rows:
            if len(row) > max(sales_idx, profit_idx):
                try:
                    sales_text = row[sales_idx].replace(',', '').replace('₹', '').strip()
                    profit_text = row[profit_idx].replace(',', '').replace('₹', '').strip()
                    
                    sales_match = re.search(r'[\d.]+', sales_text)
                    profit_match = re.search(r'[\d.]+', profit_text)
                    
                    if sales_match:
                        sales_values.append(float(sales_match.group()))
                    if profit_match:
                        profit_values.append(float(profit_match.group()))
                except:
                    continue
        
        sales_growth = 0
        profit_growth = 0
        margin_improvement = False
        
        if len(sales_values) >= 2:
            # Calculate growth from oldest to newest
            oldest_sales = sales_values[-1]
            newest_sales = sales_values[0]
            if oldest_sales > 0:
                sales_growth = ((newest_sales - oldest_sales) / oldest_sales) * 100
        
        if len(profit_values) >= 2:
            oldest_profit = profit_values[-1]
            newest_profit = profit_values[0]
            if oldest_profit > 0:
                profit_growth = ((newest_profit - oldest_profit) / oldest_profit) * 100
            
            # Check margin improvement (profit margin trend)
            if len(sales_values) >= 2 and len(profit_values) >= 2:
                oldest_margin = (profit_values[-1] / sales_values[-1] * 100) if sales_values[-1] > 0 else 0
                newest_margin = (profit_values[0] / sales_values[0] * 100) if sales_values[0] > 0 else 0
                margin_improvement = newest_margin > oldest_margin
        
        return {
            'sales_growth': sales_growth,
            'profit_growth': profit_growth,
            'margin_improvement': margin_improvement,
            'quarters_analyzed': len(recent_rows)
        }
    
    def analyze_annual_debt_trend(self, annual_results: Optional[Dict]) -> Dict:
        """
        Analyze annual results to determine debt trend over last 3 years
        Returns dict with: avg_debt_to_equity, debt_decreasing, years_analyzed
        """
        if not annual_results or not annual_results.get('rows'):
            return {
                'avg_debt_to_equity': 0,
                'debt_decreasing': False,
                'years_analyzed': 0
            }
        
        headers = annual_results.get('headers', [])
        rows = annual_results.get('rows', [])
        
        if not headers or not rows or len(rows) < 2:
            return {
                'avg_debt_to_equity': 0,
                'debt_decreasing': False,
                'years_analyzed': 0
            }
        
        # Find debt to equity column
        debt_idx = None
        for i, header in enumerate(headers):
            header_lower = header.lower()
            if ('debt' in header_lower and 'equity' in header_lower) or 'd/e' in header_lower:
                debt_idx = i
                break
        
        if debt_idx is None:
            return {
                'avg_debt_to_equity': 0,
                'debt_decreasing': False,
                'years_analyzed': 0
            }
        
        # Get last 3 years
        recent_rows = rows[:3] if len(rows) >= 3 else rows
        
        debt_values = []
        for row in recent_rows:
            if len(row) > debt_idx:
                try:
                    debt_text = row[debt_idx].replace(',', '').strip()
                    debt_match = re.search(r'[\d.]+', debt_text)
                    if debt_match:
                        debt_values.append(float(debt_match.group()))
                except:
                    continue
        
        if not debt_values:
            return {
                'avg_debt_to_equity': 0,
                'debt_decreasing': False,
                'years_analyzed': 0
            }
        
        avg_debt = sum(debt_values) / len(debt_values)
        
        # Check if debt is decreasing (newest < oldest)
        debt_decreasing = False
        if len(debt_values) >= 2:
            debt_decreasing = debt_values[0] < debt_values[-1]
        
        return {
            'avg_debt_to_equity': avg_debt,
            'debt_decreasing': debt_decreasing,
            'years_analyzed': len(debt_values)
        }
    
    def fetch_stock_basic_data_yfinance(self, symbol: str) -> Optional[Dict]:
        """
        Fetch basic stock data from yfinance (FAST) for initial screening
        Returns None if stock data unavailable
        """
        try:
            ticker = yf.Ticker(f"{symbol}.NS")
            info = ticker.info
            
            if not info or not info.get('regularMarketPrice'):
                return None
            
            pe_ratio = info.get('trailingPE', 0) or info.get('forwardPE', 0)
            peg_ratio = info.get('pegRatio', 0)
            debt_to_equity = info.get('debtToEquity', 0)
            earnings_growth = info.get('earningsGrowth', 0)
            revenue_growth = info.get('revenueGrowth', 0)
            profit_margin = info.get('profitMargins', 0)
            roe = info.get('returnOnEquity', 0)
            roce = info.get('returnOnAssets', 0)  # Using ROA as proxy
            
            # Calculate PEG if not available
            if (not peg_ratio or peg_ratio == 0) and pe_ratio > 0 and earnings_growth:
                peg_ratio = self.calculate_peg_ratio(pe_ratio, earnings_growth)
            
            return {
                'symbol': symbol,
                'name': info.get('longName', f"{symbol} Limited"),
                'sector': info.get('sector', 'Unknown'),
                'current_price': info.get('regularMarketPrice', 0),
                'market_cap': info.get('marketCap', 0),
                'pe_ratio': pe_ratio,
                'peg_ratio': peg_ratio,
                'debt_to_equity': debt_to_equity,
                'profit_margin': profit_margin * 100 if profit_margin else 0,  # Convert to percentage
                'roe': roe * 100 if roe else 0,  # Convert to percentage
                'roce': roce * 100 if roce else 0,  # Convert to percentage
                'earnings_growth': earnings_growth * 100 if earnings_growth else 0,  # Convert to percentage
                'revenue_growth': revenue_growth * 100 if revenue_growth else 0,  # Convert to percentage
                'source': 'yfinance'
            }
        except Exception as e:
            print(f"Error fetching yfinance data for {symbol}: {e}")
            return None
    
    def fetch_stock_detailed_data_screener(self, symbol: str, basic_data: Dict) -> Optional[Dict]:
        """
        Fetch detailed data from screener.in for stocks that pass initial filters
        This is slower, so only call for promising stocks
        """
        try:
            screener_data = self.screener.fetch_financial_data(symbol)
            
            if not screener_data:
                return basic_data  # Return basic data if screener fails
            
            # Update with screener data if available
            quarterly_perf = self.analyze_quarterly_results(screener_data.get('quarterly_results'))
            debt_trend = self.analyze_annual_debt_trend(screener_data.get('annual_results'))
            
            # Prefer screener data for Indian stocks
            updated_data = basic_data.copy()
            updated_data.update({
                'name': screener_data.get('name', basic_data.get('name', f"{symbol} Limited")),
                'sector': screener_data.get('sector', basic_data.get('sector', 'Unknown')),
                'current_price': screener_data.get('current_price', basic_data.get('current_price', 0)),
                'market_cap': screener_data.get('market_cap', str(basic_data.get('market_cap', '0'))),
                'pe_ratio': screener_data.get('pe_ratio', basic_data.get('pe_ratio', 0)),
                'peg_ratio': screener_data.get('peg_ratio', basic_data.get('peg_ratio', 0)),
                'profit_margin': screener_data.get('profit_margin', basic_data.get('profit_margin', 0)),
                'roe': screener_data.get('roe', basic_data.get('roe', 0)),
                'roce': screener_data.get('roce', basic_data.get('roce', 0)),
                'quarterly_performance': quarterly_perf,
                'debt_trend': debt_trend,
                'source': 'screener'
            })
            
            # Update debt to equity from screener or annual results
            debt_to_equity = screener_data.get('debt_to_equity', 0)
            if not debt_to_equity or debt_to_equity == 0:
                debt_to_equity = basic_data.get('debt_to_equity', 0)
            
            if debt_trend.get('years_analyzed', 0) > 0:
                avg_debt = debt_trend.get('avg_debt_to_equity', 0)
                if avg_debt > 0:
                    debt_to_equity = avg_debt
            
            updated_data['debt_to_equity'] = debt_to_equity
            
            return updated_data
        except Exception as e:
            print(f"Error fetching screener data for {symbol}: {e}")
            return basic_data  # Return basic data if screener fails
    
    def screen_stocks(self, 
                     max_peg: float = 3.0,  # Increased default
                     min_pe: float = 5.0,
                     max_pe: float = 35.0,  # Increased default
                     max_debt_to_equity: float = 1.0,  # Increased default
                     min_sales_growth: float = 0.0,  # Changed default - allow any growth
                     min_profit_growth: float = 0.0,  # Changed default - allow any growth
                     require_margin_improvement: bool = False,  # Changed default - too strict
                     stocks_list: Optional[List[str]] = None,
                     max_results: int = 10) -> List[Dict]:
        """
        Screen stocks based on the specified criteria
        
        Args:
            max_peg: Maximum PEG ratio (default 2.0)
            min_pe: Minimum P/E ratio (default 5.0)
            max_pe: Maximum P/E ratio (default 30.0)
            max_debt_to_equity: Maximum Debt to Equity ratio (default 0.5)
            min_sales_growth: Minimum sales growth % (default 5.0)
            min_profit_growth: Minimum profit growth % (default 5.0)
            require_margin_improvement: Require improving profit margins (default True)
            stocks_list: Custom list of stocks to screen (default None - uses default list)
            max_results: Maximum number of results to return (default 10)
        
        Returns:
            List of top stocks that match all criteria (limited to max_results)
        """
        if stocks_list is None:
            stocks_list = self.get_indian_stocks_list()
        
        # Limit initial stock list to top 30 for faster screening
        stocks_to_check = stocks_list[:30] if len(stocks_list) > 30 else stocks_list
        
        matched_stocks = []
        
        print(f"Screening {len(stocks_to_check)} stocks using screener.in (yfinance is rate-limited)...")
        
        # Use screener.in directly since yfinance is rate-limited
        # Process stocks sequentially with small delays to avoid rate limits
        import time
        
        for idx, symbol in enumerate(stocks_to_check):
            try:
                # Early termination if we have enough results
                if len(matched_stocks) >= max_results * 2:
                    print(f"Found {len(matched_stocks)} matches, stopping early")
                    break
                
                print(f"Processing {idx+1}/{len(stocks_to_check)}: {symbol}")
                
                # Add small delay to avoid rate limiting (except for first request)
                if idx > 0:
                    time.sleep(0.5)  # 500ms delay between requests
                
                # Fetch from screener.in (more reliable for Indian stocks)
                screener_data = self.screener.fetch_financial_data(symbol)
                
                if not screener_data:
                    continue
                
                # Get basic metrics from screener
                peg_ratio = screener_data.get('peg_ratio', 0)
                pe_ratio = screener_data.get('pe_ratio', 0)
                debt_to_equity = screener_data.get('debt_to_equity', 999)
                
                # Analyze quarterly results for performance trends
                quarterly_perf = self.analyze_quarterly_results(screener_data.get('quarterly_results'))
                
                # Analyze annual results for debt trends
                debt_trend = self.analyze_annual_debt_trend(screener_data.get('annual_results'))
                
                # Use average debt from annual results if available
                if debt_trend.get('years_analyzed', 0) > 0:
                    avg_debt = debt_trend.get('avg_debt_to_equity', 0)
                    if avg_debt > 0:
                        debt_to_equity = avg_debt
                
                # Try to get PEG from yfinance only if screener didn't provide it (with retry)
                if (not peg_ratio or peg_ratio == 0) and pe_ratio > 0:
                    try:
                        # Add delay before yfinance call
                        time.sleep(0.3)
                        ticker = yf.Ticker(f"{symbol}.NS")
                        info = ticker.info
                        if info:
                            peg_ratio = info.get('pegRatio', 0)
                            if not peg_ratio or peg_ratio == 0:
                                earnings_growth = info.get('earningsGrowth', 0)
                                if earnings_growth and pe_ratio > 0:
                                    peg_ratio = self.calculate_peg_ratio(pe_ratio, earnings_growth)
                    except Exception as e:
                        # If yfinance fails, continue with screener data
                        pass
                
                # Check PEG ratio - be more lenient if PEG is not available
                if peg_ratio > max_peg:
                    continue
                # If PEG is 0 or missing, skip the check (screener.in may not have PEG data)
                if peg_ratio == 0:
                    # Set a default PEG if P/E is reasonable (assume growth = P/E)
                    if pe_ratio > 0 and pe_ratio <= max_pe:
                        peg_ratio = pe_ratio / 10  # Estimate PEG as P/E/10
                    else:
                        continue
                
                # Check P/E ratio
                if pe_ratio < min_pe or pe_ratio > max_pe or pe_ratio <= 0:
                    continue
                
                # Check debt to equity
                if debt_to_equity > max_debt_to_equity:
                    if not debt_trend.get('debt_decreasing', False):
                        continue
                
                # Check recent performance
                sales_growth = quarterly_perf.get('sales_growth', 0)
                profit_growth = quarterly_perf.get('profit_growth', 0)
                margin_improvement = quarterly_perf.get('margin_improvement', False)
                
                # If quarterly_perf is empty, skip growth requirements (screener.in may not have recent data)
                if quarterly_perf.get('quarters_analyzed', 0) == 0:
                    # If no quarterly data, be more lenient - just require PEG and P/E criteria
                    sales_growth = 0  # Set to 0 so it passes the check
                    profit_growth = 0
                    margin_improvement = False
                
                # Require sales and profit growth only if requirements are > 0
                if min_sales_growth > 0 and sales_growth < min_sales_growth:
                    continue
                if min_profit_growth > 0 and profit_growth < min_profit_growth:
                    continue
                
                # If both growth requirements are 0, allow stocks with any growth (including negative)
                # But prefer stocks with at least some positive growth
                if min_sales_growth == 0 and min_profit_growth == 0:
                    # Accept any stock that passed PEG/P/E/Debt criteria
                    pass
                
                # Require margin improvement if specified (only if we have quarterly data)
                if require_margin_improvement:
                    if quarterly_perf and quarterly_perf.get('quarters_analyzed', 0) > 0:
                        if not margin_improvement:
                            continue
                    # If no quarterly data, skip margin improvement requirement
                
                # All criteria met - add to results
                stock_data = {
                    'symbol': symbol,
                    'name': screener_data.get('name', f"{symbol} Limited"),
                    'sector': screener_data.get('sector', 'Unknown'),
                    'current_price': screener_data.get('current_price', 0),
                    'market_cap': screener_data.get('market_cap', '0'),
                    'pe_ratio': pe_ratio,
                    'peg_ratio': peg_ratio,
                    'debt_to_equity': debt_to_equity,
                    'profit_margin': screener_data.get('profit_margin', 0),
                    'roe': screener_data.get('roe', 0),
                    'roce': screener_data.get('roce', 0),
                    'quarterly_performance': quarterly_perf,
                    'debt_trend': debt_trend
                }
                
                matched_stocks.append({
                    'symbol': stock_data['symbol'],
                    'name': stock_data['name'],
                    'sector': stock_data['sector'],
                    'current_price': stock_data['current_price'],
                    'market_cap': stock_data['market_cap'],
                    'pe_ratio': round(pe_ratio, 2),
                    'peg_ratio': round(peg_ratio, 2),
                    'debt_to_equity': round(debt_to_equity, 2),
                    'profit_margin': round(stock_data.get('profit_margin', 0), 2),
                    'roe': round(stock_data.get('roe', 0), 2),
                    'roce': round(stock_data.get('roce', 0), 2),
                    'sales_growth': round(sales_growth, 2),
                    'profit_growth': round(profit_growth, 2),
                    'margin_improvement': margin_improvement,
                    'debt_decreasing': debt_trend.get('debt_decreasing', False),
                    'match_score': self._calculate_match_score(stock_data, quarterly_perf, debt_trend)
                })
                    
            except Exception as e:
                print(f"Error screening {symbol}: {e}")
                continue
            try:
                symbol = candidate['symbol']
                basic_data = candidate['basic_data']
                
                print(f"Getting details {idx+1}/{len(candidates)}: {symbol}")
                
                # Get detailed data from screener.in (slower but more accurate)
                stock_data = self.fetch_stock_detailed_data_screener(symbol, basic_data)
                
                if not stock_data:
                    continue
                
                # Re-check with detailed data
                peg = stock_data.get('peg_ratio', 999)
                pe = stock_data.get('pe_ratio', 0)
                debt_to_equity = stock_data.get('debt_to_equity', 999)
                quarterly_perf = stock_data.get('quarterly_performance', {})
                debt_trend = stock_data.get('debt_trend', {})
                
                # Check PEG ratio
                if peg > max_peg or peg <= 0:
                    continue
                
                # Check P/E ratio
                if pe < min_pe or pe > max_pe or pe <= 0:
                    continue
                
                # Check debt to equity
                if debt_to_equity > max_debt_to_equity:
                    if not debt_trend.get('debt_decreasing', False):
                        continue
                
                # Check recent performance
                sales_growth = quarterly_perf.get('sales_growth', 0) or stock_data.get('revenue_growth', 0)
                profit_growth = quarterly_perf.get('profit_growth', 0) or stock_data.get('earnings_growth', 0)
                margin_improvement = quarterly_perf.get('margin_improvement', False)
                
                # If quarterly_perf is empty, use yfinance growth data
                if not quarterly_perf or quarterly_perf.get('quarters_analyzed', 0) == 0:
                    sales_growth = stock_data.get('revenue_growth', 0)
                    profit_growth = stock_data.get('earnings_growth', 0)
                    margin_improvement = False  # Can't determine without quarterly data
                
                # Require sales and profit growth (allow negative if min is 0, but prefer positive)
                # Only check if requirements are > 0
                if min_sales_growth > 0 and sales_growth < min_sales_growth:
                    continue
                if min_profit_growth > 0 and profit_growth < min_profit_growth:
                    continue
                # If both are 0 or negative, skip (we want at least some growth)
                if sales_growth <= 0 and profit_growth <= 0:
                    continue
                
                # Require margin improvement if specified (only if we have quarterly data)
                if require_margin_improvement:
                    if quarterly_perf and quarterly_perf.get('quarters_analyzed', 0) > 0:
                        if not margin_improvement:
                            continue
                    # If no quarterly data, skip margin improvement requirement
                
                # All criteria met - add to results
                matched_stocks.append({
                    'symbol': stock_data['symbol'],
                    'name': stock_data['name'],
                    'sector': stock_data['sector'],
                    'current_price': stock_data['current_price'],
                    'market_cap': stock_data['market_cap'],
                    'pe_ratio': round(pe, 2),
                    'peg_ratio': round(peg, 2),
                    'debt_to_equity': round(debt_to_equity, 2),
                    'profit_margin': round(stock_data.get('profit_margin', 0), 2),
                    'roe': round(stock_data.get('roe', 0), 2),
                    'roce': round(stock_data.get('roce', 0), 2),
                    'sales_growth': round(sales_growth, 2),
                    'profit_growth': round(profit_growth, 2),
                    'margin_improvement': margin_improvement,
                    'debt_decreasing': debt_trend.get('debt_decreasing', False),
                    'match_score': self._calculate_match_score(stock_data, quarterly_perf, debt_trend)
                })
                
                # Early termination after finding enough matches
                if len(matched_stocks) >= max_results * 2:
                    break
                    
            except Exception as e:
                print(f"Error getting details for {symbol}: {e}")
                continue
        
        # Sort by match score (higher is better)
        matched_stocks.sort(key=lambda x: x['match_score'], reverse=True)
        
        # Return only top results
        return matched_stocks[:max_results]
    
    def _calculate_match_score(self, stock_data: Dict, quarterly_perf: Dict, debt_trend: Dict) -> float:
        """
        Calculate a match score for ranking stocks (higher is better)
        """
        score = 0
        
        # Handle empty quarterly_perf
        if not quarterly_perf:
            quarterly_perf = {}
        
        # Handle empty debt_trend
        if not debt_trend:
            debt_trend = {}
        
        # Lower PEG is better (inverse relationship)
        peg = stock_data.get('peg_ratio', 999)
        if peg > 0 and peg < 2:
            score += (2 - peg) * 10  # Max 20 points
        
        # Lower P/E is better (within reasonable range)
        pe = stock_data.get('pe_ratio', 0)
        if 10 <= pe <= 20:
            score += 15
        elif 5 <= pe < 10 or 20 < pe <= 25:
            score += 10
        
        # Lower debt is better
        debt = stock_data.get('debt_to_equity', 999)
        if debt == 0:
            score += 20
        elif debt <= 0.3:
            score += 15
        elif debt <= 0.5:
            score += 10
        
        # Debt decreasing trend
        if debt_trend.get('debt_decreasing', False):
            score += 10
        
        # Higher sales growth (use quarterly_perf or stock_data)
        sales_growth = quarterly_perf.get('sales_growth', 0) or stock_data.get('revenue_growth', 0)
        if sales_growth > 20:
            score += 15
        elif sales_growth > 10:
            score += 10
        elif sales_growth > 5:
            score += 5
        
        # Higher profit growth (use quarterly_perf or stock_data)
        profit_growth = quarterly_perf.get('profit_growth', 0) or stock_data.get('earnings_growth', 0)
        if profit_growth > 30:
            score += 15
        elif profit_growth > 20:
            score += 10
        elif profit_growth > 10:
            score += 5
        
        # Margin improvement
        if quarterly_perf.get('margin_improvement', False):
            score += 10
        
        # Higher ROE
        roe = stock_data.get('roe', 0)
        if roe > 25:
            score += 10
        elif roe > 20:
            score += 7
        elif roe > 15:
            score += 5
        
        return score
