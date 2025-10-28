# Stock SWOT Analysis Website

## Project Status: âœ… Running Successfully!

Both backend and frontend servers are running:
- Backend: http://localhost:5000
- Frontend: http://localhost:8000

## Quick Start

1. Backend is already running on port 5000
2. Frontend is already running on port 8000
3. Open your browser and go to: http://localhost:8000

## Features Implemented

âœ… Real-time Nifty50 and Sensex market data
âœ… Stock SWOT analysis generation
âœ… Beautiful modern UI with Tailwind CSS
âœ… Real-time data polling (updates every 5 seconds)
âœ… Backend caching for API responses

## Try It Out

1. Open http://localhost:8000 in your browser
2. You'll see real-time Nifty50 and Sensex data
3. Enter a stock symbol (e.g., RELIANCE, TCS, INFY) and click "Analyze"
4. View the comprehensive SWOT analysis

## API Endpoints

- GET http://localhost:5000/api/nifty50 - Get Nifty50 data
- GET http://localhost:5000/api/sensex - Get Sensex data
- GET http://localhost:5000/api/swot/<SYMBOL> - Get SWOT analysis

## Sample Stock Symbols

- RELIANCE (Reliance Industries)
- TCS (Tata Consultancy Services)
- HDFCBANK (HDFC Bank)
- INFY (Infosys)
- ICICIBANK (ICICI Bank)

## Project Structure

```
stock-analysis-site/
â”œâ”€â”€ backend/
â”‚   â”œâ”€â”€ app.py                   # Flask API server
â”‚   â”œâ”€â”€ modules/
â”‚   â”‚   â”œâ”€â”€ database.py          # SQLite database operations
â”‚   â”‚   â”œâ”€â”€ data_fetcher.py      # Market data fetching
â”‚   â”‚   â””â”€â”€ swot_analyzer.py     # SWOT analysis engine
â”‚   â””â”€â”€ requirements.txt          # Python dependencies
â””â”€â”€ frontend/
    â”œâ”€â”€ index.html               # Main HTML file
    â””â”€â”€ src/
        â””â”€â”€ app.jsx              # React application
```

## Technologies Used

- **Backend**: Python Flask, SQLite
- **Frontend**: React (via CDN), Tailwind CSS
- **Data**: NSE India, BSE India, Yahoo Finance (via yfinance)

Enjoy exploring the stock market analysis!
