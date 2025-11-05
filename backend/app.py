from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import datetime
from modules.database import init_db, get_db_connection
from modules.data_fetcher import DataFetcher
from modules.swot_analyzer import SWOTAnalyzer
from modules.company_info import CompanyInfo
from modules.stock_screener import StockScreener
from modules.auth import login_user, register_user, forgot_password, verify_token, create_or_reset_password, verify_jwt_token
from modules.email_service import send_password_create_email, send_password_reset_email

app = Flask(__name__)
CORS(app)
init_db()
data_fetcher = DataFetcher()
swot_analyzer = SWOTAnalyzer()
company_info = CompanyInfo()
stock_screener = StockScreener()

@app.route("/")
def index():
    return jsonify({"status": "Stock SWOT API", "version": "1.0"})

# Authentication endpoints
@app.route("/api/login", methods=["POST"])
def login():
    try:
        data = request.get_json()
        username = data.get('username') or data.get('email')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({"success": False, "error": "Username and password are required"}), 400
        
        result = login_user(username, password)
        if result['success']:
            return jsonify(result)
        else:
            return jsonify(result), 401
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/api/register", methods=["POST"])
def register():
    try:
        data = request.get_json()
        first_name = data.get('first_name')
        last_name = data.get('last_name', '')
        email = data.get('email')
        phone = data.get('phone', '')
        
        result = register_user(first_name, last_name, email, phone)
        
        if result['success']:
            # Send email with password create link
            send_password_create_email(email, first_name, result['token'])
            return jsonify({
                "success": True,
                "message": result['message']
            })
        else:
            return jsonify(result), 400
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/api/forgot-password", methods=["POST"])
def forgot_password_endpoint():
    try:
        data = request.get_json()
        first_name = data.get('first_name')
        last_name = data.get('last_name', '')
        email = data.get('email')
        phone = data.get('phone', '')
        
        result = forgot_password(first_name, last_name, email, phone)
        
        if result['success']:
            # Send email with password reset link
            send_password_reset_email(email, first_name, result['token'])
            return jsonify({
                "success": True,
                "message": result['message']
            })
        else:
            return jsonify(result), 400
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/api/verify-token", methods=["POST"])
def verify_token_endpoint():
    try:
        data = request.get_json()
        token = data.get('token')
        token_type = data.get('token_type', 'create_password')  # 'create_password' or 'reset_password'
        
        if not token:
            return jsonify({"success": False, "error": "Token is required"}), 400
        
        result = verify_token(token, token_type)
        return jsonify(result)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/api/create-password", methods=["POST"])
def create_password():
    try:
        data = request.get_json()
        token = data.get('token')
        password = data.get('password')
        
        if not token or not password:
            return jsonify({"success": False, "error": "Token and password are required"}), 400
        
        result = create_or_reset_password(token, password, 'create_password')
        return jsonify(result)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/api/reset-password", methods=["POST"])
def reset_password():
    try:
        data = request.get_json()
        token = data.get('token')
        password = data.get('password')
        
        if not token or not password:
            return jsonify({"success": False, "error": "Token and password are required"}), 400
        
        result = create_or_reset_password(token, password, 'reset_password')
        return jsonify(result)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/api/verify-auth", methods=["POST"])
def verify_auth():
    """Verify JWT token and return user info - Fast response for expired tokens"""
    try:
        data = request.get_json()
        token = data.get('token')
        
        if not token:
            return jsonify({"success": False, "error": "Token is required"}), 400
        
        payload = verify_jwt_token(token)
        if payload:
            return jsonify({"success": True, "user_id": payload['user_id'], "email": payload['email']})
        else:
            # Fast response for expired/invalid tokens
            return jsonify({"success": False, "error": "Invalid or expired token"}), 401
    except Exception as e:
        # Fast error response
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/api/nifty50", methods=["GET"])
def get_nifty50():
    try:
        data = data_fetcher.fetch_nifty50()
        return jsonify({"success": True, "data": data})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/api/sensex", methods=["GET"])
def get_sensex():
    try:
        data = data_fetcher.fetch_sensex()
        return jsonify({"success": True, "data": data})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/api/stock-details/<symbol>", methods=["GET"])
def get_stock_details(symbol):
    """Get detailed stock information from Yahoo Finance"""
    try:
        stock_data = swot_analyzer._fetch_stock_data(symbol.upper())
        
        if stock_data:
            # Format market cap (could be string from screener or number from yfinance)
            market_cap = stock_data.get('market_cap', 0)
            
            # If market_cap is already a string from screener.in, use it directly
            if isinstance(market_cap, str):
                market_cap_display = market_cap
            # Otherwise convert from number
            elif isinstance(market_cap, (int, float)):
                if market_cap >= 1000000000000:
                    market_cap_display = f"{market_cap / 1000000000000:.2f} T"
                elif market_cap >= 10000000000:
                    market_cap_display = f"{market_cap / 10000000000:.2f} B"
                elif market_cap >= 10000000:
                    market_cap_display = f"{market_cap / 10000000:.2f} Cr"
                else:
                    market_cap_display = f"{market_cap:,.0f}"
            else:
                market_cap_display = str(market_cap)
            
            # Correctly format financial metrics
            roe_raw = stock_data.get('roe', 0)
            # ROE from screener.in is already in percentage (29 = 29%)
            # ROE from yfinance is in decimal (0.29 = 29%)
            # Check if it's from screener (value >= 1 typically) or yfinance (value < 1)
            if isinstance(roe_raw, (int, float)):
                if roe_raw > 0 and roe_raw <= 1:
                    roe_percent = round(roe_raw * 100, 2)  # yfinance format
                else:
                    roe_percent = round(roe_raw, 2)  # screener.in format (already %)
            else:
                roe_percent = 0
            
            roce_raw = stock_data.get('roce', 0)
            # ROCE from screener.in is already in percentage
            if isinstance(roce_raw, (int, float)):
                if roce_raw > 0 and roce_raw <= 1:
                    roce_percent = round(roce_raw * 100, 2)  # yfinance format
                else:
                    roce_percent = round(roce_raw, 2)  # screener.in format (already %)
            else:
                roce_percent = 0
            
            dividend_yield_raw = stock_data.get('dividend_yield', 0)
            # Dividend yield from yfinance is ALREADY in percentage form
            # TI returns 0.21 which IS 0.21% (yfinance formats it as decimal percentage)
            # So we do NOT convert - it's already correct
            # Just round it to 2 decimal places for display
            if dividend_yield_raw:
                div_yield = round(dividend_yield_raw, 2)
            else:
                div_yield = 0
            
            details = {
                "symbol": stock_data['symbol'],
                "name": stock_data.get('name', ''),
                "sector": stock_data.get('sector', 'Unknown'),
                "current_price": round(stock_data.get('current_price', 0), 2),
                "market_cap": market_cap_display,
                "pe_ratio": round(stock_data.get('pe_ratio', 0), 2),
                "book_value": round(stock_data.get('book_value', 0), 2),
                "roe": roe_percent,
                "roce": roce_percent,
                "dividend_yield": div_yield,
                "52w_high": round(stock_data.get('52w_high', 0), 2),
                "52w_low": round(stock_data.get('52w_low', 0), 2),
                "previous_close": round(stock_data.get('previous_close', 0), 2),
                "peer_comparison": stock_data.get('peer_comparison'),
                "quarterly_results": stock_data.get('quarterly_results')
            }
            
            return jsonify({"success": True, "data": details})
        else:
            return jsonify({"success": False, "error": "Stock data not found"}), 404
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/api/swot/<symbol>", methods=["POST", "GET"])
def generate_swot(symbol):
    try:
        swot_data = swot_analyzer.analyze(symbol.upper())
        return jsonify({"success": True, "data": {"symbol": symbol.upper(), "swot": swot_data,
                   "timestamp": datetime.now().isoformat()}})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/api/historical/<symbol>", methods=["GET"])
def get_historical_data(symbol):
    try:
        period = request.args.get('period', '1y')  # Default to 1 year
        
        # Map period values
        period_map = {
            '1y': '1y',
            '3y': '3y',
            '5y': '5y',
            'all': 'max'
        }
        
        period = period_map.get(period, '1y')
        data = data_fetcher.fetch_historical_data(symbol.upper(), period)
        
        if data:
            return jsonify({"success": True, "data": data, "period": period})
        else:
            return jsonify({"success": False, "error": "Historical data not found"}), 404
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/api/company-info/<symbol>", methods=["GET"])
def get_company_info(symbol):
    try:
        info = company_info.get_annual_reports_and_news(symbol.upper())
        return jsonify({"success": True, "data": info})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/api/peer-comparison/<symbol>", methods=["GET"])
def get_peer_comparison(symbol):
    """Get peer comparison data for stocks in the same sector"""
    try:
        stock_data = swot_analyzer._fetch_stock_data(symbol.upper())
        if not stock_data:
            return jsonify({"success": False, "error": "Stock data not found"}), 404
        
        peer_data = stock_data.get('peer_comparison', [])
        
        # If peer_comparison is None or empty, return empty array
        if not peer_data:
            return jsonify({"success": True, "data": [], "sector": stock_data.get('sector', 'Unknown')})
        
        # If it's already in the new format (list of dicts), return as is
        if isinstance(peer_data, list) and len(peer_data) > 0 and isinstance(peer_data[0], dict):
            return jsonify({
                "success": True, 
                "data": peer_data,
                "sector": stock_data.get('sector', 'Unknown')
            })
        
        # If it's in old format (dict with headers/rows), convert it
        # (This should not happen with new code, but handle it for compatibility)
        return jsonify({
            "success": True,
            "data": [],
            "sector": stock_data.get('sector', 'Unknown')
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/api/bulk-deals/<symbol>", methods=["GET"])
def get_bulk_deals(symbol):
    """Get bulk deals data for the last 30 days"""
    try:
        days = request.args.get('days', 30, type=int)
        from modules.screener_scraper import ScreenerScraper
        scraper = ScreenerScraper()
        bulk_deals = scraper.fetch_bulk_deals(symbol.upper(), days=days)
        return jsonify({"success": True, "data": bulk_deals})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/api/screen-stocks", methods=["GET", "POST"])
def screen_stocks():
    """
    Screen Indian stocks based on criteria:
    - Low PEG ratio
    - Reasonable P/E ratio
    - Low/no debt from previous 3 years
    - Recent performance improvements (sales, profits, margins)
    
    Query parameters (all optional):
    - max_peg: Maximum PEG ratio (default 3.0)
    - min_pe: Minimum P/E ratio (default 5.0)
    - max_pe: Maximum P/E ratio (default 35.0)
    - max_debt_to_equity: Maximum Debt to Equity (default 1.0)
    - min_sales_growth: Minimum sales growth % (default 0.0 - allows any positive growth)
    - min_profit_growth: Minimum profit growth % (default 0.0 - allows any positive growth)
    - require_margin_improvement: Require improving margins (default false)
    """
    try:
        # Get parameters from query string or JSON body
        if request.method == 'POST':
            params = request.get_json() or {}
        else:
            params = request.args.to_dict()
        
        # Parse parameters with defaults (more reasonable values)
        max_peg = float(params.get('max_peg', 3.0))  # Increased from 2.0
        min_pe = float(params.get('min_pe', 5.0))
        max_pe = float(params.get('max_pe', 35.0))  # Increased from 30.0
        max_debt_to_equity = float(params.get('max_debt_to_equity', 1.0))  # Increased from 0.5
        min_sales_growth = float(params.get('min_sales_growth', 0.0))  # Changed from 5.0
        min_profit_growth = float(params.get('min_profit_growth', 0.0))  # Changed from 5.0
        require_margin_improvement = params.get('require_margin_improvement', 'false').lower() == 'true'  # Changed default to false
        
        # Custom stocks list if provided
        stocks_list = params.get('stocks_list')
        if stocks_list and isinstance(stocks_list, list):
            stocks_list = [s.upper() for s in stocks_list]
        else:
            stocks_list = None
        
        # Run the screener
        print(f"Starting stock screening with criteria: max_peg={max_peg}, min_pe={min_pe}, max_pe={max_pe}")
        results = stock_screener.screen_stocks(
            max_peg=max_peg,
            min_pe=min_pe,
            max_pe=max_pe,
            max_debt_to_equity=max_debt_to_equity,
            min_sales_growth=min_sales_growth,
            min_profit_growth=min_profit_growth,
            require_margin_improvement=require_margin_improvement,
            stocks_list=stocks_list,
            max_results=10  # Limit to top 10 results
        )
        
        print(f"Screening completed. Found {len(results)} matching stocks.")
        
        return jsonify({
            "success": True,
            "data": results if results else [],
            "count": len(results) if results else 0,
            "criteria": {
                "max_peg": max_peg,
                "min_pe": min_pe,
                "max_pe": max_pe,
                "max_debt_to_equity": max_debt_to_equity,
                "min_sales_growth": min_sales_growth,
                "min_profit_growth": min_profit_growth,
                "require_margin_improvement": require_margin_improvement
            },
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"Error in screen_stocks endpoint: {e}")
        print(f"Traceback: {error_trace}")
        return jsonify({
            "success": False, 
            "error": str(e),
            "traceback": error_trace if app.debug else None
        }), 500

if __name__ == "__main__":
    app.run(debug=True, port=5000)
