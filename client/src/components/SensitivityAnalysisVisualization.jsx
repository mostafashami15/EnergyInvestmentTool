import React, { useState, useEffect } from 'react';
import PropTypes from 'prop-types';
import { 
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, 
  ResponsiveContainer, ReferenceLine
} from 'recharts';

/**
 * SensitivityAnalysisVisualization component provides interactive visualization
 * of parameter sensitivity analysis for energy investment decisions.
 */
const SensitivityAnalysisVisualization = ({ 
  sensitivityData, 
  onParameterChange, 
  baselineValues,
  loading = false
}) => {
  const [selectedMetric, setSelectedMetric] = useState('npv');
  const [customParams, setCustomParams] = useState({});
  const [customScenarioResults, setCustomScenarioResults] = useState(null);
  const [activeTab, setActiveTab] = useState('tornado');

  // Parameter definitions with labels, min/max values, and steps
  const parameterDefinitions = {
    system_cost_per_watt: {
      label: 'System Cost ($/W)',
      min: 1.5,
      max: 4.0,
      step: 0.05,
      default: baselineValues?.system_cost_per_watt || 2.8,
      format: value => `$${value.toFixed(2)}/W`
    },
    electricity_rate: {
      label: 'Electricity Rate ($/kWh)',
      min: 0.08,
      max: 0.25,
      step: 0.01,
      default: baselineValues?.electricity_rate || 0.12,
      format: value => `$${value.toFixed(2)}/kWh`
    },
    loan_rate: {
      label: 'Loan Interest Rate (%)',
      min: 2.0,
      max: 10.0,
      step: 0.25,
      default: baselineValues?.loan_rate || 5.5,
      format: value => `${value.toFixed(2)}%`
    },
    incentive_percent: {
      label: 'Incentives (%)',
      min: 0,
      max: 50,
      step: 5,
      default: baselineValues?.incentive_percent || 30,
      format: value => `${value}%`
    },
    electricity_inflation: {
      label: 'Electricity Price Inflation (%)',
      min: 0,
      max: 5,
      step: 0.25,
      default: baselineValues?.electricity_inflation || 2.5,
      format: value => `${value.toFixed(2)}%`
    },
    panel_degradation: {
      label: 'Annual Panel Degradation (%)',
      min: 0.1,
      max: 1.0,
      step: 0.05,
      default: baselineValues?.panel_degradation || 0.5,
      format: value => `${value.toFixed(2)}%`
    }
  };

  // Metric definitions with labels and formatting
  const metricDefinitions = {
    npv: {
      label: 'Net Present Value (NPV)',
      format: value => `$${Math.round(value).toLocaleString()}`,
      description: 'Total value of all cash flows in today\'s dollars'
    },
    roi_percent: {
      label: 'Return on Investment (ROI)',
      format: value => `${value.toFixed(1)}%`,
      description: 'Percentage return on the initial investment'
    },
    payback_period_years: {
      label: 'Payback Period',
      format: value => `${value.toFixed(1)} years`,
      description: 'Time required to recover the cost of investment'
    },
    irr_percent: {
      label: 'Internal Rate of Return (IRR)',
      format: value => `${value.toFixed(1)}%`,
      description: 'Discount rate that makes the NPV zero'
    },
    lcoe_per_kwh: {
      label: 'Levelized Cost of Energy (LCOE)',
      format: value => `$${value.toFixed(3)}/kWh`,
      description: 'Average cost per kWh over the system lifetime'
    },
    lifetime_savings: {
      label: 'Lifetime Savings',
      format: value => `$${Math.round(value).toLocaleString()}`,
      description: 'Total financial savings over the system lifetime'
    }
  };

  // Initialize custom parameters from baseline values
  useEffect(() => {
    if (baselineValues && Object.keys(customParams).length === 0) {
      const initialParams = {};
      Object.keys(parameterDefinitions).forEach(param => {
        if (baselineValues[param] !== undefined) {
          initialParams[param] = baselineValues[param];
        } else {
          initialParams[param] = parameterDefinitions[param].default;
        }
      });
      setCustomParams(initialParams);
    }
  }, [baselineValues]);

  // Handle custom parameter change from sliders
  const handleParameterChange = (param, value) => {
    setCustomParams(prev => ({
      ...prev,
      [param]: value
    }));
  };

  // Calculate custom scenario when user clicks button
  const calculateCustomScenario = () => {
    if (onParameterChange) {
      onParameterChange(customParams);
    }
  };

  // Update custom scenario results when received from parent
  useEffect(() => {
    if (sensitivityData?.customScenario) {
      setCustomScenarioResults(sensitivityData.customScenario);
    }
  }, [sensitivityData]);

  // Prepare tornado chart data
  const prepareTornadoData = () => {
    if (!sensitivityData || !sensitivityData.tornado_data || !sensitivityData.tornado_data[selectedMetric]) {
      return [];
    }

    return sensitivityData.tornado_data[selectedMetric].map(item => {
      // Format parameter name for display
      const paramName = item.parameter
        .split('_')
        .map(word => word.charAt(0).toUpperCase() + word.slice(1))
        .join(' ');

      return {
        parameter: paramName,
        low: item.low,
        high: item.high,
        tooltipContent: `${paramName}
          Low: ${item.min_variation} (${metricDefinitions[selectedMetric]?.format(item.min_value) || item.min_value})
          High: ${item.max_variation} (${metricDefinitions[selectedMetric]?.format(item.max_value) || item.max_value})`
      };
    });
  };

  // Prepare scenario comparison data
  const prepareScenarioData = () => {
    if (!sensitivityData || !sensitivityData.scenarios) {
      return [];
    }

    return sensitivityData.scenarios.map((scenario, index) => {
      const data = {
        name: scenario,
        value: sensitivityData.metrics[selectedMetric][index]
      };

      // Add percent change for tooltip
      if (sensitivityData.percent_changes && sensitivityData.percent_changes[selectedMetric]) {
        data.percentChange = sensitivityData.percent_changes[selectedMetric][index];
      }

      return data;
    });
  };

  // Custom tooltip for tornado chart
  const TornadoTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-white p-4 border border-gray-200 shadow-md rounded">
          <p className="font-bold">{payload[0].payload.parameter}</p>
          {payload[0].payload.tooltipContent.split('\n').map((line, i) => (
            <p key={i} className="text-sm">{line}</p>
          ))}
        </div>
      );
    }
    return null;
  };

  // Custom tooltip for scenario comparison
  const ScenarioTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      return (
        <div className="bg-white p-4 border border-gray-200 shadow-md rounded">
          <p className="font-bold">{data.name}</p>
          <p>
            {metricDefinitions[selectedMetric]?.label}: {' '}
            {metricDefinitions[selectedMetric]?.format(data.value)}
          </p>
          {data.percentChange !== undefined && (
            <p className="text-sm">
              {data.percentChange > 0 ? '+' : ''}{data.percentChange?.toFixed(1)}% vs. Base Case
            </p>
          )}
        </div>
      );
    }
    return null;
  };

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h2 className="text-2xl font-bold mb-4">Sensitivity Analysis</h2>
      
      {/* Tabs */}
      <div className="flex border-b mb-6">
        <button
          className={`py-2 px-4 mr-2 ${activeTab === 'tornado' 
            ? 'border-b-2 border-blue-500 font-semibold text-blue-600' 
            : 'text-gray-500 hover:text-gray-700'}`}
          onClick={() => setActiveTab('tornado')}
        >
          Parameter Impact
        </button>
        <button
          className={`py-2 px-4 mr-2 ${activeTab === 'scenarios' 
            ? 'border-b-2 border-blue-500 font-semibold text-blue-600' 
            : 'text-gray-500 hover:text-gray-700'}`}
          onClick={() => setActiveTab('scenarios')}
        >
          Scenario Comparison
        </button>
        <button
          className={`py-2 px-4 ${activeTab === 'custom' 
            ? 'border-b-2 border-blue-500 font-semibold text-blue-600' 
            : 'text-gray-500 hover:text-gray-700'}`}
          onClick={() => setActiveTab('custom')}
        >
          Custom Scenario
        </button>
      </div>
      
      {/* Metric selector */}
      <div className="mb-6">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Select Financial Metric
        </label>
        <select
          className="block w-full py-2 px-3 border border-gray-300 bg-white rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
          value={selectedMetric}
          onChange={e => setSelectedMetric(e.target.value)}
        >
          {Object.entries(metricDefinitions).map(([key, { label }]) => (
            <option key={key} value={key}>{label}</option>
          ))}
        </select>
        <p className="mt-2 text-sm text-gray-500">
          {metricDefinitions[selectedMetric]?.description}
        </p>
      </div>
      
      {/* Loading indicator */}
      {loading && (
        <div className="flex justify-center items-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
        </div>
      )}
      
      {!loading && (
        <>
          {/* Tornado Chart View */}
          {activeTab === 'tornado' && (
            <>
              <div className="bg-gray-50 rounded p-4 mb-6">
                <p className="text-sm text-gray-700">
                  This chart shows how changes in each parameter affect the selected financial metric.
                  Longer bars indicate parameters with greater impact on your investment decision.
                </p>
              </div>
              <div className="h-96">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart
                    data={prepareTornadoData()}
                    layout="vertical"
                    margin={{ top: 20, right: 30, left: 150, bottom: 5 }}
                  >
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis 
                      type="number" 
                      domain={['dataMin', 'dataMax']} 
                      tickFormatter={value => `${value > 0 ? '+' : ''}${value.toFixed(1)}%`} 
                    />
                    <YAxis dataKey="parameter" type="category" width={150} />
                    <Tooltip content={<TornadoTooltip />} />
                    <Legend />
                    <ReferenceLine x={0} stroke="#000" />
                    <Bar dataKey="low" name="Decrease" fill="#ef4444" />
                    <Bar dataKey="high" name="Increase" fill="#22c55e" />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </>
          )}
          
          {/* Scenario Comparison View */}
          {activeTab === 'scenarios' && (
            <>
              <div className="bg-gray-50 rounded p-4 mb-6">
                <p className="text-sm text-gray-700">
                  Compare how different scenarios affect your selected financial metric.
                  Scenarios represent different combinations of parameter values.
                </p>
              </div>
              <div className="h-96">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart
                    data={prepareScenarioData()}
                    margin={{ top: 20, right: 30, left: 20, bottom: 70 }}
                  >
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis 
                      dataKey="name" 
                      angle={-45} 
                      textAnchor="end" 
                      height={70} 
                    />
                    <YAxis 
                      label={{ 
                        value: metricDefinitions[selectedMetric]?.label, 
                        angle: -90, 
                        position: 'insideLeft' 
                      }} 
                    />
                    <Tooltip content={<ScenarioTooltip />} />
                    <Bar 
                      dataKey="value" 
                      name={metricDefinitions[selectedMetric]?.label} 
                      fill="#3b82f6" 
                    />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </>
          )}
          
          {/* Custom Scenario View */}
          {activeTab === 'custom' && (
            <>
              <div className="bg-gray-50 rounded p-4 mb-6">
                <p className="text-sm text-gray-700">
                  Adjust parameters using the sliders below to create a custom scenario.
                  Click "Calculate" to see how your changes affect the financial metrics.
                </p>
              </div>
              
              {/* Parameter sliders */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
                {Object.entries(parameterDefinitions).map(([param, def]) => (
                  <div key={param} className="mb-4">
                    <div className="flex justify-between items-center mb-2">
                      <label className="block text-sm font-medium text-gray-700">
                        {def.label}
                      </label>
                      <span className="text-sm text-gray-600 font-medium">
                        {def.format(customParams[param] || def.default)}
                      </span>
                    </div>
                    <input
                      type="range"
                      min={def.min}
                      max={def.max}
                      step={def.step}
                      value={customParams[param] || def.default}
                      onChange={e => handleParameterChange(param, parseFloat(e.target.value))}
                      className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
                    />
                    <div className="flex justify-between text-xs text-gray-500 mt-1">
                      <span>{def.format(def.min)}</span>
                      <span>{def.format(def.max)}</span>
                    </div>
                  </div>
                ))}
              </div>
              
              {/* Calculate button */}
              <div className="flex justify-center mb-6">
                <button
                  onClick={calculateCustomScenario}
                  className="px-6 py-2 bg-blue-600 text-white font-medium rounded hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-opacity-50"
                  disabled={loading}
                >
                  {loading ? 'Calculating...' : 'Calculate Results'}
                </button>
              </div>
              
              {/* Results display */}
              {customScenarioResults && (
                <div className="mt-6">
                  <h3 className="text-lg font-semibold mb-3">Custom Scenario Results</h3>
                  <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4">
                    {Object.entries(metricDefinitions).map(([key, { label, format }]) => {
                      const value = customScenarioResults[key];
                      const baseValue = sensitivityData?.base_case?.[key];
                      const percentChange = baseValue ? 
                        ((value - baseValue) / Math.abs(baseValue)) * 100 : 
                        null;
                      
                      // Determine if this metric is better when higher or lower
                      const isHigherBetter = !['payback_period_years', 'lcoe_per_kwh'].includes(key);
                      const isPositiveChange = percentChange > 0;
                      const isPositiveImpact = (isHigherBetter && isPositiveChange) || 
                                              (!isHigherBetter && !isPositiveChange);
                      
                      return (
                        <div 
                          key={key} 
                          className="bg-gray-50 p-4 rounded border"
                        >
                          <p className="text-sm text-gray-600">{label}</p>
                          <p className="text-xl font-bold">
                            {value !== undefined && value !== null ? format(value) : 'N/A'}
                          </p>
                          {percentChange !== null && (
                            <p className={`text-sm ${isPositiveImpact ? 'text-green-600' : 'text-red-600'}`}>
                              {percentChange > 0 ? '+' : ''}{percentChange.toFixed(1)}% vs. Base Case
                            </p>
                          )}
                        </div>
                      );
                    })}
                  </div>
                </div>
              )}
            </>
          )}
        </>
      )}
    </div>
  );
};

SensitivityAnalysisVisualization.propTypes = {
  sensitivityData: PropTypes.object,
  onParameterChange: PropTypes.func,
  baselineValues: PropTypes.object,
  loading: PropTypes.bool
};

export default SensitivityAnalysisVisualization;