# Stock Screener Feature

## Overview

The Stock Screener is a powerful tool that filters Indian stocks based on multiple financial criteria to identify potentially undervalued stocks with strong fundamentals and recent performance improvements.

## Features

The screener filters stocks based on:

1. **Low PEG Ratio** - Price/Earnings to Growth ratio (indicates undervalued growth stocks)
2. **Reasonable P/E Ratio** - Price to Earnings ratio within a reasonable range
3. **Low/No Debt** - Debt to Equity ratio analysis from previous 3 years
4. **Recent Performance** - Analysis of:
   - Sales/revenue growth
   - Profit growth
   - Profit margin improvements
   - Debt reduction trends

## API Endpoint

### `/api/screen-stocks`

**Methods:** GET, POST

**Query Parameters (all optional):**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `max_peg` | float | 2.0 | Maximum PEG ratio |
| `min_pe` | float | 5.0 | Minimum P/E ratio |
| `max_pe` | float | 30.0 | Maximum P/E ratio |
| `max_debt_to_equity` | float | 0.5 | Maximum Debt to Equity ratio |
| `min_sales_growth` | float | 5.0 | Minimum sales growth percentage |
| `min_profit_growth` | float | 5.0 | Minimum profit growth percentage |
| `require_margin_improvement` | boolean | true | Require improving profit margins |

**Example Request:**

```bash
# GET request
curl "http://localhost:5000/api/screen-stocks?max_peg=1.5&min_pe=10&max_pe=25&max_debt_to_equity=0.3"

# POST request
curl -X POST "http://localhost:5000/api/screen-stocks" \
  -H "Content-Type: application/json" \
  -d '{
    "max_peg": 1.5,
    "min_pe": 10,
    "max_pe": 25,
    "max_debt_to_equity": 0.3,
    "min_sales_growth": 10,
    "min_profit_growth": 15,
    "require_margin_improvement": true
  }'
```

**Response Format:**

```json
{
  "success": true,
  "data": [
    {
      "symbol": "RELIANCE",
      "name": "Reliance Industries Ltd",
      "sector": "Energy",
      "current_price": 2450.50,
      "market_cap": "16.5 L Cr",
      "pe_ratio": 18.5,
      "peg_ratio": 1.2,
      "debt_to_equity": 0.35,
      "profit_margin": 12.5,
      "roe": 22.3,
      "roce": 18.7,
      "sales_growth": 15.2,
      "profit_growth": 28.5,
      "margin_improvement": true,
      "debt_decreasing": true,
      "match_score": 85.5
    }
  ],
  "count": 1,
  "criteria": {
    "max_peg": 1.5,
    "min_pe": 10,
    "max_pe": 25,
    "max_debt_to_equity": 0.3,
    "min_sales_growth": 10,
    "min_profit_growth": 15,
    "require_margin_improvement": true
  },
  "timestamp": "2025-01-15T10:30:00"
}
```

## Understanding the Criteria

### PEG Ratio (Price/Earnings to Growth)
- **Lower is better** (typically < 1.0 is considered undervalued)
- PEG = P/E Ratio / Earnings Growth Rate
- Indicates if a stock is undervalued relative to its growth prospects

### P/E Ratio (Price to Earnings)
- **Reasonable range**: 10-25 for most industries
- Too low (< 5) might indicate issues
- Too high (> 30) might indicate overvaluation

### Debt to Equity Ratio
- **Lower is better** (< 0.5 is ideal)
- Measures financial leverage
- The screener also checks if debt is decreasing over 3 years

### Sales Growth
- **Higher is better** (> 10% is strong)
- Indicates expanding business and market share

### Profit Growth
- **Higher is better** (> 15% is strong)
- Shows improving profitability and operational efficiency

### Margin Improvement
- Checks if profit margins are improving quarter-over-quarter
- Indicates operational efficiency improvements

## Match Score

Stocks are ranked by a match score that considers:
- Lower PEG ratio (better)
- Reasonable P/E ratio (10-20 ideal)
- Lower debt (better)
- Debt decreasing trend
- Higher sales/profit growth
- Margin improvements
- Higher ROE (Return on Equity)

## Usage Examples

### Example 1: Conservative Investor
Looking for low-risk, stable stocks:
```python
params = {
    "max_peg": 1.5,
    "min_pe": 10,
    "max_pe": 20,
    "max_debt_to_equity": 0.3,
    "min_sales_growth": 5,
    "min_profit_growth": 5,
    "require_margin_improvement": False
}
```

### Example 2: Growth Investor
Looking for high-growth stocks:
```python
params = {
    "max_peg": 2.0,
    "min_pe": 15,
    "max_pe": 35,
    "max_debt_to_equity": 0.5,
    "min_sales_growth": 15,
    "min_profit_growth": 20,
    "require_margin_improvement": True
}
```

### Example 3: Value Investor
Looking for undervalued stocks:
```python
params = {
    "max_peg": 1.0,
    "min_pe": 5,
    "max_pe": 15,
    "max_debt_to_equity": 0.4,
    "min_sales_growth": 0,
    "min_profit_growth": 0,
    "require_margin_improvement": False
}
```

## Testing

Run the test script:
```bash
cd backend
python test_screener.py
```

## Notes

- Screening can take several minutes as it analyzes multiple stocks
- Data is fetched from screener.in and Yahoo Finance
- Results are sorted by match score (highest first)
- The screener analyzes stocks from Nifty 50, Nifty Next 50, and other major indices
- For custom stock lists, use the `stocks_list` parameter in POST requests

## Data Sources

1. **screener.in** - Primary source for Indian stock financial data
2. **Yahoo Finance** - Fallback for PEG ratio and additional metrics

## Limitations

- Screening requires internet connection
- Rate limiting may apply from data sources
- Some stocks may not have complete data available
- Historical data availability depends on company reporting

## Future Enhancements

- Add more stocks from Nifty 500
- Include news sentiment analysis
- Add technical indicators
- Cache results for faster repeated queries
- Add export functionality (CSV, Excel)
