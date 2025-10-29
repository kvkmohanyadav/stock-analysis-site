  const { useState, useEffect, useRef } = React;

function App() {
  const [niftyData, setNiftyData] = useState(null);
  const [sensexData, setSensexData] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [swotData, setSwotData] = useState(null);
  const [stockDetails, setStockDetails] = useState(null);
  const [loading, setLoading] = useState(false);
  const [historicalData, setHistoricalData] = useState(null);
  const [selectedPeriod, setSelectedPeriod] = useState('1y');
  const [companyInfo, setCompanyInfo] = useState(null);
  const chartCanvasRef = useRef(null);
  const chartInstanceRef = useRef(null);

  useEffect(() => {
    const fetchMarketData = async () => {
      try {
        const nifty = await axios.get('http://localhost:5000/api/nifty50');
        const sensex = await axios.get('http://localhost:5000/api/sensex');
        if (nifty.data.success) setNiftyData(nifty.data.data);
        if (sensex.data.success) setSensexData(sensex.data.data);
      } catch (error) {
        console.error('Error:', error);
      }
    };
    fetchMarketData();
    const interval = setInterval(fetchMarketData, 5000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    // Render chart when historical data changes
    if (!historicalData || !chartCanvasRef.current || historicalData.length === 0) {
      return;
    }

    // Small delay to ensure canvas is rendered
    const timeoutId = setTimeout(() => {
      if (!chartCanvasRef.current) return;

      // Destroy existing chart if it exists
      if (chartInstanceRef.current) {
        chartInstanceRef.current.destroy();
        chartInstanceRef.current = null;
      }

      const ctx = chartCanvasRef.current.getContext('2d');
      if (!ctx) return;

      // Create labels showing only month and year for x-axis
      const labels = historicalData.map(item => {
        const date = new Date(item.date);
        return date.toLocaleDateString('en-US', { month: 'short', year: 'numeric' });
      });
      
      // Keep full date for each point for tooltip display
      const fullDates = historicalData.map(item => item.date);
      const prices = historicalData.map(item => item.close);

      if (typeof Chart === 'undefined') {
        console.error('Chart.js is not loaded');
        return;
      }

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
            // Store full dates as custom data for tooltip
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
    }, 100);

    // Cleanup on unmount
    return () => {
      clearTimeout(timeoutId);
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

  const handleSearch = async () => {
    if (!searchQuery.trim()) return;
    setLoading(true);
    try {
      const symbol = searchQuery.toUpperCase();
      // Fetch SWOT, stock details, historical data, and company info
      const [swotResponse, detailsResponse, historicalResponse, companyInfoResponse] = await Promise.all([
        axios.get(`http://localhost:5000/api/swot/${symbol}`),
        axios.get(`http://localhost:5000/api/stock-details/${symbol}`),
        axios.get(`http://localhost:5000/api/historical/${symbol}?period=${selectedPeriod}`).catch(err => {
          console.error('Historical data fetch failed:', err);
          return { data: { success: false, error: err.message } };
        }),
        axios.get(`http://localhost:5000/api/company-info/${symbol}`).catch(err => {
          console.error('Company info fetch failed:', err);
          return { data: { success: false, error: err.message } };
        })
      ]);
      
      if (swotResponse.data.success) setSwotData(swotResponse.data.data.swot);
      if (detailsResponse.data.success) setStockDetails(detailsResponse.data.data);
      if (historicalResponse.data.success) {
        setHistoricalData(historicalResponse.data.data);
        console.log('Historical data loaded:', historicalResponse.data.data.length, 'data points');
      } else {
        console.error('Historical data failed:', historicalResponse.data.error);
      }
      if (companyInfoResponse.data.success) {
        setCompanyInfo(companyInfoResponse.data.data);
      }
    } catch (error) {
      console.error('Error:', error);
      alert('Error generating analysis');
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

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <header className="bg-white shadow-md">
        <div className="container mx-auto px-4 py-6">
          <h1 className="text-3xl font-bold text-gray-800">Stock SWOT Analysis</h1>
          <p className="text-gray-600 mt-2">Real-time market insights</p>
        </div>
      </header>
      
      <div className="container mx-auto px-4 py-8">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
          <div className="bg-white rounded-lg shadow-lg p-6">
            <h2 className="text-2xl font-bold text-gray-800 mb-4">NIFTY 50</h2>
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
            <h2 className="text-2xl font-bold text-gray-800 mb-4">SENSEX</h2>
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

          {stockDetails && stockDetails.peer_comparison && (
            <div className="mb-6 bg-gradient-to-br from-gray-50 to-slate-50 rounded-lg p-6 border-2 border-gray-300">
              <h3 className="text-2xl font-bold text-gray-800 mb-2">Quarterly Results</h3>
              <p className="text-sm text-gray-600 mb-4">Figures in Rs. Crores</p>
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200 bg-white rounded-lg shadow">
                  <thead className="bg-gray-100">
                    <tr>
                      {stockDetails.peer_comparison.headers.map((header, idx) => (
                        <th key={idx} className="px-4 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider border-b">
                          {header}
                        </th>
                      ))}
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {stockDetails.peer_comparison.rows.filter(row => 
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

          {companyInfo && (
            <div className="mt-6 bg-white rounded-lg shadow-lg p-6 border-2 border-indigo-200">
              <h3 className="text-2xl font-bold text-gray-800 mb-6">Company News & Updates</h3>
              
              {/* News Section */}
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

              {/* Tweets Section - Show even if tweets array is empty */}
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
                                {/* Duplicate for seamless loop */}
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
        </div>
      </div>
    </div>
  );
}

ReactDOM.render(<App />, document.getElementById('root'));
