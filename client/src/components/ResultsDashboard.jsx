import React, { useState } from 'react';
import { 
  LineChart, Line, BarChart, Bar, PieChart, Pie, ResponsiveContainer, 
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, Cell, 
  AreaChart, Area, ComposedChart, Scatter, Label
} from 'recharts';

// Custom formatter for currency
const formatCurrency = (value) => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(value);
};

// Custom formatter for large numbers
const formatNumber = (value) => {
  return new Intl.NumberFormat('en-US').format(Math.round(value));
};

// Custom formatter for percentages
const formatPercent = (value) => {
  return `${value.toFixed(1)}%`;
};

// Custom tooltip for charts
const CustomTooltip = ({ active, payload, label, valuePrefix, valueSuffix }) => {
  if (active && payload && payload.length) {
    return (
      <div className="bg-white p-3 border border-gray-300 rounded shadow-lg">
        <p className="font-medium text-gray-700">{label}</p>
        {payload.map((entry, index) => (
          <p key={index} style={{ color: entry.color }} className="text-sm">
            {entry.name}: {valuePrefix || ''}{typeof entry.value === 'number' ? entry.value.toLocaleString('en-US', {
              minimumFractionDigits: entry.value % 1 === 0 ? 0 : 2,
              maximumFractionDigits: 2
            }) : entry.value}{valueSuffix || ''}
          </p>
        ))}
      </div>
    );
  }
  return null;
};

const ResultsDashboard = ({ results, location }) => {
  const [activeTab, setActiveTab] = useState('summary');
  
  // If no results provided, show placeholder
  if (!results) {
    return (
      <div className="bg-white p-6 rounded-lg shadow">
        <h2 className="text-xl font-bold mb-6 text-gray-800">Results Dashboard</h2>
        <p className="text-gray-600">No calculation results available. Please select a location and enter system parameters to calculate results.</p>
      </div>
    );
  }
  
  // Extract production data
  const productionData = results.production || {};
  const nrelData = productionData.nrel || {};
  const nasaData = productionData.nasa || {};
  const comparison = productionData.comparison || {};
  
  // Extract financial data
  const financialData = results.financials || {};
  const metrics = financialData.financial_metrics || {};
  const cashFlows = financialData.yearly_cash_flows || [];
  
  // Prepare data for charts
  const monthlyProductionData = [];
  const monthNames = [
    'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
    'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'
  ];
  
  // Format monthly production data if available
  if (nrelData.monthly_production_kwh || nasaData.monthly_production_kwh) {
    for (let i = 0; i < 12; i++) {
      const monthData = {
        month: monthNames[i],
        nrel: nrelData.monthly_production_kwh ? Math.round(nrelData.monthly_production_kwh[i]) : null,
        nasa: nasaData.monthly_production_kwh ? Math.round(nasaData.monthly_production_kwh[i]) : null
      };
      monthlyProductionData.push(monthData);
    }
  }
  
  // Format cash flow data if available
  const cashFlowData = cashFlows.map(year => ({
    year: `Year ${year.year}`,
    savings: Math.round(year.energy_savings || 0),
    costs: Math.round((year.maintenance_cost || 0) + (year.insurance_cost || 0) + (year.inverter_replacement || 0)),
    netCashFlow: Math.round(year.net_cash_flow || 0),
    cumulativeCashFlow: Math.round(year.cumulative_cash_flow || 0)
  }));
  
  // Prepare ROI breakdown data
  const roiBreakdownData = [
    { name: 'Energy Savings', value: Math.round(metrics.total_lifetime_savings || 0) },
    { name: 'SREC Revenue', value: Math.round((metrics.total_lifetime_revenue || 0) - (metrics.total_lifetime_savings || 0)) },
    { name: 'Maintenance', value: Math.round((metrics.total_lifetime_costs || 0) * 0.6) },
    { name: 'Insurance', value: Math.round((metrics.total_lifetime_costs || 0) * 0.3) },
    { name: 'Inverter Replacement', value: Math.round((metrics.total_lifetime_costs || 0) * 0.1) }
  ].filter(item => item.value > 0);
  
  // Prepare production comparison data
  const productionComparisonData = [];
  if (nrelData.annual_production_kwh) {
    productionComparisonData.push({
      name: 'NREL Estimate',
      value: Math.round(nrelData.annual_production_kwh)
    });
  }
  if (nasaData.annual_production_kwh) {
    productionComparisonData.push({
      name: 'NASA Estimate',
      value: Math.round(nasaData.annual_production_kwh)
    });
  }
  if (comparison.average_production_kwh) {
    productionComparisonData.push({
      name: 'Average',
      value: Math.round(comparison.average_production_kwh)
    });
  }
  
  // Helper function to determine payback visualization data
  const getPaybackVisualization = () => {
    const paybackYears = metrics.payback_period_years || 0;
    const analysisYears = cashFlows.length;
    
    // Create data with pre-payback and post-payback years
    return Array.from({ length: analysisYears }, (_, i) => {
      const year = i + 1;
      return {
        year: `Year ${year}`,
        value: year,
        payback: year <= paybackYears ? year : 0,
        postPayback: year > paybackYears ? year : 0
      };
    });
  };
  
  const paybackData = getPaybackVisualization();
  
  // Colors for charts
  const colors = {
    nrel: '#1f77b4',
    nasa: '#ff7f0e',
    average: '#2ca02c',
    savings: '#2ca02c',
    costs: '#d62728',
    netCashFlow: '#1f77b4',
    cumulative: '#9467bd',
    payback: '#ff7f0e',
    postPayback: '#2ca02c'
  };
  
  const RADIAN = Math.PI / 180;
  const renderCustomizedLabel = ({ cx, cy, midAngle, innerRadius, outerRadius, percent, index, name, value }) => {
    const radius = innerRadius + (outerRadius - innerRadius) * 0.5;
    const x = cx + radius * Math.cos(-midAngle * RADIAN);
    const y = cy + radius * Math.sin(-midAngle * RADIAN);
    
    return percent > 0.05 ? (
      <text x={x} y={y} fill="white" textAnchor={x > cx ? 'start' : 'end'} dominantBaseline="central">
        {`${name} (${(percent * 100).toFixed(0)}%)`}
      </text>
    ) : null;
  };
  
  // Key metrics for summary
  const keyMetrics = [
    {
      title: 'Annual Production',
      value: comparison.average_production_kwh 
        ? formatNumber(comparison.average_production_kwh) 
        : (nrelData.annual_production_kwh 
          ? formatNumber(nrelData.annual_production_kwh) 
          : (nasaData.annual_production_kwh 
            ? formatNumber(nasaData.annual_production_kwh) 
            : 'N/A')),
      unit: 'kWh',
      icon: (
        <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
        </svg>
      ),
      color: 'bg-yellow-100 text-yellow-800'
    },
    {
      title: 'Payback Period',
      value: metrics.payback_period_years ? metrics.payback_period_years.toFixed(1) : 'N/A',
      unit: 'Years',
      icon: (
        <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      ),
      color: 'bg-blue-100 text-blue-800'
    },
    {
      title: 'Return on Investment',
      value: metrics.roi_percent ? metrics.roi_percent.toFixed(1) : 'N/A',
      unit: '%',
      icon: (
        <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
        </svg>
      ),
      color: 'bg-green-100 text-green-800'
    },
    {
      title: 'Net Present Value',
      value: metrics.npv ? formatCurrency(metrics.npv) : 'N/A',
      unit: '',
      icon: (
        <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      ),
      color: 'bg-purple-100 text-purple-800'
    }
  ];
  
  return (
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
            disabled={!financialData.financial_metrics}
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
            disabled={!cashFlows.length}
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
            {keyMetrics.map((metric, index) => (
              <div key={index} className={`p-4 rounded-lg ${metric.color}`}>
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    {metric.icon}
                  </div>
                  <div className="ml-4">
                    <h3 className="text-sm font-medium">{metric.title}</h3>
                    <p className="text-2xl font-bold">
                      {metric.value} {metric.unit}
                    </p>
                  </div>
                </div>
              </div>
            ))}
          </div>
          
          {/* Production Summary Chart */}
          <div className="mb-6">
            <h3 className="text-lg font-semibold mb-2 text-gray-700">Production Comparison</h3>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={productionComparisonData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" />
                  <YAxis>
                    <Label value="Annual Production (kWh)" angle={-90} position="insideLeft" style={{ textAnchor: 'middle' }} />
                  </YAxis>
                  <Tooltip content={<CustomTooltip valueSuffix=" kWh" />} />
                  <Legend />
                  <Bar dataKey="value" name="Production" fill="#1f77b4" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
          
          {/* Payback Period Visualization */}
          {metrics.payback_period_years && (
            <div className="mb-6">
              <h3 className="text-lg font-semibold mb-2 text-gray-700">Payback Period</h3>
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={paybackData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="year" />
                    <YAxis />
                    <Tooltip content={<CustomTooltip valueSuffix=" years" />} />
                    <Legend />
                    <Bar dataKey="payback" name="Payback Period" stackId="a" fill={colors.payback} />
                    <Bar dataKey="postPayback" name="Post-Payback Returns" stackId="a" fill={colors.postPayback} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
              <p className="text-gray-600 text-sm mt-2">
                Your investment will pay for itself in approximately {metrics.payback_period_years.toFixed(1)} years. 
                After this point, all returns represent profit on your investment.
              </p>
            </div>
          )}
        </div>
      )}
      
      {/* Production Tab */}
      {activeTab === 'production' && (
        <div>
          {/* Monthly Production Chart */}
          {monthlyProductionData.length > 0 && (
            <div className="mb-6">
              <h3 className="text-lg font-semibold mb-2 text-gray-700">Monthly Production</h3>
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={monthlyProductionData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="month" />
                    <YAxis>
                      <Label value="Energy (kWh)" angle={-90} position="insideLeft" style={{ textAnchor: 'middle' }} />
                    </YAxis>
                    <Tooltip content={<CustomTooltip valueSuffix=" kWh" />} />
                    <Legend />
                    {nrelData.monthly_production_kwh && (
                      <Bar dataKey="nrel" name="NREL Estimate" fill={colors.nrel} />
                    )}
                    {nasaData.monthly_production_kwh && (
                      <Bar dataKey="nasa" name="NASA Estimate" fill={colors.nasa} />
                    )}
                  </BarChart>
                </ResponsiveContainer>
              </div>
              <p className="text-gray-600 text-sm mt-2">
                Monthly production varies throughout the year based on seasonal changes in solar radiation.
                The highest production typically occurs during summer months.
              </p>
            </div>
          )}
          
          {/* Production Data Table */}
          <div className="mb-6">
            <h3 className="text-lg font-semibold mb-2 text-gray-700">Production Data</h3>
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Data Source
                    </th>
                    <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Annual Production
                    </th>
                    <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Production per kW
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {nrelData.annual_production_kwh && (
                    <tr>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                        NREL PVWatts
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {formatNumber(nrelData.annual_production_kwh)} kWh
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {formatNumber(nrelData.production_per_kw)} kWh/kW
                      </td>
                    </tr>
                  )}
                  {nasaData.annual_production_kwh && (
                    <tr>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                        NASA POWER
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {formatNumber(nasaData.annual_production_kwh)} kWh
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {formatNumber(nasaData.production_per_kw)} kWh/kW
                      </td>
                    </tr>
                  )}
                  {comparison.average_production_kwh && (
                    <tr className="bg-blue-50">
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                        Average (Used for Calculations)
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {formatNumber(comparison.average_production_kwh)} kWh
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {comparison.average_production_kwh && productionData.system_parameters 
                          ? formatNumber(comparison.average_production_kwh / productionData.system_parameters.capacity_kw) 
                          : 'N/A'} kWh/kW
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
            {comparison.percent_difference && (
              <p className="text-gray-600 text-sm mt-2">
                The difference between NREL and NASA estimates is {Math.abs(comparison.percent_difference).toFixed(1)}%. 
                NREL estimates tend to be more optimistic than NASA's more conservative approach.
              </p>
            )}
          </div>
        </div>
      )}
      
      {/* Financial Tab */}
      {activeTab === 'financial' && financialData.financial_metrics && (
        <div>
          {/* ROI Breakdown */}
          <div className="mb-6">
            <h3 className="text-lg font-semibold mb-2 text-gray-700">ROI Breakdown</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="bg-gray-50 p-4 rounded">
                <h4 className="font-medium text-gray-700 mb-2">Financial Metrics</h4>
                <table className="min-w-full">
                  <tbody>
                    <tr>
                      <td className="py-1 text-sm text-gray-500">Total System Cost</td>
                      <td className="py-1 text-sm text-gray-900 font-medium">
                        {financialData.costs && formatCurrency(financialData.costs.system_cost)}
                      </td>
                    </tr>
                    <tr>
                      <td className="py-1 text-sm text-gray-500">Net Cost (After Incentives)</td>
                      <td className="py-1 text-sm text-gray-900 font-medium">
                        {financialData.costs && formatCurrency(financialData.costs.net_system_cost)}
                      </td>
                    </tr>
                    <tr>
                      <td className="py-1 text-sm text-gray-500">Lifetime Savings</td>
                      <td className="py-1 text-sm text-gray-900 font-medium">
                        {metrics.total_lifetime_savings && formatCurrency(metrics.total_lifetime_savings)}
                      </td>
                    </tr>
                    <tr>
                      <td className="py-1 text-sm text-gray-500">ROI</td>
                      <td className="py-1 text-sm text-gray-900 font-medium">
                        {metrics.roi_percent && formatPercent(metrics.roi_percent)}
                      </td>
                    </tr>
                    <tr>
                      <td className="py-1 text-sm text-gray-500">IRR</td>
                      <td className="py-1 text-sm text-gray-900 font-medium">
                        {metrics.irr_percent && formatPercent(metrics.irr_percent)}
                      </td>
                    </tr>
                    <tr>
                      <td className="py-1 text-sm text-gray-500">Levelized Cost of Energy</td>
                      <td className="py-1 text-sm text-gray-900 font-medium">
                        {metrics.lcoe_per_kwh && `$${metrics.lcoe_per_kwh.toFixed(3)}/kWh`}
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
              
              {roiBreakdownData.length > 0 && (
                <div className="h-64">
                  <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                      <Pie
                        data={roiBreakdownData}
                        dataKey="value"
                        nameKey="name"
                        cx="50%"
                        cy="50%"
                        outerRadius={80}
                        fill="#8884d8"
                        labelLine={false}
                        label={renderCustomizedLabel}
                      >
                        {roiBreakdownData.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={['#2ca02c', '#98df8a', '#d62728', '#ff9896', '#9467bd'][index % 5]} />
                        ))}
                      </Pie>
                      <Tooltip formatter={(value) => formatCurrency(value)} />
                      <Legend />
                    </PieChart>
                  </ResponsiveContainer>
                </div>
              )}
            </div>
          </div>
          
          {/* Sensitivity Analysis */}
          {financialData.sensitivity_analysis && (
            <div className="mb-6">
              <h3 className="text-lg font-semibold mb-2 text-gray-700">Sensitivity Analysis</h3>
              <p className="text-gray-600 text-sm mb-4">
                How changes in key parameters affect your project's financial outcomes.
              </p>
              
              {/* We can add sensitivity analysis charts here when that data is available */}
            </div>
          )}
        </div>
      )}
      
      {/* Cash Flow Tab */}
      {activeTab === 'cashflow' && cashFlowData.length > 0 && (
        <div>
          {/* Cumulative Cash Flow Chart */}
          <div className="mb-6">
            <h3 className="text-lg font-semibold mb-2 text-gray-700">Cumulative Cash Flow</h3>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <ComposedChart data={cashFlowData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="year" />
                  <YAxis yAxisId="left" orientation="left">
                    <Label value="Cash Flow ($)" angle={-90} position="insideLeft" style={{ textAnchor: 'middle' }} />
                  </YAxis>
                  <Tooltip content={<CustomTooltip valuePrefix="$" />} />
                  <Legend />
                  <Bar dataKey="savings" name="Energy Savings" fill={colors.savings} yAxisId="left" />
                  <Bar dataKey="costs" name="Costs" fill={colors.costs} yAxisId="left" />
                  <Line dataKey="cumulativeCashFlow" name="Cumulative Cash Flow" stroke={colors.cumulative} yAxisId="left" dot={true} />
                </ComposedChart>
              </ResponsiveContainer>
            </div>
            <p className="text-gray-600 text-sm mt-2">
              This chart shows your annual cash flows and cumulative returns over the system lifetime.
              The point where the cumulative line crosses into positive territory represents your payback period.
            </p>
          </div>
          
          {/* Annual Cash Flow Table */}
          <div className="mb-6">
            <h3 className="text-lg font-semibold mb-2 text-gray-700">Annual Cash Flow Details</h3>
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th scope="col" className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Year
                    </th>
                    <th scope="col" className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Energy Savings
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
                                    {cashFlowData.slice(0, 10).map((year, index) => (
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
                                    {cashFlowData.length > 10 && (
                                        <tr>
                                        <td colSpan="5" className="px-4 py-2 text-sm text-center text-gray-500">
                                            Showing first 10 years. Full data available in detailed report.
                                        </td>
                                        </tr>
                                    )}
                                    </tbody>
                                </table>
                                </div>
                            </div>
                            </div>
                        )}
                        </div>
                    );
                    };

                    export default ResultsDashboard;