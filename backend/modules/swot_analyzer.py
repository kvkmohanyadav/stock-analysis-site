import random
from datetime import datetime
import yfinance as yf
from .screener_scraper import ScreenerScraper

class SWOTAnalyzer:
    def __init__(self):
        self.screener = ScreenerScraper()
    
    def _fetch_stock_data(self, symbol):
        """Fetch real stock data from screener.in first, fallback to yfinance"""
        try:
            # Try screener.in first for accurate Indian stock data
            screener_data = self.screener.fetch_financial_data(symbol)
            if screener_data and screener_data.get('current_price', 0) > 0:
                return {
                    "symbol": symbol,
                    "name": screener_data.get('name', f"{symbol} Limited"),
                    "sector": screener_data.get('sector', 'Unknown'),
                    "current_price": screener_data.get('current_price', 0),
                    "previous_close": screener_data.get('current_price', 0),  # Use current as proxy
                    "market_cap": screener_data.get('market_cap', '0'),
                    "pe_ratio": screener_data.get('pe_ratio', 0),
                    "forward_pe": 0,
                    "peg_ratio": 0,
                    "dividend_yield": screener_data.get('dividend_yield', 0),
                    "roe": screener_data.get('roe', 0),
                    "roce": screener_data.get('roce', 0),
                    "roa": 0,
                    "book_value": screener_data.get('book_value', 0),
                    "debt_to_equity": 0,
                    "profit_margin": 0,
                    "gross_margin": 0,
                    "revenue_growth": 0,
                    "earnings_growth": 0,
                    "beta": 1.0,
                    "52w_high": screener_data.get('52w_high', 0),
                    "52w_low": screener_data.get('52w_low', 0),
                    "volume": 0,
                    "avg_volume": 0,
                    "target_price": 0,
                    "peer_comparison": screener_data.get('peer_comparison')
                }
            
            # Fallback to yfinance if screener fails
            ticker = yf.Ticker(f"{symbol}.NS")
            info = ticker.info
            hist = ticker.history(period="1y")
            
            if info:
                # Calculate ROE and ROCE from available financial data
                # ROE = Net Income / Total Stockholder Equity
                # ROCE = EBIT / (Total Equity + Total Debt)
                
                roe_calculated = info.get('returnOnEquity', 0)
                roce_calculated = info.get('returnOnAssets', 0)  # Using ROA as proxy
                
                # Try to calculate ROE if missing
                if not roe_calculated or roe_calculated == 0:
                    net_income = info.get('netIncomeToCommon', 0)
                    total_equity = info.get('totalStockholderEquity', 0)
                    if net_income and total_equity and total_equity > 0:
                        roe_calculated = net_income / total_equity
                
                # Try to calculate ROCE if missing
                if not roce_calculated or roce_calculated == 0:
                    ebit = info.get('ebit', 0) or info.get('ebitda', 0)
                    total_equity = info.get('totalStockholderEquity', 0) or 0
                    total_debt = info.get('totalDebt', 0) or 0
                    if ebit and (total_equity + total_debt) > 0:
                        roce_calculated = ebit / (total_equity + total_debt)
                
                # If still missing ROE, use profit margin as a reasonable proxy
                if not roe_calculated or roe_calculated == 0:
                    # Try profit margin as a proxy (profit efficiency)
                    profit_margin = info.get('profitMargins', 0)
                    if profit_margin:
                        roe_calculated = profit_margin  # Use as proxy
                
                # If still missing ROCE, use ROA or profit margin
                if not roce_calculated or roce_calculated == 0:
                    roce_calculated = info.get('returnOnAssets', 0) or info.get('profitMargins', 0)
                
                return {
                    "symbol": symbol,
                    "name": info.get('longName', f"{symbol} Limited"),
                    "sector": info.get('sector', 'Unknown'),
                    "current_price": info.get('currentPrice', info.get('regularMarketPrice', 0)),
                    "previous_close": info.get('previousClose', 0),
                    "market_cap": info.get('marketCap', 0),
                    "pe_ratio": info.get('trailingPE', 0),
                    "forward_pe": info.get('forwardPE', 0),
                    "peg_ratio": info.get('pegRatio', 0),
                    "dividend_yield": info.get('dividendYield', 0),
                    "roe": roe_calculated,
                    "roce": roce_calculated,
                    "roa": info.get('returnOnAssets', 0),
                    "book_value": info.get('bookValue', 0),
                    "debt_to_equity": info.get('debtToEquity', 0),
                    "profit_margin": info.get('profitMargins', 0),
                    "gross_margin": info.get('grossMargins', 0),
                    "revenue_growth": info.get('revenueGrowth', 0),
                    "earnings_growth": info.get('earningsGrowth', 0),
                    "beta": info.get('beta', 1.0),
                    "52w_high": info.get('fiftyTwoWeekHigh', 0),
                    "52w_low": info.get('fiftyTwoWeekLow', 0),
                    "volume": info.get('volume', 0),
                    "avg_volume": info.get('averageVolume', 0),
                    "target_price": info.get('targetMeanPrice', 0)
                }
        except Exception as e:
            print(f"Error fetching stock data for {symbol}: {e}")
        
        return None
    
    def _format_percentage(self, value, is_yield=False):
        """Format percentage value - handles both decimal (0.29) and percent (29) formats"""
        try:
            val = float(value) if value else 0
            
            # For dividend yield from screener: 0.21 means 0.21% (don't multiply by 100)
            # For dividend yield from yfinance: same behavior
            if is_yield:
                # Dividend yields are already in percentage format (0.21 = 0.21%)
                if val > 100:  # Edge case: already multiplied
                    return round(val, 2)
                else:
                    return round(val, 2)  # Keep as is
            else:
                # For ROE/ROCE: value could be decimal (0.29) or percent (29)
                if val > 100:
                    # Already in percentage, use as is
                    return round(val, 2)
                elif val > 1:
                    # Looks like percentage already (29)
                    return round(val, 2)
                else:
                    # Decimal format, convert to percentage
                    return round(val * 100, 2)
        except (ValueError, TypeError):
            return 0
    
    def _parse_market_cap(self, market_cap):
        """Convert market cap to absolute numeric value"""
        if isinstance(market_cap, str):
            # Extract numeric value from string like "₹9,552Cr." or "10.28 B"
            try:
                import re
                numbers = re.findall(r'[\d.]+', market_cap.replace(',', ''))
                if numbers:
                    market_cap_value = float(numbers[0])
                    # Check if it's in Crores, Billions, etc.
                    if 'Cr' in market_cap or 'crore' in market_cap.lower():
                        market_cap_value = market_cap_value * 10000000  # Convert to absolute
                    elif 'B' in market_cap or 'billion' in market_cap.lower():
                        market_cap_value = market_cap_value * 1000000000  # Convert to absolute
                    elif 'T' in market_cap or 'trillion' in market_cap.lower():
                        market_cap_value = market_cap_value * 1000000000000  # Convert to absolute
                else:
                    market_cap_value = 0
            except:
                market_cap_value = 0
        else:
            market_cap_value = float(market_cap) if isinstance(market_cap, (int, float)) else 0
        return market_cap_value
    
    def _generate_swot_from_data(self, stock_data):
        """Generate SWOT analysis from real stock data"""
        strengths = []
        weaknesses = []
        opportunities = []
        threats = []
        
        # Analyze based on P/E ratio
        pe = stock_data.get('pe_ratio', 0)
        # Ensure pe is numeric
        try:
            pe = float(pe) if pe else 0
        except (ValueError, TypeError):
            pe = 0
        
        if 10 <= pe <= 25:
            strengths.append(f"Attractive P/E ratio of {pe:.1f} indicating reasonable valuation")
        elif pe > 30:
            weaknesses.append(f"High P/E ratio of {pe:.1f} suggesting overvaluation")
        
        # Analyze Return on Equity
        roe = stock_data.get('roe', 0) * 100 if isinstance(stock_data.get('roe'), (int, float)) else 0
        if roe > 20:
            strengths.append(f"Excellent Return on Equity ({roe:.1f}%) indicating highly efficient capital usage")
        elif roe > 15:
            strengths.append(f"Strong Return on Equity ({roe:.1f}%) indicating efficient capital usage")
        elif roe > 0 and roe < 10:
            weaknesses.append(f"Low Return on Equity ({roe:.1f}%) - needs improvement in capital efficiency")
        elif roe <= 0:
            weaknesses.append(f"Negative Return on Equity ({roe:.1f}%) indicating financial distress")
        
        # Analyze Return on Assets
        roa = stock_data.get('roa', 0) * 100
        if roa > 5:
            strengths.append(f"Healthy Return on Assets ({roa:.1f}%)")
        
        # Analyze debt
        debt_eq = stock_data.get('debt_to_equity', 0)
        try:
            debt_eq = float(debt_eq) if debt_eq else 0
        except (ValueError, TypeError):
            debt_eq = 0
        
        if debt_eq < 0.3:
            strengths.append(f"Prudent debt management (D/E: {debt_eq:.2f}) - low financial risk")
        elif debt_eq < 0.5:
            strengths.append(f"Conservative debt levels (D/E: {debt_eq:.2f}) providing stability")
        elif 0.5 <= debt_eq <= 1.0:
            strengths.append(f"Moderate leverage (D/E: {debt_eq:.2f}) for growth")
        elif debt_eq > 1.0 and debt_eq <= 2.0:
            weaknesses.append(f"Elevated leverage (D/E: {debt_eq:.2f}) increasing financial risk")
        elif debt_eq > 2.0:
            weaknesses.append(f"Excessive leverage (D/E: {debt_eq:.2f}) - high financial risk")
        
        # Analyze profit margins
        profit_margin = stock_data.get('profit_margin', 0) * 100 if isinstance(stock_data.get('profit_margin'), (int, float)) else 0
        if profit_margin > 20:
            strengths.append(f"Exceptional profit margins ({profit_margin:.1f}%) demonstrating strong operational efficiency")
        elif profit_margin > 15:
            strengths.append(f"Strong profit margins ({profit_margin:.1f}%) indicating efficient operations")
        elif profit_margin > 10:
            strengths.append(f"Healthy profit margins ({profit_margin:.1f}%)")
        elif profit_margin > 0 and profit_margin < 5:
            weaknesses.append(f"Thin profit margins ({profit_margin:.1f}%) - operational efficiency concerns")
        elif profit_margin <= 0:
            weaknesses.append(f"Negative profit margins indicating operational losses")
        
        # Analyze growth
        revenue_growth = stock_data.get('revenue_growth', 0) * 100 if isinstance(stock_data.get('revenue_growth'), (int, float)) else 0
        if revenue_growth > 20:
            strengths.append(f"Exceptional revenue growth ({revenue_growth:.1f}%) - strong market expansion")
        elif revenue_growth > 10:
            strengths.append(f"Strong revenue growth ({revenue_growth:.1f}%) indicating market traction")
        elif revenue_growth > 5:
            strengths.append(f"Steady revenue growth ({revenue_growth:.1f}%)")
        elif revenue_growth < -5:
            weaknesses.append(f"Contracting revenues ({revenue_growth:.1f}%) - business challenges")
        elif revenue_growth < 0:
            weaknesses.append(f"Declining revenue ({revenue_growth:.1f}%)")
        
        earnings_growth = stock_data.get('earnings_growth', 0) * 100 if isinstance(stock_data.get('earnings_growth'), (int, float)) else 0
        if earnings_growth > 25:
            strengths.append(f"Outstanding earnings growth ({earnings_growth:.1f}%) - profitability momentum")
        elif earnings_growth > 15:
            strengths.append(f"Strong earnings growth ({earnings_growth:.1f}%)")
        elif earnings_growth > 0 and earnings_growth < 5:
            weaknesses.append(f"Sluggish earnings growth ({earnings_growth:.1f}%)")
        elif earnings_growth < 0:
            weaknesses.append(f"Earnings declining ({earnings_growth:.1f}%) - profitability concerns")
        
        # Analyze beta (volatility)
        beta = stock_data.get('beta', 1.0)
        try:
            beta = float(beta) if beta else 1.0
        except (ValueError, TypeError):
            beta = 1.0
        
        if beta < 1.0:
            strengths.append(f"Low volatility (beta: {beta:.2f}) - stable against market")
        elif beta > 1.5:
            weaknesses.append(f"High volatility (beta: {beta:.2f}) - more sensitive to market")
        
        # Dividend analysis
        div_yield = stock_data.get('dividend_yield', 0) * 100 if isinstance(stock_data.get('dividend_yield'), (int, float)) else 0
        if div_yield > 5:
            strengths.append(f"Excellent dividend yield ({div_yield:.2f}%) for income investors")
        elif div_yield > 2:
            strengths.append(f"Attractive dividend yield ({div_yield:.2f}%) providing regular income")
        elif div_yield > 0 and div_yield < 1:
            weaknesses.append(f"Low dividend yield ({div_yield:.2f}%) - limited income generation")
        elif div_yield == 0:
            weaknesses.append("No dividend payment - reinvestment strategy preferred")
        
        # Market cap based opportunities
        market_cap = stock_data.get('market_cap', 0)
        market_cap_value = self._parse_market_cap(market_cap)
        
        if market_cap_value > 100000000000:  # Large cap
            strengths.append("Large market capitalization providing stability")
        elif market_cap_value > 5000000000:  # Mid cap
            opportunities.append("Mid-cap position with growth potential")
        
        # Sector-specific opportunities
        sector = stock_data.get('sector', '')
        if sector:
            opportunities.append(f"Growth potential in {sector} sector")
        
        # Generate sector-specific and data-driven opportunities
        if not opportunities:
            opportunities = [
                "Digital transformation opportunities",
                "Market expansion in Tier 2/3 cities",
                "Government policy support",
                "Strategic partnerships and acquisitions",
                "Emerging technology adoption"
            ]
        
        # Generate dynamic threats based on financial metrics and sector
        threats = self._generate_threats(stock_data, sector)
        
        # If we don't have enough strengths/weaknesses, add generic ones
        if len(strengths) < 3:
            strengths.extend([
                "Established market presence",
                "Experienced management team"
            ])
        
        if len(weaknesses) < 3:
            weaknesses.extend([
                "Dependence on domestic market",
                "Regulatory compliance challenges"
            ])
        
        return {
            "symbol": stock_data['symbol'],
            "name": stock_data.get('name', f"{stock_data['symbol']} Limited"),
            "sector": stock_data.get('sector', 'Unknown'),
            "analysis_date": datetime.now().strftime("%B %d, %Y"),
            "strengths": strengths[:7],
            "weaknesses": weaknesses[:7],
            "opportunities": opportunities[:7],
            "threats": threats[:7],
            "financial_summary": {
                "current_price": round(float(stock_data.get('current_price', 0)), 2),
                "market_cap": str(stock_data.get('market_cap', 0)),  # Keep as string if from screener
                "pe_ratio": round(float(stock_data.get('pe_ratio', 0)), 2),
                "debt_to_equity": round(float(stock_data.get('debt_to_equity', 0)), 2),
                "profit_margin": round(float(stock_data.get('profit_margin', 0)), 4),
                "roe": self._format_percentage(stock_data.get('roe', 0)),
                "dividend_yield": self._format_percentage(stock_data.get('dividend_yield', 0), is_yield=True)
            }
        }
    
    def _generate_threats(self, stock_data, sector):
        """Generate dynamic threats based on financial metrics and sector analysis"""
        threats = []
        
        # Analyze financial distress indicators
        debt_eq = stock_data.get('debt_to_equity', 0)
        if debt_eq > 2.0:
            threats.append(f"High leverage (D/E: {debt_eq:.2f}) increasing bankruptcy risk during economic downturn")
        
        # Analyze profitability trends
        profit_margin = stock_data.get('profit_margin', 0) * 100 if isinstance(stock_data.get('profit_margin'), (int, float)) else 0
        if profit_margin < 5:
            threats.append("Thin profit margins vulnerable to cost inflation and competitive pressure")
        elif profit_margin < 0:
            threats.append("Operating losses - cash flow concerns and potential funding crisis")
        
        # Analyze revenue decline
        revenue_growth = stock_data.get('revenue_growth', 0) * 100 if isinstance(stock_data.get('revenue_growth'), (int, float)) else 0
        if revenue_growth < -10:
            threats.append(f"Severe revenue contraction ({revenue_growth:.1f}%) indicating market share loss")
        
        # Analyze ROE decline - capital efficiency issue
        roe = stock_data.get('roe', 0) * 100 if isinstance(stock_data.get('roe'), (int, float)) else 0
        if roe < 0:
            threats.append("Negative ROE indicating capital destruction and investor confidence loss")
        elif roe < 10:
            threats.append(f"Low ROE ({roe:.1f}%) - inefficient capital allocation vs peers")
        
        # Analyze beta - volatility risk
        beta = stock_data.get('beta', 1.0)
        if beta > 1.5:
            threats.append(f"High volatility (beta: {beta:.2f}) - magnified losses during market corrections")
        elif beta < 0.5:
            threats.append(f"Unusually low volatility (beta: {beta:.2f}) may mask underlying risks")
        
        # Sector-specific threats
        if sector.lower() == 'energy' or 'oil' in sector.lower() or 'gas' in sector.lower():
            threats.extend([
                "Volatile commodity prices (oil/gas) affecting margins",
                "Regulatory changes towards renewable energy",
                "Environmental regulations and carbon taxes",
                "Geopolitical tensions affecting energy supply"
            ])
        elif sector.lower() == 'technology' or 'tech' in sector.lower() or 'software' in sector.lower() or 'IT' in sector:
            threats.extend([
                "Rapid technological obsolescence risks",
                "Intense competition from global tech giants",
                "Cybersecurity vulnerabilities and data breaches",
                "Skill shortage in emerging technologies (AI, Cloud)"
            ])
        elif 'banking' in sector.lower() or 'finance' in sector.lower() or 'bank' in sector.lower() or 'financial' in sector.lower():
            threats.extend([
                "Rising non-performing assets (NPA) risk",
                "Interest rate volatility impact on margins",
                "Regulatory capital requirements (Basel norms)",
                "Digital disruption from fintech companies",
                "Economic slowdown increasing credit defaults"
            ])
        elif sector.lower() == 'fmcg' or 'consumer' in sector.lower():
            threats.extend([
                "Raw material cost inflation",
                "Intensifying competition from unorganized sector",
                "Changing consumer preferences towards health/wellness",
                "Rural consumption slowdown"
            ])
        elif sector.lower() == 'healthcare' or 'pharma' in sector.lower():
            threats.extend([
                "Regulatory price controls on medicines",
                "US FDA compliance and inspection risks",
                "Patent expiration leading to generic competition",
                "Supply chain disruptions from geopolitical tensions"
            ])
        elif 'telecom' in sector.lower():
            threats.extend([
                "Intense price wars from 5G competition",
                "High capital expenditure requirements for network expansion",
                "Regulatory spectrum auction costs",
                "Customer churn due to service quality issues"
            ])
        
        # High P/E ratio threat
        pe = stock_data.get('pe_ratio', 0)
        if pe > 30:
            threats.append(f"Elevated valuation (P/E: {pe:.1f}) - correction risk if earnings disappoint")
        
        # Market cap based threats
        market_cap = stock_data.get('market_cap', 0)
        # Convert market_cap to numeric value (handles both string and number)
        market_cap_value = self._parse_market_cap(market_cap)
        
        if market_cap_value < 1000000000:  # Small cap
            threats.append("Low market cap - limited liquidity and vulnerability to market manipulation")
        elif market_cap_value < 10000000000:  # Mid cap
            threats.append("Mid-cap volatility - higher risk than large-cap peers during market corrections")
        
        # Earnings decline threat
        earnings_growth = stock_data.get('earnings_growth', 0) * 100 if isinstance(stock_data.get('earnings_growth'), (int, float)) else 0
        if earnings_growth < -20:
            threats.append(f"Sharp earnings decline ({earnings_growth:.1f}%) indicating operational crisis")
        
        # Generic market threats (always applicable)
        generic_threats = [
            "Economic recession impacting demand",
            "Global supply chain disruptions",
            "Currency fluctuation affecting export competitiveness"
        ]
        
        threats.extend(generic_threats)
        
        return threats[:10]  # Limit to top 10 most relevant threats
    
    def analyze(self, symbol):
        # Fetch real stock data
        stock_data = self._fetch_stock_data(symbol)
        
        if stock_data:
            return self._generate_swot_from_data(stock_data)
        
        # Fallback: return generic SWOT if data unavailable
        return {
            "symbol": symbol,
            "name": f"{symbol} Limited",
            "sector": "Unknown",
            "analysis_date": datetime.now().strftime("%B %d, %Y"),
            "strengths": ["Market presence", "Established operations", "Revenue generation"],
            "weaknesses": ["Data unavailable", "Limited visibility", "Analysis pending"],
            "opportunities": ["Market growth", "Expansion", "Technology adoption"],
            "threats": ["Competition", "Economic factors", "Regulatory changes"],
            "financial_summary": {"current_price": 0, "market_cap": 0, "pe_ratio": 0, 
                                 "debt_to_equity": 0, "profit_margin": 0, "roe": 0, "dividend_yield": 0}
        }
