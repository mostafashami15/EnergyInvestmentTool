import React, { useState, useEffect } from 'react';

const SystemParameterForm = ({ onCalculate, initialValues, loading }) => {
  // Default values
  const defaultValues = {
    systemCapacity: 10,
    moduleType: 1,
    arrayType: 2,
    tilt: 20,
    azimuth: 180,
    losses: 14,
    systemCostPerWatt: 2.80,
    incentivePercent: 30,
    dataSource: 'both',
    includeFinancials: true,
    loanPercent: 70,
    loanTerm: 20,
    loanRate: 5.5,
    analysisYears: 25,
  };

  // Merge provided initial values with defaults
  const mergedInitialValues = { ...defaultValues, ...initialValues };
  
  // State for form values
  const [formValues, setFormValues] = useState(mergedInitialValues);
  
  // Update state when initialValues prop changes
  useEffect(() => {
    if (initialValues) {
      setFormValues({ ...formValues, ...initialValues });
    }
  }, [initialValues]);

  // Handle form input changes
  const handleInputChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormValues({
      ...formValues,
      [name]: type === 'checkbox' ? checked : type === 'number' ? parseFloat(value) : value,
    });
  };

  // Handle form submission
  const handleSubmit = (e) => {
    e.preventDefault();
    if (onCalculate) {
      onCalculate(formValues);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="bg-white p-4 rounded-lg shadow">
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
              value={formValues.systemCapacity}
              onChange={handleInputChange}
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
              value={formValues.moduleType}
              onChange={handleInputChange}
              className="w-full p-2 border border-gray-300 rounded focus:ring-blue-500 focus:border-blue-500"
            >
              <option value={1}>Standard (15% efficient)</option>
              <option value={2}>Premium (19% efficient)</option>
              <option value={3}>Thin Film (10% efficient)</option>
            </select>
          </div>
          
          <div>
            <label htmlFor="arrayType" className="block text-sm font-medium text-gray-700 mb-1">
              Array Type
            </label>
            <select
              id="arrayType"
              name="arrayType"
              value={formValues.arrayType}
              onChange={handleInputChange}
              className="w-full p-2 border border-gray-300 rounded focus:ring-blue-500 focus:border-blue-500"
            >
              <option value={1}>Fixed - Open Rack</option>
              <option value={2}>Fixed - Roof Mounted</option>
              <option value={3}>1-Axis Tracking</option>
              <option value={4}>1-Axis Backtracking</option>
              <option value={5}>2-Axis Tracking</option>
            </select>
          </div>
          
          <div>
            <label htmlFor="losses" className="block text-sm font-medium text-gray-700 mb-1">
              System Losses (%)
            </label>
            <input
              type="number"
              id="losses"
              name="losses"
              min="0"
              max="99"
              step="0.1"
              value={formValues.losses}
              onChange={handleInputChange}
              className="w-full p-2 border border-gray-300 rounded focus:ring-blue-500 focus:border-blue-500"
            />
            <p className="text-xs text-gray-500 mt-1">
              Includes soiling, shading, wiring, etc.
            </p>
          </div>
        </div>
      </div>
      
      {/* Array Orientation */}
      <div className="mb-4">
        <h3 className="text-lg font-semibold mb-2 text-gray-700">Array Orientation</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label htmlFor="tilt" className="block text-sm font-medium text-gray-700 mb-1">
              Tilt (degrees)
            </label>
            <input
              type="number"
              id="tilt"
              name="tilt"
              min="0"
              max="90"
              step="1"
              value={formValues.tilt}
              onChange={handleInputChange}
              className="w-full p-2 border border-gray-300 rounded focus:ring-blue-500 focus:border-blue-500"
            />
            <p className="text-xs text-gray-500 mt-1">
              0° = horizontal, 90° = vertical
            </p>
          </div>
          
          <div>
            <label htmlFor="azimuth" className="block text-sm font-medium text-gray-700 mb-1">
              Azimuth (degrees)
            </label>
            <input
              type="number"
              id="azimuth"
              name="azimuth"
              min="0"
              max="359"
              step="1"
              value={formValues.azimuth}
              onChange={handleInputChange}
              className="w-full p-2 border border-gray-300 rounded focus:ring-blue-500 focus:border-blue-500"
            />
            <p className="text-xs text-gray-500 mt-1">
              180° = south, 90° = east, 270° = west
            </p>
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
              value={formValues.systemCostPerWatt}
              onChange={handleInputChange}
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
              value={formValues.incentivePercent}
              onChange={handleInputChange}
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
              value={formValues.loanPercent}
              onChange={handleInputChange}
              className="w-full p-2 border border-gray-300 rounded focus:ring-blue-500 focus:border-blue-500"
            />
            <p className="text-xs text-gray-500 mt-1">
              0% = cash purchase
            </p>
          </div>
          
          <div className="grid grid-cols-2 gap-2">
            <div>
              <label htmlFor="loanTerm" className="block text-sm font-medium text-gray-700 mb-1">
                Loan Term (years)
              </label>
              <input
                type="number"
                id="loanTerm"
                name="loanTerm"
                min="1"
                max="30"
                step="1"
                value={formValues.loanTerm}
                onChange={handleInputChange}
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
                value={formValues.loanRate}
                onChange={handleInputChange}
                className="w-full p-2 border border-gray-300 rounded focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
          </div>
          
          <div>
            <label htmlFor="analysisYears" className="block text-sm font-medium text-gray-700 mb-1">
              Analysis Period (years)
            </label>
            <input
              type="number"
              id="analysisYears"
              name="analysisYears"
              min="1"
              max="40"
              step="1"
              value={formValues.analysisYears}
              onChange={handleInputChange}
              className="w-full p-2 border border-gray-300 rounded focus:ring-blue-500 focus:border-blue-500"
            />
          </div>
        </div>
      </div>
      
      {/* Data Source Options */}
      <div className="mb-4">
        <h3 className="text-lg font-semibold mb-2 text-gray-700">Data Source Options</h3>
        <div className="grid grid-cols-1 gap-4">
          <div>
            <label htmlFor="dataSource" className="block text-sm font-medium text-gray-700 mb-1">
              Data Source
            </label>
            <select
              id="dataSource"
              name="dataSource"
              value={formValues.dataSource}
              onChange={handleInputChange}
              className="w-full p-2 border border-gray-300 rounded focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="nrel">NREL (US-focused, optimistic)</option>
              <option value="nasa">NASA (Global, conservative)</option>
              <option value="both">Both (compare results)</option>
            </select>
          </div>
          
          <div className="flex items-center mt-2">
            <input
              type="checkbox"
              id="includeFinancials"
              name="includeFinancials"
              checked={formValues.includeFinancials}
              onChange={handleInputChange}
              className="h-4 w-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
            />
            <label htmlFor="includeFinancials" className="ml-2 block text-sm text-gray-700">
              Include detailed financial analysis
            </label>
          </div>
        </div>
      </div>
      
      <div className="mt-6">
        <button
          type="submit"
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
  );
};

export default SystemParameterForm;