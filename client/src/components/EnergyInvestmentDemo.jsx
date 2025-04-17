import React, { useState } from 'react';
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

const EnergyInvestmentDemo = () => {
  // States for form inputs
  const [location, setLocation] = useState({ lat: 39.7392, lon: -104.9903 }); // Default: Denver
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [showLoginForm, setShowLoginForm] = useState(false);
  const [showRegisterForm, setShowRegisterForm] = useState(false);
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [systemParams, setSystemParams] = useState({
    systemCapacity: 10,
    moduleType: 1,
    arrayType: 2,
    tilt: 20,
    azimuth: 180,
    losses: 14,
    systemCostPerWatt: 2.80,
    incentivePercent: 30,
    loanPercent: 70,
    loanTerm: 20,
    loanRate: 5.5,
    analysisYears: 25,
  });
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState(null);
  const [activeTab, setActiveTab] = useState('summary');
  const [showSensitivity, setShowSensitivity] = useState(false);

  // Mock login functionality
  const handleLogin = (e) => {
    e.preventDefault();
    setLoading(true);
    
    // Simulate API call
    setTimeout(() => {
      setIsAuthenticated(true);
      setShowLoginForm(false);
      setLoading(false);
    }, 1000);
  };

  // Handle parameter changes
  const handleParamChange = (e) => {
    const { name, value, type } = e.target;
    setSystemParams({
      ...systemParams,
      [name]: type === 'number' ? parseFloat(value) : value,
    });
  };

  // Handle location changes
  const handleLocationChange = (e) => {
    const { name, value } = e.target;
    setLocation({
      ...location,
      [name]: parseFloat(value),
    });
  };

  // Mock calculation
  const handleCalculate = () => {
    setLoading(true);
    
    // Simulate API call
    setTimeout(() => {
      // Generate simulated results
      const monthNames = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
      const monthlyProduction = monthNames.map(month => {
        // Create seasonal variation with peak in summer
        const monthIndex = monthNames.indexOf(month);
        const seasonalFactor = 1 + Math.sin((monthIndex - 2) * Math.PI / 6) * 0.5;
        
        return {
          month,
          production: Math.round(systemParams.systemCapacity * 100 * seasonalFactor),
        };
      });
      
      // Calculate financial metrics
      const annualProduction = monthlyProduction.reduce((sum, month) => sum + month.production, 0);
      const costPerKwh = 0.12; // Assumed electricity rate
      const annualSavings = annualProduction * costPerKwh;
      const totalCost = systemParams.systemCapacity * 1000 * systemParams.systemCostPerWatt;
      const netCost = totalCost * (1 - systemParams.incentivePercent / 100);
      const roi = (annualSavings * systemParams.analysisYears / netCost) * 100;
      const paybackYears = netCost / annualSavings;
      
      // Generate cash flow data
      const cashFlowData = [];
      let cumulativeCashFlow = -netCost;
      
      for (let year = 1; year <= systemParams.analysisYears; year++) {
        // Simple degradation factor
        const degradationFactor = Math.pow(0.995, year - 1);
        const yearProduction = annualProduction * degradationFactor;
        const yearSavings = yearProduction * costPerKwh * Math.pow(1.025, year - 1); // 2.5% electricity inflation
        const maintenanceCost = systemParams.systemCapacity * 20; // $20 per kW
        const netCashFlow = yearSavings - maintenanceCost;
        cumulativeCashFlow += netCashFlow;
        
        cashFlowData.push({
          year: `Year ${year}`,
          savings: Math.round(yearSavings),
          costs: Math.round(maintenanceCost),
          netCashFlow: Math.round(netCashFlow),
          cumulativeCashFlow: Math.round(cumulativeCashFlow),
        });
      }
      
      // Create simulated results object
      setResults({
        production: {
          monthlyProduction,
          annualProduction,
        },
        financials: {
          totalCost,
          netCost,
          annualSavings,
          roi,
          paybackYears,
          npv: netCost * 0.8, // Simplified NPV calculation
          irr: 8.5, // Sample IRR
          cashFlowData,
        },
      });
      
      setLoading(false);
      setShowSensitivity(true);
    }, 1500);
  };

  // Format currency
  const formatCurrency = (value) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      maximumFractionDigits: 0,
    }).format(value);
  };

  // Tornado chart data for sensitivity analysis
  const tornadoData = [
    { parameter: 'System Cost', low: -15, high: 12 },
    { parameter: 'Electricity Rate', low: -10, high: 15 },
    { parameter: 'Production', low: -12, high: 10 },
    { parameter: 'Loan Rate', low: -5, high: 4 },
    { parameter: 'Electricity Inflation', low: -7, high: 9 },
  ];

  return (
    <div className="min-h-screen bg-gray-100">
      {/* Header */}
      <header className="bg-blue-600 text-white p-4 shadow-md">
        <div className="container mx-auto flex justify-between items-center">
          <h1 className="text-2xl font-bold">Energy Investment Decision Support System</h1>
          
          <div className="flex items-center space-x-4">
            {isAuthenticated ? (
              <>
                <button className="bg-blue-500 hover:bg-blue-700 text-white py-1 px-3 rounded">
                  My Projects
                </button>
                <span className="text-sm">Welcome, {username || 'User'}</span>
                <button 
                  onClick={() => setIsAuthenticated(false)}
                  className="bg-blue-500 hover:bg-blue-700 text-white py-1 px-3 rounded"
                >
                  Logout
                </button>
              </>
            ) : (
              <>
                <button 
                  onClick={() => setShowLoginForm(true)}
                  className="bg-blue-500 hover:bg-blue-700 text-white py-1 px-3 rounded"
                >
                  Login
                </button>
                <button 
                  onClick={() => setShowRegisterForm(true)}
                  className="bg-blue-500 hover:bg-blue-700 text-white py-1 px-3 rounded"
                >
                  Register
                </button>
              </>
            )}
          </div>
        </div>
      </header>
      
      <main className="container mx-auto px-4 py-8">
        <div className="mb-8">
          <h2 className="text-2xl font-bold text-gray-900">Analyze renewable energy potential and financial returns</h2>
          <p className="text-gray-600 mt-2">
            Select a location, configure your system, and calculate the results
          </p>
        </div>
        
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Left column: Map (simulated) */}
          <div className="lg:col-span-2">
            <div className="bg-white rounded-lg shadow">
              <div className="p-4 border-b">
                <h2 className="text-lg font-semibold text-gray-800">Solar Resource Map</h2>
                <p className="text-sm text-gray-600">
                  Enter coordinates to select a location
                </p>
              </div>
              
              <div className="p-4">
                <div className="flex flex-col md:flex-row mb-4 gap-2">
                  <div className="flex-grow">
                    <label htmlFor="lat" className="block text-sm font-medium text-gray-700 mb-1">
                      Latitude
                    </label>
                    <input
                      type="number"
                      id="lat"
                      name="lat"
                      value={location.lat}
                      onChange={handleLocationChange}
                      step="0.0001"
                      className="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
                    />
                  </div>
                  <div className="flex-grow">
                    <label htmlFor="lon" className="block text-sm font-medium text-gray-700 mb-1">
                      Longitude
                    </label>
                    <input
                      type="number"
                      id="lon"
                      name="lon"
                      value={location.lon}
                      onChange={handleLocationChange}
                      step="0.0001"
                      className="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
                    />
                  </div>
                </div>
              </div>
              
              <div className="bg-gray-200 h-96 flex items-center justify-center rounded-b-lg">
                <div className="text-center text-gray-500">
                  <p>Map visualization would appear here</p>
                  <p className="text-sm mt-2">Current location: {location.lat.toFixed(4)}, {location.lon.toFixed(4)}</p>
                </div>
              </div>
            </div>
          </div>
          
          {/* Right column: Parameters form */}
          <div>
            <form className="bg-white p-4 rounded-lg shadow">
              <h2 className="text-xl font-bold mb-4 text-gray-800">System Parameters</h2>
              
              {/* System Specifications */}
              <div className="mb-4">
                <h3 className="text-lg font-semibold mb-2 text-gray-700">System Specifications</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label htmlFor="systemCapacity" className="block text-sm font-medium text-gray-700 mb-1">
                      System Capacity (kW)
                    </label>
                    <input
                      type="number"
                      id="systemCapacity"
                      name="systemCapacity"
                      min="0.5"
                      max="1000"
                      step="0.1"
                      value={systemParams.systemCapacity}
                      onChange={handleParamChange}
                      className="w-full p-2 border border-gray-300 rounded focus:ring-blue-500 focus:border-blue-500"
                    />
                  </div>
                  
                  <div>
                    <label htmlFor="moduleType" className="block text-sm font-medium text-gray-700 mb-1">
                      Module Type
                    </label>
                    <select
                      id="moduleType"
                      name="moduleType"
                      value={systemParams.moduleType}
                      onChange={handleParamChange}
                      className="w-full p-2 border border-gray-300 rounded focus:ring-blue-500 focus:border-blue-500"
                    >
                      <option value={1}>Standard (15% efficient)</option>
                      <option value={2}>Premium (19% efficient)</option>
                      <option value={3}>Thin Film (10% efficient)</option>
                    </select>
                  </div>
                </div>
              </div>
              
              {/* Financial Parameters */}
              <div className="mb-4">
                <h3 className="text-lg font-semibold mb-2 text-gray-700">Financial Parameters</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label htmlFor="systemCostPerWatt" className="block text-sm font-medium text-gray-700 mb-1">
                      System Cost ($/watt)
                    </label>
                    <input
                      type="number"
                      id="systemCostPerWatt"
                      name="systemCostPerWatt"
                      min="0.1"
                      max="10"
                      step="0.01"
                      value={systemParams.systemCostPerWatt}
                      onChange={handleParamChange}
                      className="w-full p-2 border border-gray-300 rounded focus:ring-blue-500 focus:border-blue-500"
                    />
                  </div>
                  
                  <div>
                    <label htmlFor="incentivePercent" className="block text-sm font-medium text-gray-700 mb-1">
                      Incentive (%)
                    </label>
                    <input
                      type="number"
                      id="incentivePercent"
                      name="incentivePercent"
                      min="0"
                      max="100"
                      step="1"
                      value={systemParams.incentivePercent}
                      onChange={handleParamChange}
                      className="w-full p-2 border border-gray-300 rounded focus:ring-blue-500 focus:border-blue-500"
                    />
                    <p className="text-xs text-gray-500 mt-1">
                      Federal ITC is currently 30%
                    </p>
                  </div>
                  
                  <div>
                    <label htmlFor="loanPercent" className="block text-sm font-medium text-gray-700 mb-1">
                      Loan Amount (% of cost)
                    </label>
                    <input
                      type="number"
                      id="loanPercent"
                      name="loanPercent"
                      min="0"
                      max="100"
                      step="1"
                      value={systemParams.loanPercent}
                      onChange={handleParamChange}
                      className="w-full p-2 border border-gray-300 rounded focus:ring-blue-500 focus:border-blue-500"
                    />
                  </div>
                  
                  <div>
                    <label htmlFor="loanRate" className="block text-sm font-medium text-gray-700 mb-1">
                      Interest Rate (%)
                    </label>
                    <input
                      type="number"
                      id="loanRate"
                      name="loanRate"
                      min="0"
                      max="20"
                      step="0.1"
                      value={systemParams.loanRate}
                      onChange={handleParamChange}
                      className="w-full p-2 border border-gray-300 rounded focus:ring-blue-500 focus:border-blue-500"
                    />
                  </div>
                </div>
              </div>
              
              <div className="mt-6">
                <button
                  type="button"
                  onClick={handleCalculate}
                  className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition-colors"
                  disabled={loading}
                >
                  {loading ? (
                    <span className="flex items-center justify-center">
                      <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                      </svg>
                      Calculating...
                    </span>
                  ) : (
                    'Calculate Results'
                  )}
                </button>
              </div>
            </form>
          </div>
          
          {/* Results dashboard */}
          {results && (
            <div className="lg:col-span-3 mt-8">
              <div className="bg-white p-6 rounded-lg shadow">
                <div className="mb-6">
                  <h2 className="text-xl font-bold mb-2 text-gray-800">Results Dashboard</h2>
                  {location && (
                    <p className="text-gray-600">
                      Location: {location.lat.toFixed(4)}, {location.lon.toFixed(4)}
                    </p>
                  )}
                </div>
                
                {/* Tabs */}
                <div className="mb-6 border-b border-gray-200">
                  <nav className="flex -mb-px">
                    <button
                      onClick={() => setActiveTab('summary')}
                      className={`mr-8 py-2 px-1 font-medium text-sm ${
                        activeTab === 'summary'
                          ? 'border-b-2 border-blue-500 text-blue-600'
                          : 'text-gray-500 hover:text-gray-700'
                      }`}
                    >
                      Summary
                    </button>
                    <button
                      onClick={() => setActiveTab('production')}
                      className={`mr-8 py-2 px-1 font-medium text-sm ${
                        activeTab === 'production'
                          ? 'border-b-2 border-blue-500 text-blue-600'
                          : 'text-gray-500 hover:text-gray-700'
                      }`}
                    >
                      Production
                    </button>
                    <button
                      onClick={() => setActiveTab('financial')}
                      className={`mr-8 py-2 px-1 font-medium text-sm ${
                        activeTab === 'financial'
                          ? 'border-b-2 border-blue-500 text-blue-600'
                          : 'text-gray-500 hover:text-gray-700'
                      }`}
                    >
                      Financial
                    </button>
                    <button
                      onClick={() => setActiveTab('cashflow')}
                      className={`mr-8 py-2 px-1 font-medium text-sm ${
                        activeTab === 'cashflow'
                          ? 'border-b-2 border-blue-500 text-blue-600'
                          : 'text-gray-500 hover:text-gray-700'
                      }`}
                    >
                      Cash Flow
                    </button>
                  </nav>
                </div>
                
                {/* Summary Tab */}
                {activeTab === 'summary' && (
                  <div>
                    {/* Key Metrics Cards */}
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
                      <div className="bg-yellow-100 text-yellow-800 p-4 rounded-lg">
                        <div className="flex items-center">
                          <div className="flex-shrink-0">
                            <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                            </svg>
                          </div>
                          <div className="ml-4">
                            <h3 className="text-sm font-medium">Annual Production</h3>
                            <p className="text-2xl font-bold">
                              {results.production.annualProduction.toLocaleString()} kWh
                            </p>
                          </div>
                        </div>
                      </div>

                      <div className="bg-blue-100 text-blue-800 p-4 rounded-lg">
                        <div className="flex items-center">
                          <div className="flex-shrink-0">
                            <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                            </svg>
                          </div>
                          <div className="ml-4">
                            <h3 className="text-sm font-medium">Payback Period</h3>
                            <p className="text-2xl font-bold">
                              {results.financials.paybackYears.toFixed(1)} Years
                            </p>
                          </div>
                        </div>
                      </div>

                      <div className="bg-green-100 text-green-800 p-4 rounded-lg">
                        <div className="flex items-center">
                          <div className="flex-shrink-0">
                            <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                            </svg>
                          </div>
                          <div className="ml-4">
                            <h3 className="text-sm font-medium">Return on Investment</h3>
                            <p className="text-2xl font-bold">
                              {results.financials.roi.toFixed(1)}%
                            </p>
                          </div>
                        </div>
                      </div>

                      <div className="bg-purple-100 text-purple-800 p-4 rounded-lg">
                        <div className="flex items-center">
                          <div className="flex-shrink-0">
                            <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                            </svg>
                          </div>
                          <div className="ml-4">
                            <h3 className="text-sm font-medium">Net Present Value</h3>
                            <p className="text-2xl font-bold">
                              {formatCurrency(results.financials.npv)}
                            </p>
                          </div>
                        </div>
                      </div>
                    </div>
                    
                    {/* Production Chart */}
                    <div className="mb-6">
                      <h3 className="text-lg font-semibold mb-2 text-gray-700">Annual Production</h3>
                      <div className="h-64">
                        <ResponsiveContainer width="100%" height="100%">
                          <BarChart data={results.production.monthlyProduction}>
                            <CartesianGrid strokeDasharray="3 3" />
                            <XAxis dataKey="month" />
                            <YAxis />
                            <Tooltip />
                            <Legend />
                            <Bar dataKey="production" name="Production (kWh)" fill="#1f77b4" />
                          </BarChart>
                        </ResponsiveContainer>
                      </div>
                    </div>
                  </div>
                )}
                
                {/* Production Tab */}
                {activeTab === 'production' && (
                  <div>
                    <div className="mb-6">
                      <h3 className="text-lg font-semibold mb-2 text-gray-700">Monthly Production</h3>
                      <div className="h-64">
                        <ResponsiveContainer width="100%" height="100%">
                          <BarChart data={results.production.monthlyProduction}>
                            <CartesianGrid strokeDasharray="3 3" />
                            <XAxis dataKey="month" />
                            <YAxis />
                            <Tooltip />
                            <Legend />
                            <Bar dataKey="production" name="Production (kWh)" fill="#1f77b4" />
                          </BarChart>
                        </ResponsiveContainer>
                      </div>
                      <p className="text-gray-600 text-sm mt-2">
                        Monthly production varies throughout the year based on seasonal changes in solar radiation.
                        The highest production typically occurs during summer months.
                      </p>
                    </div>
                  </div>
                )}
                
                {/* Financial Tab */}
                {activeTab === 'financial' && (
                  <div>
                    <div className="mb-6">
                      <h3 className="text-lg font-semibold mb-2 text-gray-700">Financial Metrics</h3>
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div className="bg-gray-50 p-4 rounded">
                          <h4 className="font-medium text-gray-700 mb-2">Key Metrics</h4>
                          <table className="min-w-full">
                            <tbody>
                              <tr>
                                <td className="py-1 text-sm text-gray-500">Total System Cost</td>
                                <td className="py-1 text-sm text-gray-900 font-medium">
                                  {formatCurrency(results.financials.totalCost)}
                                </td>
                              </tr>
                              <tr>
                                <td className="py-1 text-sm text-gray-500">Net Cost (After Incentives)</td>
                                <td className="py-1 text-sm text-gray-900 font-medium">
                                  {formatCurrency(results.financials.netCost)}
                                </td>
                              </tr>
                              <tr>
                                <td className="py-1 text-sm text-gray-500">Annual Savings</td>
                                <td className="py-1 text-sm text-gray-900 font-medium">
                                  {formatCurrency(results.financials.annualSavings)}
                                </td>
                              </tr>
                              <tr>
                                <td className="py-1 text-sm text-gray-500">ROI</td>
                                <td className="py-1 text-sm text-gray-900 font-medium">
                                  {results.financials.roi.toFixed(1)}%
                                </td>
                              </tr>
                              <tr>
                                <td className="py-1 text-sm text-gray-500">IRR</td>
                                <td className="py-1 text-sm text-gray-900 font-medium">
                                  {results.financials.irr.toFixed(1)}%
                                </td>
                              </tr>
                              <tr>
                                <td className="py-1 text-sm text-gray-500">Payback Period</td>
                                <td className="py-1 text-sm text-gray-900 font-medium">
                                  {results.financials.paybackYears.toFixed(1)} years
                                </td>
                              </tr>
                            </tbody>
                          </table>
                        </div>
                        
                        <div className="h-64">
                          <ResponsiveContainer width="100%" height="100%">
                            <BarChart data={[
                              { name: 'System Cost', value: results.financials.netCost },
                              { name: 'Lifetime Savings', value: results.financials.annualSavings * systemParams.analysisYears }
                            ]}>
                              <CartesianGrid strokeDasharray="3 3" />
                              <XAxis dataKey="name" />
                              <YAxis />
                              <Tooltip formatter={(value) => formatCurrency(value)} />
                              <Legend />
                              <Bar dataKey="value" fill="#2ca02c" />
                            </BarChart>
                          </ResponsiveContainer>
                        </div>
                      </div>
                    </div>
                  </div>
                )}
                
                {/* Cash Flow Tab */}
                {activeTab === 'cashflow' && (
                  <div>
                    <div className="mb-6">
                      <h3 className="text-lg font-semibold mb-2 text-gray-700">Cumulative Cash Flow</h3>
                      <div className="h-64">
                        <ResponsiveContainer width="100%" height="100%">
                          <LineChart data={results.financials.cashFlowData}>
                            <CartesianGrid strokeDasharray="3 3" />
                            <XAxis dataKey="year" />
                            <YAxis />
                            <Tooltip formatter={(value) => formatCurrency(value)} />
                            <Legend />
                            <Line type="monotone" dataKey="cumulativeCashFlow" name="Cumulative Cash Flow" stroke="#8884d8" />
                          </LineChart>
                        </ResponsiveContainer>
                      </div>
                      <p className="text-gray-600 text-sm mt-2">
                        This chart shows your cumulative cash flow over the system lifetime.
                        The point where the line crosses into positive territory represents your payback period.
                      </p>
                    </div>
                    
                    <div className="mb-6">
                      <h3 className="text-lg font-semibold mb-2 text-gray-700">Annual Cash Flow</h3>
                      <div className="overflow-x-auto">
                        <table className="min-w-full divide-y divide-gray-200">
                          <thead className="bg-gray-50">
                            <tr>
                              <th scope="col" className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                Year
                              </th>
                              <th scope="col" className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                Savings
                              </th>
                              <th scope="col" className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                Costs
                              </th>
                              <th scope="col" className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                Net Cash Flow
                              </th>
                              <th scope="col" className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                Cumulative
                              </th>
                            </tr>
                          </thead>
                          <tbody className="bg-white divide-y divide-gray-200">
                            {results.financials.cashFlowData.slice(0, 10).map((year, index) => (
                              <tr key={index} className={year.cumulativeCashFlow >= 0 ? 'bg-green-50' : ''}>
                                <td className="px-4 py-2 whitespace-nowrap text-sm font-medium text-gray-900">
                                  {year.year}
                                </td>
                                <td className="px-4 py-2 whitespace-nowrap text-sm text-gray-500">
                                  {formatCurrency(year.savings)}
                                </td>
                                <td className="px-4 py-2 whitespace-nowrap text-sm text-gray-500">
                                  {formatCurrency(year.costs)}
                                </td>
                                <td className="px-4 py-2 whitespace-nowrap text-sm text-gray-900">
                                  {formatCurrency(year.netCashFlow)}
                                </td>
                                <td className="px-4 py-2 whitespace-nowrap text-sm font-medium" 
                                    style={{ color: year.cumulativeCashFlow >= 0 ? '#2ca02c' : '#d62728' }}>
                                  {formatCurrency(year.cumulativeCashFlow)}
                                </td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}
          
          {/* Sensitivity Analysis Section */}
          {showSensitivity && (
            <div className="lg:col-span-3 mt-8">
              <div className="bg-white p-6 rounded-lg shadow">
                <h2 className="text-2xl font-bold mb-4">Sensitivity Analysis</h2>
                
                <div className="bg-gray-50 rounded p-4 mb-6">
                  <p className="text-sm text-gray-700">
                    This chart shows how changes in each parameter affect the Net Present Value (NPV).
                    Longer bars indicate parameters with greater impact on your investment decision.
                  </p>
                </div>
                
                <div className="h-96">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart
                      data={tornadoData}
                      layout="vertical"
                      margin={{ top: 20, right: 30, left: 150, bottom: 5 }}
                    >
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis type="number" domain={['dataMin', 'dataMax']} tickFormatter={value => `${value > 0 ? '+' : ''}${value}%`} />
                      <YAxis dataKey="parameter" type="category" width={150} />
                      <Tooltip />
                      <Legend />
                      <Bar dataKey="low" name="Decrease" fill="#ef4444" />
                      <Bar dataKey="high" name="Increase" fill="#22c55e" />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </div>
            </div>
          )}
        </div>
      </main>
      
      <footer className="mt-auto pt-8 pb-4 border-t border-gray-200 text-center text-gray-500 text-sm">
        <p>Energy Investment Decision Support System Demo &copy; {new Date().getFullYear()}</p>
      </footer>
      
      {/* Login Modal */}
      {showLoginForm && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-75 flex items-center justify-center p-4 z-10">
          <div className="bg-white rounded-lg shadow-xl max-w-md w-full">
            <div className="p-4 flex justify-end">
              <button onClick={() => setShowLoginForm(false)} className="text-gray-500 text-2xl">&times;</button>
            </div>
            <div className="w-full max-w-md mx-auto">
              <form 
                onSubmit={handleLogin} 
                className="bg-white shadow-md rounded px-8 pt-6 pb-8 mb-4"
              >
                <h2 className="text-2xl font-bold mb-6 text-center text-gray-800">Log In</h2>
                
                <div className="mb-4">
                  <label 
                    className="block text-gray-700 text-sm font-bold mb-2" 
                    htmlFor="username"
                  >
                    Username or Email
                  </label>
                  <input
                    id="username"
                    type="text"
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                    className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
                    placeholder="Enter your username or email"
                  />
                </div>
                
                <div className="mb-6">
                  <label 
                    className="block text-gray-700 text-sm font-bold mb-2" 
                    htmlFor="password"
                  >
                    Password
                  </label>
                  <input
                    id="password"
                    type="password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 mb-3 leading-tight focus:outline-none focus:shadow-outline"
                    placeholder="Enter your password"
                  />
                </div>
                
                <div className="flex items-center justify-between">
                  <button
                    type="submit"
                    className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline w-full"
                  >
                    {loading ? 'Signing in...' : 'Sign In'}
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default EnergyInvestmentDemo;