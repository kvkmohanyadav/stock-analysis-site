"""
Test script for Stock Screener API

This script demonstrates how to use the stock screener endpoint to find Indian stocks
that meet specific investment criteria.

Usage:
    python test_screener.py
"""

import requests
import json

def test_stock_screener():
    """Test the stock screener API endpoint"""
    
    # API endpoint
    url = "http://localhost:5000/api/screen-stocks"
    
    # Default criteria (can be customized)
    params = {
        "max_peg": 2.0,              # Maximum PEG ratio
        "min_pe": 5.0,              # Minimum P/E ratio
        "max_pe": 30.0,             # Maximum P/E ratio
        "max_debt_to_equity": 0.5,  # Maximum Debt to Equity ratio
        "min_sales_growth": 5.0,    # Minimum sales growth %
        "min_profit_growth": 5.0,   # Minimum profit growth %
        "require_margin_improvement": True  # Require improving profit margins
    }
    
    print("=" * 80)
    print("STOCK SCREENER TEST")
    print("=" * 80)
    print(f"\nSearching for stocks with criteria:")
    print(f"  - PEG Ratio < {params['max_peg']}")
    print(f"  - P/E Ratio: {params['min_pe']} - {params['max_pe']}")
    print(f"  - Debt to Equity < {params['max_debt_to_equity']}")
    print(f"  - Sales Growth > {params['min_sales_growth']}%")
    print(f"  - Profit Growth > {params['min_profit_growth']}%")
    print(f"  - Margin Improvement: {params['require_margin_improvement']}")
    print("\nCalling API...")
    
    try:
        # Make GET request
        response = requests.get(url, params=params, timeout=300)  # 5 min timeout for screening
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get('success'):
                results = data.get('data', [])
                count = data.get('count', 0)
                
                print(f"\n✓ Found {count} matching stocks")
                print("=" * 80)
                
                if results:
                    print(f"\n{'Rank':<6} {'Symbol':<12} {'Name':<25} {'P/E':<8} {'PEG':<8} {'D/E':<8} {'Sales%':<10} {'Profit%':<10}")
                    print("-" * 80)
                    
                    for idx, stock in enumerate(results[:20], 1):  # Show top 20
                        print(f"{idx:<6} {stock['symbol']:<12} {stock['name'][:24]:<25} "
                              f"{stock['pe_ratio']:<8.2f} {stock['peg_ratio']:<8.2f} "
                              f"{stock['debt_to_equity']:<8.2f} {stock['sales_growth']:<10.2f} "
                              f"{stock['profit_growth']:<10.2f}")
                    
                    if len(results) > 20:
                        print(f"\n... and {len(results) - 20} more stocks")
                    
                    # Show detailed info for top 3
                    print("\n" + "=" * 80)
                    print("TOP 3 STOCKS - DETAILED VIEW")
                    print("=" * 80)
                    
                    for idx, stock in enumerate(results[:3], 1):
                        print(f"\n{idx}. {stock['name']} ({stock['symbol']})")
                        print(f"   Sector: {stock['sector']}")
                        print(f"   Current Price: ₹{stock['current_price']:.2f}")
                        print(f"   Market Cap: {stock['market_cap']}")
                        print(f"   P/E Ratio: {stock['pe_ratio']}")
                        print(f"   PEG Ratio: {stock['peg_ratio']}")
                        print(f"   Debt to Equity: {stock['debt_to_equity']}")
                        print(f"   Profit Margin: {stock['profit_margin']}%")
                        print(f"   ROE: {stock['roe']}%")
                        print(f"   ROCE: {stock['roce']}%")
                        print(f"   Sales Growth: {stock['sales_growth']:.2f}%")
                        print(f"   Profit Growth: {stock['profit_growth']:.2f}%")
                        print(f"   Margin Improvement: {'Yes' if stock['margin_improvement'] else 'No'}")
                        print(f"   Debt Decreasing: {'Yes' if stock['debt_decreasing'] else 'No'}")
                        print(f"   Match Score: {stock['match_score']:.1f}")
                else:
                    print("\nNo stocks found matching the criteria.")
                    print("Try relaxing some criteria (e.g., increase max_peg or max_debt_to_equity)")
            else:
                print(f"\n✗ API Error: {data.get('error', 'Unknown error')}")
        else:
            print(f"\n✗ HTTP Error: {response.status_code}")
            print(f"Response: {response.text}")
    
    except requests.exceptions.ConnectionError:
        print("\n✗ Error: Could not connect to the API.")
        print("Make sure the Flask backend is running on http://localhost:5000")
    except requests.exceptions.Timeout:
        print("\n✗ Error: Request timed out. Screening takes time, please be patient.")
    except Exception as e:
        print(f"\n✗ Error: {str(e)}")

if __name__ == "__main__":
    test_stock_screener()
