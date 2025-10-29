from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import datetime
from modules.database import init_db, get_db_connection
from modules.data_fetcher import DataFetcher
from modules.swot_analyzer import SWOTAnalyzer
from modules.company_info import CompanyInfo

app = Flask(__name__)
CORS(app)
init_db()
data_fetcher = DataFetcher()
swot_analyzer = SWOTAnalyzer()
company_info = CompanyInfo()

@app.route("/")
def index():
    return jsonify({"status": "Stock SWOT API", "version": "1.0"})

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
                "peer_comparison": stock_data.get('peer_comparison')
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

if __name__ == "__main__":
    app.run(debug=True, port=5000)
