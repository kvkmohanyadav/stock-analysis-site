const { useState, useEffect } = React;

function App() {
  const [niftyData, setNiftyData] = useState(null);
  const [sensexData, setSensexData] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [swotData, setSwotData] = useState(null);
  const [stockDetails, setStockDetails] = useState(null);
  const [loading, setLoading] = useState(false);

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

  const handleSearch = async () => {
    if (!searchQuery.trim()) return;
    setLoading(true);
    try {
      // Fetch both SWOT and stock details
      const [swotResponse, detailsResponse] = await Promise.all([
        axios.get(`http://localhost:5000/api/swot/${searchQuery.toUpperCase()}`),
        axios.get(`http://localhost:5000/api/stock-details/${searchQuery.toUpperCase()}`)
      ]);
      
      if (swotResponse.data.success) setSwotData(swotResponse.data.data.swot);
      if (detailsResponse.data.success) setStockDetails(detailsResponse.data.data);
    } catch (error) {
      console.error('Error:', error);
      alert('Error generating analysis');
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
        </div>
      </div>
    </div>
  );
}

ReactDOM.render(<App />, document.getElementById('root'));
