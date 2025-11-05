const { useState, useEffect, useRef } = React;

// Main Stock Analysis Component (original app content)
function StockAnalysis({ user, onLogout }) {
  const [niftyData, setNiftyData] = useState(null);
  const [sensexData, setSensexData] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [swotData, setSwotData] = useState(null);
  const [stockDetails, setStockDetails] = useState(null);
  const [loading, setLoading] = useState(false);
  const [historicalData, setHistoricalData] = useState(null);
  const [selectedPeriod, setSelectedPeriod] = useState('1y');
  const [companyInfo, setCompanyInfo] = useState(null);
  const [bulkDeals, setBulkDeals] = useState(null);
  const [screenerResults, setScreenerResults] = useState(null);
  const [screenerLoading, setScreenerLoading] = useState(false);
  const [screenerCriteria, setScreenerCriteria] = useState({
    max_peg: 3.0,  // Increased from 2.0 to find more stocks
    min_pe: 5.0,
    max_pe: 35.0,  // Increased from 30.0
    max_debt_to_equity: 1.0,  // Increased from 0.5 to be more reasonable
    min_sales_growth: 0.0,  // Changed from 5.0 - allow any positive growth
    min_profit_growth: 0.0,  // Changed from 5.0 - allow any positive growth
    require_margin_improvement: false  // Changed from true - too strict without quarterly data
  });
  const chartCanvasRef = useRef(null);
  const chartInstanceRef = useRef(null);

  useEffect(() => {
    // Fetch market data only once on first login (not on page refresh)
    // Check if data already exists in localStorage
    const storedNifty = localStorage.getItem('niftyData');
    const storedSensex = localStorage.getItem('sensexData');
    
    if (storedNifty) {
      try {
        setNiftyData(JSON.parse(storedNifty));
      } catch (e) {
        console.error('Error parsing stored Nifty data:', e);
      }
    }
    
    if (storedSensex) {
      try {
        setSensexData(JSON.parse(storedSensex));
      } catch (e) {
        console.error('Error parsing stored Sensex data:', e);
      }
    }
    
    // Only fetch if data doesn't exist (first login)
    if (!storedNifty || !storedSensex) {
      const fetchMarketData = async () => {
        try {
          const [nifty, sensex] = await Promise.all([
            axios.get('http://localhost:5000/api/nifty50', { timeout: 5000 }).catch(() => null),
            axios.get('http://localhost:5000/api/sensex', { timeout: 5000 }).catch(() => null)
          ]);
          if (nifty?.data?.success) {
            setNiftyData(nifty.data.data);
            localStorage.setItem('niftyData', JSON.stringify(nifty.data.data));
          }
          if (sensex?.data?.success) {
            setSensexData(sensex.data.data);
            localStorage.setItem('sensexData', JSON.stringify(sensex.data.data));
          }
        } catch (error) {
          console.error('Error fetching market data:', error);
        }
      };
      fetchMarketData();
    }
    
    // COMMENTED OUT: Real-time updates every 5 seconds
    // To enable real-time updates in the future, uncomment the following lines:
    // const interval = setInterval(fetchMarketData, 5000);
    // return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    if (!historicalData || !chartCanvasRef.current || historicalData.length === 0) {
      return;
    }

    // Clear any existing timeout
    let timeoutId;
    
    timeoutId = setTimeout(() => {
      if (!chartCanvasRef.current) return;

      // Destroy existing chart instance
      if (chartInstanceRef.current) {
        chartInstanceRef.current.destroy();
        chartInstanceRef.current = null;
      }

      const ctx = chartCanvasRef.current.getContext('2d');
      if (!ctx) return;

      const labels = historicalData.map(item => {
        const date = new Date(item.date);
        return date.toLocaleDateString('en-US', { month: 'short', year: 'numeric' });
      });
      
      const fullDates = historicalData.map(item => item.date);
      const prices = historicalData.map(item => item.close);

      if (typeof Chart === 'undefined') {
        console.error('Chart.js is not loaded');
        return;
      }

      try {
        const chart = new Chart(ctx, {
          type: 'line',
          data: {
            labels: labels,
            datasets: [{
              label: 'Stock Price',
              data: prices,
              borderColor: 'rgb(59, 130, 246)',
              backgroundColor: 'rgba(59, 130, 246, 0.1)',
              borderWidth: 2,
              fill: true,
              tension: 0.4,
              pointRadius: 0,
              pointHoverRadius: 5,
              _fullDates: fullDates
            }]
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
              legend: {
                display: false
              },
              tooltip: {
                mode: 'index',
                intersect: false,
                callbacks: {
                  title: function(context) {
                    const dataIndex = context[0].dataIndex;
                    const fullDate = chart.data.datasets[0]._fullDates[dataIndex];
                    const date = new Date(fullDate);
                    const formattedDate = date.toLocaleDateString('en-US', { 
                      weekday: 'short',
                      year: 'numeric', 
                      month: 'short', 
                      day: 'numeric' 
                    });
                    return formattedDate;
                  },
                  label: function(context) {
                    return 'Price: ₹' + context.parsed.y.toFixed(2);
                  }
                }
              }
            },
            scales: {
              x: {
                display: true,
                title: {
                  display: true,
                  text: 'Time',
                  font: {
                    size: 14,
                    weight: 'bold'
                  }
                },
                grid: {
                  display: true,
                  color: 'rgba(0, 0, 0, 0.05)'
                }
              },
              y: {
                display: true,
                title: {
                  display: true,
                  text: 'Price (₹)',
                  font: {
                    size: 14,
                    weight: 'bold'
                  }
                },
                grid: {
                  display: true,
                  color: 'rgba(0, 0, 0, 0.05)'
                },
                ticks: {
                  callback: function(value) {
                    return '₹' + value.toFixed(0);
                  }
                }
              }
            },
            interaction: {
              mode: 'index',
              intersect: false
            }
          }
        });

        chartInstanceRef.current = chart;
      } catch (error) {
        console.error('Error creating chart:', error);
      }
    }, 300); // Increased timeout to reduce re-renders

    return () => {
      if (timeoutId) clearTimeout(timeoutId);
      if (chartInstanceRef.current) {
        chartInstanceRef.current.destroy();
        chartInstanceRef.current = null;
      }
    };
  }, [historicalData, selectedPeriod]);

  const fetchHistoricalData = async (symbol, period) => {
    try {
      const response = await axios.get(`http://localhost:5000/api/historical/${symbol}?period=${period}`);
      if (response.data.success) {
        setHistoricalData(response.data.data);
        return response.data.data;
      }
    } catch (error) {
      console.error('Error fetching historical data:', error);
    }
    return null;
  };

  const handleSearch = async (symbolOverride = null) => {
    const symbolToSearch = symbolOverride || searchQuery.trim();
    if (!symbolToSearch) return;
    
    console.log('🔍 handleSearch called with symbol:', symbolToSearch);
    
    setLoading(true);
    try {
      const symbol = symbolToSearch.toUpperCase();
      const [swotResponse, detailsResponse, historicalResponse, companyInfoResponse, bulkDealsResponse] = await Promise.all([
        axios.get(`http://localhost:5000/api/swot/${symbol}`).catch(err => {
          console.error('SWOT fetch failed:', err);
          return { data: { success: false, error: err.message } };
        }),
        axios.get(`http://localhost:5000/api/stock-details/${symbol}`).catch(err => {
          console.error('Stock details fetch failed:', err);
          return { data: { success: false, error: err.message } };
        }),
        axios.get(`http://localhost:5000/api/historical/${symbol}?period=${selectedPeriod}`).catch(err => {
          console.error('Historical data fetch failed:', err);
          return { data: { success: false, error: err.message } };
        }),
        axios.get(`http://localhost:5000/api/company-info/${symbol}`).catch(err => {
          console.error('Company info fetch failed:', err);
          return { data: { success: false, error: err.message } };
        }),
        axios.get(`http://localhost:5000/api/bulk-deals/${symbol}?days=180`).catch(err => {
          console.error('Bulk deals fetch failed:', err);
          return { data: { success: false, error: err.message } };
        })
      ]);
      
      if (swotResponse?.data?.success) {
        setSwotData(swotResponse.data.data.swot);
      } else {
        console.error('SWOT analysis failed:', swotResponse?.data?.error || 'Unknown error');
        alert('Error: Could not generate SWOT analysis. Please try again.');
      }
      
      if (detailsResponse?.data?.success) {
        setStockDetails(detailsResponse.data.data);
      } else {
        console.error('Stock details failed:', detailsResponse?.data?.error || 'Unknown error');
      }
      
      if (historicalResponse?.data?.success) {
        setHistoricalData(historicalResponse.data.data);
        console.log('Historical data loaded:', historicalResponse.data.data.length, 'data points');
      } else {
        console.error('Historical data failed:', historicalResponse?.data?.error || 'Unknown error');
      }
      
      if (companyInfoResponse?.data?.success) {
        setCompanyInfo(companyInfoResponse.data.data);
      } else {
        console.error('Company info failed:', companyInfoResponse?.data?.error || 'Unknown error');
      }
      
      if (bulkDealsResponse?.data?.success) {
        console.log('Bulk deals received:', bulkDealsResponse.data.data);
        setBulkDeals(bulkDealsResponse.data.data || []);
      } else {
        console.error('Bulk deals failed:', bulkDealsResponse?.data?.error || 'Unknown error');
        setBulkDeals([]);
      }
    } catch (error) {
      console.error('Unexpected error:', error);
      alert('Error generating analysis: ' + (error.message || 'Unknown error'));
    } finally {
      setLoading(false);
    }
  };

  const handlePeriodChange = async (period) => {
    if (!searchQuery.trim()) return;
    setSelectedPeriod(period);
    setLoading(true);
    try {
      const data = await fetchHistoricalData(searchQuery.toUpperCase(), period);
      setHistoricalData(data);
    } catch (error) {
      console.error('Error changing period:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleRunScreener = async () => {
    console.log('=== STOCK SCREENER - START ===');
    console.log('1. Function called - handleRunScreener');
    console.log('2. Current screenerCriteria state:', JSON.stringify(screenerCriteria, null, 2));
    
    setScreenerLoading(true);
    setScreenerResults(null);
    
    const startTime = Date.now();
    
    try {
      // Build parameters
      const params = new URLSearchParams({
        max_peg: screenerCriteria.max_peg.toString(),
        min_pe: screenerCriteria.min_pe.toString(),
        max_pe: screenerCriteria.max_pe.toString(),
        max_debt_to_equity: screenerCriteria.max_debt_to_equity.toString(),
        min_sales_growth: screenerCriteria.min_sales_growth.toString(),
        min_profit_growth: screenerCriteria.min_profit_growth.toString(),
        require_margin_improvement: screenerCriteria.require_margin_improvement.toString()
      });
      
      const apiUrl = `http://localhost:5000/api/screen-stocks?${params.toString()}`;
      
      console.log('3. API Request Details:');
      console.log('   - URL:', apiUrl);
      console.log('   - Parameters:', {
        max_peg: screenerCriteria.max_peg,
        min_pe: screenerCriteria.min_pe,
        max_pe: screenerCriteria.max_pe,
        max_debt_to_equity: screenerCriteria.max_debt_to_equity,
        min_sales_growth: screenerCriteria.min_sales_growth,
        min_profit_growth: screenerCriteria.min_profit_growth,
        require_margin_improvement: screenerCriteria.require_margin_improvement
      });
      console.log('   - Query string:', params.toString());
      console.log('   - Request started at:', new Date().toISOString());
      
      const response = await axios.get(apiUrl, {
        timeout: 60000 // 1 minute timeout
      });
      
      const endTime = Date.now();
      const duration = ((endTime - startTime) / 1000).toFixed(2);
      
      console.log('4. API Response Received:');
      console.log('   - Status:', response.status);
      console.log('   - Response time:', duration + 's');
      console.log('   - Full response:', JSON.stringify(response.data, null, 2));
      console.log('   - Response received at:', new Date().toISOString());
      
      if (response.data.success) {
        const results = response.data.data || [];
        console.log('5. Success - Processing results:');
        console.log('   - Results count:', results.length);
        console.log('   - Results data:', JSON.stringify(results, null, 2));
        
        setScreenerResults(results);
        console.log(`6. ✅ SUCCESS: Found ${results.length} matching stocks`);
      } else {
        const errorMsg = response.data.error || 'Failed to screen stocks';
        console.error('5. ❌ API Error Response:');
        console.error('   - Error message:', errorMsg);
        console.error('   - Full error data:', response.data);
        alert('Error: ' + errorMsg);
        setScreenerResults([]);
      }
    } catch (error) {
      const endTime = Date.now();
      const duration = ((endTime - startTime) / 1000).toFixed(2);
      
      console.error('4. ❌ Exception Caught:');
      console.error('   - Error type:', error.name);
      console.error('   - Error message:', error.message);
      console.error('   - Error code:', error.code);
      console.error('   - Duration before error:', duration + 's');
      console.error('   - Full error object:', error);
      
      if (error.code === 'ECONNABORTED') {
        console.error('   - Error type: TIMEOUT');
        alert('Screening timed out. This should take 30-60 seconds. Please try again.');
      } else if (error.response) {
        console.error('   - Error type: SERVER RESPONSE ERROR');
        console.error('   - Status:', error.response.status);
        console.error('   - Status text:', error.response.statusText);
        console.error('   - Response data:', error.response.data);
        const errorMsg = error.response.data?.error || error.response.statusText || 'Unknown error';
        alert('Error screening stocks: ' + errorMsg);
      } else if (error.request) {
        console.error('   - Error type: NO RESPONSE');
        console.error('   - Request object:', error.request);
        alert('Cannot connect to server. Please make sure the backend is running on port 5000.');
      } else {
        console.error('   - Error type: UNKNOWN');
        alert('Error screening stocks: ' + (error.message || 'Unknown error'));
      }
      setScreenerResults([]);
    } finally {
      setScreenerLoading(false);
      console.log('7. Function completed - Loading state set to false');
      console.log('=== STOCK SCREENER - END ===\n');
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <header className="bg-white shadow-md">
        <div className="container mx-auto px-4 py-6 flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold text-gray-800">Stock SWOT Analysis</h1>
            <p className="text-gray-600 mt-2">Real-time market insights</p>
          </div>
          <div className="flex items-center gap-4">
            <span className="text-gray-700">Welcome, {user?.first_name || user?.email || 'User'}</span>
            <button
              onClick={onLogout}
              className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700"
            >
              Logout
            </button>
          </div>
        </div>
      </header>
      
      <div className="container mx-auto px-4 py-8">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
          <div className="bg-white rounded-lg shadow-lg p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-2xl font-bold text-gray-800">NIFTY 50</h2>
              <div className="relative group">
                <svg className="w-5 h-5 text-gray-400 cursor-help" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <div className="absolute right-0 top-6 w-64 p-3 bg-gray-800 text-white text-xs rounded-lg shadow-lg opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200 z-50">
                  Market data is fetched once when you first log in and stored in your browser. Values are not updated in real-time. To refresh, clear your browser cache or log out and log back in.
                </div>
              </div>
            </div>
            {niftyData ? (
              <div>
                <div className="text-4xl font-bold text-blue-600 mb-2">
                  {niftyData.current_value?.toFixed(2)}
                </div>
                <div className={`text-lg ${niftyData.change >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                  {niftyData.change >= 0 ? '+' : ''}{niftyData.change?.toFixed(2)} 
                  ({niftyData.change_percent?.toFixed(2)}%)
                </div>
              </div>
            ) : (
              <div className="text-gray-500">Loading...</div>
            )}
          </div>
          
          <div className="bg-white rounded-lg shadow-lg p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-2xl font-bold text-gray-800">SENSEX</h2>
              <div className="relative group">
                <svg className="w-5 h-5 text-gray-400 cursor-help" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <div className="absolute right-0 top-6 w-64 p-3 bg-gray-800 text-white text-xs rounded-lg shadow-lg opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200 z-50">
                  Market data is fetched once when you first log in and stored in your browser. Values are not updated in real-time. To refresh, clear your browser cache or log out and log back in.
                </div>
              </div>
            </div>
            {sensexData ? (
              <div>
                <div className="text-4xl font-bold text-blue-600 mb-2">
                  {sensexData.current_value?.toFixed(2)}
                </div>
                <div className={`text-lg ${sensexData.change >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                  {sensexData.change >= 0 ? '+' : ''}{sensexData.change?.toFixed(2)} 
                  ({sensexData.change_percent?.toFixed(2)}%)
                </div>
              </div>
            ) : (
              <div className="text-gray-500">Loading...</div>
            )}
          </div>
        </div>

        {/* Stock Screener Section */}
        <div className="mb-8 bg-gradient-to-br from-emerald-50 to-teal-50 rounded-lg shadow-xl p-8 border-2 border-emerald-300">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h2 className="text-3xl font-bold text-gray-800 mb-2 flex items-center">
                <svg className="w-8 h-8 mr-3 text-emerald-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0zM13 10V3M4 10h9" />
                </svg>
                Stock Screener
              </h2>
              <p className="text-gray-600 text-sm mt-1">
                Find undervalued stocks with low PEG, reasonable P/E, low debt, and strong recent performance
              </p>
            </div>
          </div>

          {/* Criteria Display */}
          <div className="bg-white rounded-lg p-6 mb-6 border border-emerald-200 shadow-sm">
            <h3 className="text-lg font-semibold text-gray-800 mb-4">Screening Criteria</h3>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div>
                <label className="block text-sm text-gray-600 mb-1">Max PEG Ratio</label>
                <input
                  type="number"
                  step="0.1"
                  value={screenerCriteria.max_peg}
                  onChange={(e) => {
                    const newValue = parseFloat(e.target.value) || 3.0;
                    console.log('📊 Parameter changed - max_peg:', screenerCriteria.max_peg, '→', newValue);
                    setScreenerCriteria({...screenerCriteria, max_peg: newValue});
                  }}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500"
                />
              </div>
              <div>
                <label className="block text-sm text-gray-600 mb-1">Min P/E Ratio</label>
                <input
                  type="number"
                  step="0.1"
                  value={screenerCriteria.min_pe}
                  onChange={(e) => {
                    const newValue = parseFloat(e.target.value) || 5.0;
                    console.log('📊 Parameter changed - min_pe:', screenerCriteria.min_pe, '→', newValue);
                    setScreenerCriteria({...screenerCriteria, min_pe: newValue});
                  }}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500"
                />
              </div>
              <div>
                <label className="block text-sm text-gray-600 mb-1">Max P/E Ratio</label>
                <input
                  type="number"
                  step="0.1"
                  value={screenerCriteria.max_pe}
                  onChange={(e) => {
                    const newValue = parseFloat(e.target.value) || 35.0;
                    console.log('📊 Parameter changed - max_pe:', screenerCriteria.max_pe, '→', newValue);
                    setScreenerCriteria({...screenerCriteria, max_pe: newValue});
                  }}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500"
                />
              </div>
              <div>
                <label className="block text-sm text-gray-600 mb-1">Max Debt/Equity</label>
                <input
                  type="number"
                  step="0.1"
                  value={screenerCriteria.max_debt_to_equity}
                  onChange={(e) => {
                    const newValue = parseFloat(e.target.value) || 1.0;
                    console.log('📊 Parameter changed - max_debt_to_equity:', screenerCriteria.max_debt_to_equity, '→', newValue);
                    setScreenerCriteria({...screenerCriteria, max_debt_to_equity: newValue});
                  }}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500"
                />
              </div>
              <div>
                <label className="block text-sm text-gray-600 mb-1">Min Sales Growth (%)</label>
                <input
                  type="number"
                  step="0.1"
                  value={screenerCriteria.min_sales_growth}
                  onChange={(e) => {
                    const newValue = parseFloat(e.target.value) || 0.0;
                    console.log('📊 Parameter changed - min_sales_growth:', screenerCriteria.min_sales_growth, '→', newValue);
                    setScreenerCriteria({...screenerCriteria, min_sales_growth: newValue});
                  }}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500"
                />
              </div>
              <div>
                <label className="block text-sm text-gray-600 mb-1">Min Profit Growth (%)</label>
                <input
                  type="number"
                  step="0.1"
                  value={screenerCriteria.min_profit_growth}
                  onChange={(e) => {
                    const newValue = parseFloat(e.target.value) || 0.0;
                    console.log('📊 Parameter changed - min_profit_growth:', screenerCriteria.min_profit_growth, '→', newValue);
                    setScreenerCriteria({...screenerCriteria, min_profit_growth: newValue});
                  }}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500"
                />
              </div>
              <div className="md:col-span-2 flex items-center">
                <label className="flex items-center cursor-pointer">
                  <input
                    type="checkbox"
                    checked={screenerCriteria.require_margin_improvement}
                    onChange={(e) => {
                      const newValue = e.target.checked;
                      console.log('📊 Parameter changed - require_margin_improvement:', screenerCriteria.require_margin_improvement, '→', newValue);
                      setScreenerCriteria({...screenerCriteria, require_margin_improvement: newValue});
                    }}
                    className="w-5 h-5 text-emerald-600 rounded focus:ring-emerald-500"
                  />
                  <span className="ml-2 text-sm text-gray-700">Require Margin Improvement</span>
                </label>
              </div>
            </div>
            <button
              onClick={handleRunScreener}
              disabled={screenerLoading}
              className="mt-6 w-full px-6 py-3 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700 disabled:opacity-50 font-semibold text-lg shadow-md transition-all flex items-center justify-center"
            >
              {screenerLoading ? (
                <>
                  <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  Screening Stocks... (This should take 30-60 seconds)
                </>
              ) : (
                <>
                  <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                  </svg>
                  Run Stock Screener
                </>
              )}
            </button>
          </div>

          {/* Results Display */}
          {screenerResults !== null && (
            <div className="bg-white rounded-lg p-6 border border-emerald-200 shadow-lg">
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-2xl font-bold text-gray-800">
                  Screener Results
                  <span className="ml-3 text-lg font-normal text-emerald-600">
                    ({screenerResults && screenerResults.length > 0 ? `Top ${Math.min(screenerResults.length, 10)} stocks found` : '0 stocks found'})
                  </span>
                </h3>
                {screenerResults && screenerResults.length > 0 && (
                  <span className="text-xs text-gray-500 bg-gray-100 px-3 py-1 rounded-full">
                    Showing top 10 matches
                  </span>
                )}
              </div>

              {screenerResults && screenerResults.length > 0 ? (
                <div className="overflow-x-auto">
                  <table className="min-w-full divide-y divide-gray-200">
                    <thead className="bg-gradient-to-r from-emerald-100 to-teal-100">
                      <tr>
                        <th className="px-4 py-3 text-left text-xs font-bold text-gray-700 uppercase tracking-wider">Rank</th>
                        <th className="px-4 py-3 text-left text-xs font-bold text-gray-700 uppercase tracking-wider">Symbol</th>
                        <th className="px-4 py-3 text-left text-xs font-bold text-gray-700 uppercase tracking-wider">Company</th>
                        <th className="px-4 py-3 text-left text-xs font-bold text-gray-700 uppercase tracking-wider">Sector</th>
                        <th className="px-4 py-3 text-right text-xs font-bold text-gray-700 uppercase tracking-wider">Price</th>
                        <th className="px-4 py-3 text-right text-xs font-bold text-gray-700 uppercase tracking-wider">P/E</th>
                        <th className="px-4 py-3 text-right text-xs font-bold text-gray-700 uppercase tracking-wider">PEG</th>
                        <th className="px-4 py-3 text-right text-xs font-bold text-gray-700 uppercase tracking-wider">
                          <div className="flex items-center justify-end gap-1">
                            D/E
                            <div className="relative group">
                              <svg className="w-4 h-4 text-gray-400 cursor-help" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                              </svg>
                              <div className="absolute right-0 top-6 w-48 p-2 bg-gray-800 text-white text-xs rounded-lg shadow-lg opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200 z-50">
                                Debt-to-Equity ratio. Lower is better. 0.00 means no debt or data unavailable.
                              </div>
                            </div>
                          </div>
                        </th>
                        <th className="px-4 py-3 text-right text-xs font-bold text-gray-700 uppercase tracking-wider">
                          <div className="flex items-center justify-end gap-1">
                            Sales%
                            <div className="relative group">
                              <svg className="w-4 h-4 text-gray-400 cursor-help" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                              </svg>
                              <div className="absolute right-0 top-6 w-56 p-2 bg-gray-800 text-white text-xs rounded-lg shadow-lg opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200 z-50">
                                Quarterly sales growth percentage. Shows N/A if quarterly data is unavailable.
                              </div>
                            </div>
                          </div>
                        </th>
                        <th className="px-4 py-3 text-right text-xs font-bold text-gray-700 uppercase tracking-wider">
                          <div className="flex items-center justify-end gap-1">
                            Profit%
                            <div className="relative group">
                              <svg className="w-4 h-4 text-gray-400 cursor-help" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                              </svg>
                              <div className="absolute right-0 top-6 w-56 p-2 bg-gray-800 text-white text-xs rounded-lg shadow-lg opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200 z-50">
                                Quarterly profit growth percentage. Shows N/A if quarterly data is unavailable.
                              </div>
                            </div>
                          </div>
                        </th>
                        <th className="px-4 py-3 text-center text-xs font-bold text-gray-700 uppercase tracking-wider">
                          <div className="flex items-center justify-center gap-1">
                            Score
                            <div className="relative group">
                              <svg className="w-4 h-4 text-gray-400 cursor-help" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                              </svg>
                              <div className="absolute right-0 top-6 w-72 p-3 bg-gray-800 text-white text-xs rounded-lg shadow-lg opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200 z-50">
                                Match score ranks stocks based on: PEG ratio (0-20 pts), P/E ratio (0-15 pts), Debt level (0-20 pts), Sales growth (0-15 pts), Profit growth (0-15 pts), Margin improvement (+10 pts), Debt trend (+10 pts). Higher score = better match.
                              </div>
                            </div>
                          </div>
                        </th>
                      </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                      {screenerResults.slice(0, 10).map((stock, idx) => (
                        <tr 
                          key={idx} 
                          className={`hover:bg-emerald-50 transition-colors cursor-pointer ${idx % 2 === 0 ? 'bg-white' : 'bg-gray-50'}`}
                          onClick={() => {
                            console.log('🖱️ Stock row clicked:', stock.symbol);
                            // Set the search query immediately
                            setSearchQuery(stock.symbol);
                            
                            // Scroll to the search section and trigger analysis
                            setTimeout(() => {
                              const searchInput = document.querySelector('input[placeholder*="Enter stock symbol"]');
                              if (searchInput) {
                                // Set the value directly in the input field
                                searchInput.value = stock.symbol;
                                // Trigger React's onChange event
                                const event = new Event('input', { bubbles: true });
                                searchInput.dispatchEvent(event);
                                
                                // Scroll to the search section
                                searchInput.scrollIntoView({ behavior: 'smooth', block: 'center' });
                                searchInput.focus();
                              }
                              
                              // Call handleSearch directly with the symbol (bypasses state update delay)
                              console.log('🔍 Triggering search for:', stock.symbol);
                              handleSearch(stock.symbol);
                            }, 150);
                          }}
                          title={`Click to analyze ${stock.symbol}`}
                        >
                          <td className="px-4 py-4 whitespace-nowrap">
                            <span className={`inline-flex items-center justify-center w-8 h-8 rounded-full font-bold text-sm ${
                              idx === 0 ? 'bg-yellow-400 text-yellow-900' :
                              idx === 1 ? 'bg-gray-300 text-gray-800' :
                              idx === 2 ? 'bg-orange-300 text-orange-900' :
                              'bg-gray-100 text-gray-700'
                            }`}>
                              {idx + 1}
                            </span>
                          </td>
                          <td className="px-4 py-4 whitespace-nowrap">
                            <span className="font-bold text-blue-600">{stock.symbol}</span>
                          </td>
                          <td className="px-4 py-4">
                            <div className="text-sm font-medium text-gray-900">{stock.name}</div>
                            <div className="text-xs text-gray-500">{stock.market_cap}</div>
                          </td>
                          <td className="px-4 py-4 whitespace-nowrap text-sm text-gray-600">
                            {stock.sector}
                          </td>
                          <td className="px-4 py-4 whitespace-nowrap text-right text-sm font-semibold text-gray-900">
                            ₹{stock.current_price?.toFixed(2) || 'N/A'}
                          </td>
                          <td className="px-4 py-4 whitespace-nowrap text-right text-sm text-gray-700">
                            {stock.pe_ratio?.toFixed(2) || 'N/A'}
                          </td>
                          <td className="px-4 py-4 whitespace-nowrap text-right">
                            <span className={`text-sm font-semibold ${
                              stock.peg_ratio < 1 ? 'text-green-600' :
                              stock.peg_ratio < 2 ? 'text-emerald-600' :
                              'text-gray-600'
                            }`}>
                              {stock.peg_ratio?.toFixed(2) || 'N/A'}
                            </span>
                          </td>
                          <td className="px-4 py-4 whitespace-nowrap text-right">
                            <span className={`text-sm font-semibold ${
                              stock.debt_to_equity === 0 || !stock.debt_to_equity ? 'text-green-600' :
                              stock.debt_to_equity < 0.3 ? 'text-emerald-600' :
                              stock.debt_to_equity < 0.5 ? 'text-yellow-600' :
                              'text-gray-600'
                            }`}>
                              {stock.debt_to_equity && stock.debt_to_equity > 0 ? stock.debt_to_equity.toFixed(2) : 'N/A'}
                            </span>
                          </td>
                          <td className="px-4 py-4 whitespace-nowrap text-right">
                            <span className={`text-sm font-semibold ${
                              stock.sales_growth > 15 ? 'text-green-600' :
                              stock.sales_growth > 10 ? 'text-emerald-600' :
                              stock.sales_growth > 0 ? 'text-gray-600' :
                              'text-gray-400'
                            }`}>
                              {stock.sales_growth && stock.sales_growth !== 0 ? stock.sales_growth.toFixed(2) + '%' : 'N/A'}
                            </span>
                          </td>
                          <td className="px-4 py-4 whitespace-nowrap text-right">
                            <span className={`text-sm font-semibold ${
                              stock.profit_growth > 20 ? 'text-green-600' :
                              stock.profit_growth > 10 ? 'text-emerald-600' :
                              stock.profit_growth > 0 ? 'text-gray-600' :
                              'text-gray-400'
                            }`}>
                              {stock.profit_growth && stock.profit_growth !== 0 ? stock.profit_growth.toFixed(2) + '%' : 'N/A'}
                            </span>
                          </td>
                          <td className="px-4 py-4 whitespace-nowrap text-center">
                            <div className="flex items-center justify-center">
                              <span className="text-sm font-bold text-emerald-600 bg-emerald-100 px-2 py-1 rounded">
                                {stock.match_score?.toFixed(0) || 'N/A'}
                              </span>
                            </div>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              ) : (
                <div className="text-center py-12">
                  <svg className="w-16 h-16 mx-auto text-gray-400 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  <p className="text-gray-600 text-lg font-medium">No stocks found matching the criteria</p>
                  <p className="text-gray-500 text-sm mt-2">Try relaxing some criteria to see more results</p>
                </div>
              )}
            </div>
          )}
        </div>

        <div className="bg-white rounded-lg shadow-lg p-8">
          <h2 className="text-2xl font-bold text-gray-800 mb-6">Enter a NSE or BSE Stock code</h2>
          <div className="flex gap-4 mb-6">
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
              placeholder="Enter stock symbol (e.g., RELIANCE, TCS, INFY)"
              className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <button
              onClick={handleSearch}
              disabled={loading}
              className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
            >
              {loading ? 'Analyzing...' : 'Analyze'}
            </button>
          </div>

          {stockDetails && (
            <div className="mb-6 bg-gradient-to-br from-purple-50 to-blue-50 rounded-lg p-6 border-2 border-purple-200">
              <h3 className="text-2xl font-bold text-gray-800 mb-4">{stockDetails.name || stockDetails.symbol}</h3>
              <p className="text-gray-600 mb-4">Sector: {stockDetails.sector}</p>
              
              <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
                <div className="bg-white p-4 rounded-lg shadow">
                  <div className="text-sm text-gray-600 mb-1">Current Price</div>
                  <div className="text-xl font-bold text-blue-600">₹{stockDetails.current_price}</div>
                </div>
                <div className="bg-white p-4 rounded-lg shadow">
                  <div className="text-sm text-gray-600 mb-1">Market Cap</div>
                  <div className="text-xl font-bold text-purple-600">{stockDetails.market_cap}</div>
                </div>
                <div className="bg-white p-4 rounded-lg shadow">
                  <div className="text-sm text-gray-600 mb-1">P/E Ratio</div>
                  <div className="text-xl font-bold text-indigo-600">{stockDetails.pe_ratio}</div>
                </div>
                <div className="bg-white p-4 rounded-lg shadow">
                  <div className="text-sm text-gray-600 mb-1">Book Value</div>
                  <div className="text-xl font-bold text-teal-600">₹{stockDetails.book_value}</div>
                </div>
                <div className="bg-white p-4 rounded-lg shadow">
                  <div className="text-sm text-gray-600 mb-1">ROE (%)</div>
                  <div className="text-xl font-bold text-green-600">{stockDetails.roe}%</div>
                </div>
                <div className="bg-white p-4 rounded-lg shadow">
                  <div className="text-sm text-gray-600 mb-1">ROCE (%)</div>
                  <div className="text-xl font-bold text-emerald-600">{stockDetails.roce}%</div>
                </div>
                <div className="bg-white p-4 rounded-lg shadow">
                  <div className="text-sm text-gray-600 mb-1">Dividend Yield</div>
                  <div className="text-xl font-bold text-yellow-600">{stockDetails.dividend_yield}%</div>
                </div>
                <div className="bg-white p-4 rounded-lg shadow">
                  <div className="text-sm text-gray-600 mb-1">52W Range</div>
                  <div className="text-sm font-semibold text-gray-800">
                    ₹{stockDetails['52w_low']} - ₹{stockDetails['52w_high']}
                  </div>
                </div>
              </div>
            </div>
          )}

          {historicalData && (
            <div className="mb-6 bg-white rounded-lg p-6 border-2 border-blue-200 shadow-lg">
              <div className="flex justify-between items-center mb-4">
                <h3 className="text-2xl font-bold text-gray-800">Price Movement Chart</h3>
                <div className="flex gap-2">
                  <button
                    onClick={() => handlePeriodChange('1y')}
                    className={`px-4 py-2 rounded-lg font-semibold transition-all ${
                      selectedPeriod === '1y' 
                        ? 'bg-blue-600 text-white shadow-md' 
                        : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                    }`}
                  >
                    1 Year
                  </button>
                  <button
                    onClick={() => handlePeriodChange('3y')}
                    className={`px-4 py-2 rounded-lg font-semibold transition-all ${
                      selectedPeriod === '3y' 
                        ? 'bg-blue-600 text-white shadow-md' 
                        : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                    }`}
                  >
                    3 Years
                  </button>
                  <button
                    onClick={() => handlePeriodChange('5y')}
                    className={`px-4 py-2 rounded-lg font-semibold transition-all ${
                      selectedPeriod === '5y' 
                        ? 'bg-blue-600 text-white shadow-md' 
                        : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                    }`}
                  >
                    5 Years
                  </button>
                  <button
                    onClick={() => handlePeriodChange('all')}
                    className={`px-4 py-2 rounded-lg font-semibold transition-all ${
                      selectedPeriod === 'all' 
                        ? 'bg-blue-600 text-white shadow-md' 
                        : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                    }`}
                  >
                    All Time
                  </button>
                </div>
              </div>
              <div className="h-96 bg-gray-50 rounded-lg p-4 border border-gray-200">
                <canvas ref={chartCanvasRef}></canvas>
              </div>
            </div>
          )}

          {swotData && (
            <div>
              <h3 className="text-2xl font-bold text-gray-800 mb-6">SWOT</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="border-2 border-green-200 rounded-lg p-5 bg-green-50">
                <h3 className="text-xl font-bold text-green-800 mb-4">✓ Strengths</h3>
                <ul className="space-y-2">
                  {swotData.strengths?.map((item, idx) => (
                    <li key={idx} className="text-gray-700">• {item}</li>
                  ))}
                </ul>
              </div>
              <div className="border-2 border-red-200 rounded-lg p-5 bg-red-50">
                <h3 className="text-xl font-bold text-red-800 mb-4">✗ Weaknesses</h3>
                <ul className="space-y-2">
                  {swotData.weaknesses?.map((item, idx) => (
                    <li key={idx} className="text-gray-700">• {item}</li>
                  ))}
                </ul>
              </div>
              <div className="border-2 border-blue-200 rounded-lg p-5 bg-blue-50">
                <h3 className="text-xl font-bold text-blue-800 mb-4">↑ Opportunities</h3>
                <ul className="space-y-2">
                  {swotData.opportunities?.map((item, idx) => (
                    <li key={idx} className="text-gray-700">• {item}</li>
                  ))}
                </ul>
              </div>
              <div className="border-2 border-orange-200 rounded-lg p-5 bg-orange-50">
                <h3 className="text-xl font-bold text-orange-800 mb-4">↓ Threats</h3>
                <ul className="space-y-2">
                  {swotData.threats?.map((item, idx) => (
                    <li key={idx} className="text-gray-700">• {item}</li>
                  ))}
                </ul>
              </div>
              </div>
            </div>
          )}

          {stockDetails && stockDetails.quarterly_results && stockDetails.quarterly_results.headers && stockDetails.quarterly_results.rows && (
            <div className="mb-6 bg-gradient-to-br from-gray-50 to-slate-50 rounded-lg p-6 border-2 border-gray-300">
              <h3 className="text-2xl font-bold text-gray-800 mb-2">Quarterly Results</h3>
              <p className="text-sm text-gray-600 mb-4">Figures in Rs. Crores</p>
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200 bg-white rounded-lg shadow">
                  <thead className="bg-gray-100">
                    <tr>
                      {stockDetails.quarterly_results.headers.map((header, idx) => (
                        <th key={idx} className="px-4 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider border-b">
                          {header}
                        </th>
                      ))}
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {stockDetails.quarterly_results.rows.filter(row => 
                      !row.some(cell => typeof cell === 'string' && cell.toLowerCase().includes('raw pdf'))
                    ).map((row, rowIdx) => (
                      <tr key={rowIdx} className={rowIdx % 2 === 0 ? 'bg-white' : 'bg-gray-50'}>
                        {row.map((cell, cellIdx) => (
                          <td key={cellIdx} className="px-4 py-3 whitespace-nowrap text-sm text-gray-700">
                            {cell}
                          </td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {companyInfo && (
            <div className="mt-6 bg-white rounded-lg shadow-lg p-6 border-2 border-indigo-200">
              <h3 className="text-2xl font-bold text-gray-800 mb-6">Company News & Updates</h3>
              
              {companyInfo.news && companyInfo.news.length > 0 && (
                <div className="mb-6">
                  <h4 className="text-xl font-semibold text-indigo-800 mb-4 flex items-center">
                    <svg className="w-6 h-6 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 20H5a2 2 0 01-2-2V6a2 2 0 012-2h10a2 2 0 012 2v1m2 13a2 2 0 01-2-2V7m2 13a2 2 0 002-2V9a2 2 0 00-2-2h-2m-4-3H9M7 16h6M7 8h6v4H7V8z" />
                    </svg>
                    Latest News & Updates
                  </h4>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                    {companyInfo.news.map((newsItem, idx) => (
                      <a
                        key={idx}
                        href={newsItem.link}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="flex items-center justify-between p-4 bg-gradient-to-r from-blue-50 to-cyan-50 rounded-lg border border-blue-200 hover:shadow-md transition-shadow"
                      >
                        <div className="flex-1">
                          <p className="font-semibold text-gray-800 text-sm">{newsItem.title}</p>
                          <p className="text-xs text-gray-600 mt-1">Source: {newsItem.source}</p>
                        </div>
                        <svg className="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                        </svg>
                      </a>
                    ))}
                  </div>
                </div>
              )}

              {companyInfo.twitter && companyInfo.twitter.length > 0 && (
                <div>
                  <h4 className="text-xl font-semibold text-indigo-800 mb-4 flex items-center">
                    <svg className="w-6 h-6 mr-2" fill="currentColor" viewBox="0 0 24 24">
                      <path d="M23 3a10.9 10.9 0 01-3.14 1.53 4.48 4.48 0 00-7.86 3v1A10.66 10.66 0 013 4s-4 9 5 13a11.64 11.64 0 01-7 2c9 5 20 0 20-11.5a4.5 4.5 0 00-.08-.83A7.72 7.72 0 0023 3z"/>
                    </svg>
                    Tweets
                  </h4>
                  <div className="space-y-4">
                    {companyInfo.twitter.map((feed, feedIdx) => {
                      const hasTweets = feed.tweets && Array.isArray(feed.tweets) && feed.tweets.length > 0;
                      return (
                        <div key={feedIdx} className="bg-gradient-to-r from-sky-50 to-blue-50 rounded-lg p-4 border border-sky-200">
                          <div className="flex items-center mb-3">
                            <svg className="w-5 h-5 text-sky-500 mr-2" fill="currentColor" viewBox="0 0 24 24">
                              <path d="M23 3a10.9 10.9 0 01-3.14 1.53 4.48 4.48 0 00-7.86 3v1A10.66 10.66 0 013 4s-4 9 5 13a11.64 11.64 0 01-7 2c9 5 20 0 20-11.5a4.5 4.5 0 00-.08-.83A7.72 7.72 0 0023 3z"/>
                            </svg>
                            <span className="font-bold text-sky-700">{feed.handle}</span>
                            <span className="text-gray-600 text-sm ml-2">• {feed.name}</span>
                          </div>
                          {hasTweets ? (
                            <div className="overflow-hidden h-64 relative">
                              <div className="animate-scroll-tweets absolute w-full">
                                {feed.tweets.map((tweet, tweetIdx) => (
                                  <div key={tweetIdx} className="mb-4 p-3 bg-white rounded-lg border border-sky-100 shadow-sm">
                                    <p className="text-gray-800 text-sm leading-relaxed">{tweet.text}</p>
                                  </div>
                                ))}
                                {feed.tweets.map((tweet, tweetIdx) => (
                                  <div key={`dup-${tweetIdx}`} className="mb-4 p-3 bg-white rounded-lg border border-sky-100 shadow-sm">
                                    <p className="text-gray-800 text-sm leading-relaxed">{tweet.text}</p>
                                  </div>
                                ))}
                              </div>
                            </div>
                          ) : (
                            <div className="p-6 text-center text-gray-500 text-sm bg-white rounded-lg border border-sky-100">
                              <svg className="w-12 h-12 mx-auto mb-3 text-gray-400" fill="currentColor" viewBox="0 0 24 24">
                                <path d="M23 3a10.9 10.9 0 01-3.14 1.53 4.48 4.48 0 00-7.86 3v1A10.66 10.66 0 013 4s-4 9 5 13a11.64 11.64 0 01-7 2c9 5 20 0 20-11.5a4.5 4.5 0 00-.08-.83A7.72 7.72 0 0023 3z"/>
                              </svg>
                              <p className="font-medium">Tweets unavailable</p>
                              <p className="text-xs mt-2 text-gray-400">Twitter API integration required for live tweets</p>
                              <p className="text-xs mt-1 text-gray-400">Please integrate Twitter API v2 for real-time tweet fetching</p>
                            </div>
                          )}
                        </div>
                      );
                    })}
                  </div>
                </div>
              )}
            </div>
          )}

          {bulkDeals !== null && (
            <div className="mt-6 bg-white rounded-lg shadow-lg p-6 border-2 border-yellow-200">
              <h3 className="text-2xl font-bold text-gray-800 mb-4">Bulk Deals (Last 180 Days)</h3>
              {bulkDeals.length > 0 ? (
                <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200 bg-white rounded-lg shadow">
                  <thead className="bg-gray-100">
                    <tr>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider border-b">Date</th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider border-b">Buyer</th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider border-b">Seller</th>
                      <th className="px-4 py-3 text-right text-xs font-medium text-gray-700 uppercase tracking-wider border-b">Quantity</th>
                      <th className="px-4 py-3 text-right text-xs font-medium text-gray-700 uppercase tracking-wider border-b">Price (₹)</th>
                      <th className="px-4 py-3 text-right text-xs font-medium text-gray-700 uppercase tracking-wider border-b">Value (₹)</th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {bulkDeals.map((deal, idx) => (
                      <tr key={idx} className={idx % 2 === 0 ? 'bg-white' : 'bg-gray-50'}>
                        <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-700">
                          {deal.date_display || deal.date}
                        </td>
                        <td className="px-4 py-3 text-sm text-gray-700 max-w-xs truncate" title={deal.buyer}>
                          {deal.buyer || '-'}
                        </td>
                        <td className="px-4 py-3 text-sm text-gray-700 max-w-xs truncate" title={deal.seller}>
                          {deal.seller || '-'}
                        </td>
                        <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-700 text-right">
                          {deal.quantity ? deal.quantity.toLocaleString('en-IN') : '-'}
                        </td>
                        <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-700 text-right">
                          {deal.price ? `₹${deal.price.toLocaleString('en-IN')}` : '-'}
                        </td>
                        <td className="px-4 py-3 whitespace-nowrap text-sm font-semibold text-gray-800 text-right">
                          {deal.value ? `₹${deal.value.toLocaleString('en-IN')}` : '-'}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
                </div>
              ) : (
                <div className="text-center py-8 text-gray-500">
                  <p>No bulk deals found for this stock in the last 180 days.</p>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

// Main App Component with Authentication
function App() {
  const [user, setUser] = useState(null);
  const [authToken, setAuthToken] = useState(null);
  const [currentPage, setCurrentPage] = useState('loading'); // Start with loading state
  const [passwordToken, setPasswordToken] = useState(null);
  const [passwordTokenType, setPasswordTokenType] = useState('create_password');

  useEffect(() => {
    const urlParams = new URLSearchParams(window.location.search);
    const createToken = urlParams.get('token');
    const resetToken = urlParams.get('resetToken');
    
    if (createToken) {
      setPasswordToken(createToken);
      setPasswordTokenType('create_password');
      setCurrentPage('password-create');
      return;
    }
    
    if (resetToken) {
      setPasswordToken(resetToken);
      setPasswordTokenType('reset_password');
      setCurrentPage('password-reset');
      return;
    }

    const token = localStorage.getItem('authToken');
    const userStr = localStorage.getItem('user');
    
    // Set maximum loading timeout (3 seconds total)
    const maxLoadingTimeout = setTimeout(() => {
      console.log('Maximum loading timeout exceeded, redirecting to login');
      localStorage.removeItem('authToken');
      localStorage.removeItem('user');
      setCurrentPage('login');
    }, 3000);
    
    if (token && userStr) {
      // Quick check: Try to decode JWT token to check expiration locally
      try {
        const tokenParts = token.split('.');
        if (tokenParts.length === 3) {
          const payload = JSON.parse(atob(tokenParts[1]));
          const exp = payload.exp * 1000; // Convert to milliseconds
          const now = Date.now();
          
          // If token is expired, skip API call and go directly to login
          if (exp < now) {
            console.log('Token expired locally, redirecting to login');
            clearTimeout(maxLoadingTimeout);
            localStorage.removeItem('authToken');
            localStorage.removeItem('user');
            setCurrentPage('login');
            return;
          }
        }
      } catch (e) {
        // If JWT parsing fails, continue with API verification
        console.log('Could not parse token, verifying via API');
      }
      
      // Set shorter timeout for API call (1.5 seconds)
      const apiTimeoutId = setTimeout(() => {
        console.log('Auth verification timeout, redirecting to login');
        clearTimeout(maxLoadingTimeout);
        localStorage.removeItem('authToken');
        localStorage.removeItem('user');
        setCurrentPage('login');
      }, 1500);
      
      axios.post('http://localhost:5000/api/verify-auth', { token }, { timeout: 1500 })
        .then(response => {
          clearTimeout(apiTimeoutId);
          clearTimeout(maxLoadingTimeout);
          if (response.data.success) {
            setAuthToken(token);
            setUser(JSON.parse(userStr));
            setCurrentPage('app');
          } else {
            // Token invalid or expired
            localStorage.removeItem('authToken');
            localStorage.removeItem('user');
            setCurrentPage('login');
          }
        })
        .catch(error => {
          clearTimeout(apiTimeoutId);
          clearTimeout(maxLoadingTimeout);
          console.log('Auth verification failed:', error.message);
          // On any error (network, timeout, or expired), go to login
          localStorage.removeItem('authToken');
          localStorage.removeItem('user');
          setCurrentPage('login');
        });
    } else {
      clearTimeout(maxLoadingTimeout);
      setCurrentPage('login');
    }
    
    return () => {
      clearTimeout(maxLoadingTimeout);
    };
  }, []);

  const handleLogin = (userData, token) => {
    setUser(userData);
    setAuthToken(token);
    setCurrentPage('app');
  };

  const handleLogout = () => {
    localStorage.removeItem('authToken');
    localStorage.removeItem('user');
    // Clear stored market data so fresh data is fetched on next login
    localStorage.removeItem('niftyData');
    localStorage.removeItem('sensexData');
    setUser(null);
    setAuthToken(null);
    setCurrentPage('login');
  };

  const handlePasswordCreateSuccess = (userData, token) => {
    setUser(userData);
    setAuthToken(token);
    setCurrentPage('app');
    window.history.replaceState({}, document.title, window.location.pathname);
  };

  // Show loading state
  if (currentPage === 'loading') {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  if (currentPage === 'password-create' || currentPage === 'password-reset') {
    return (
      <PasswordCreate
        token={passwordToken}
        tokenType={passwordTokenType}
        onSuccess={handlePasswordCreateSuccess}
        onBackToLogin={() => setCurrentPage('login')}
      />
    );
  }

  if (currentPage === 'app' && user && authToken) {
    return <StockAnalysis user={user} onLogout={handleLogout} />;
  }

  if (currentPage === 'register') {
    return (
      <Register
        onBackToLogin={() => setCurrentPage('login')}
        onRegistrationSuccess={() => setCurrentPage('login')}
      />
    );
  }

  if (currentPage === 'forgot-password') {
    return (
      <ForgotPassword
        onBackToLogin={() => setCurrentPage('login')}
        onSuccess={() => setCurrentPage('login')}
      />
    );
  }

  return (
    <Login
      onLogin={handleLogin}
      onSwitchToRegister={() => setCurrentPage('register')}
      onSwitchToForgotPassword={() => setCurrentPage('forgot-password')}
    />
  );
}

ReactDOM.render(<App />, document.getElementById('root'));
