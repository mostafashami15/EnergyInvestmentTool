import React, { useState, useEffect } from 'react';
import SolarMapComponent from './SolarMapComponent';
import SystemParameterForm from './SystemParameterForm';
import ResultsDashboard from './ResultsDashboard';

const EnergyInvestmentApp = () => {
  // Application state
  const [location, setLocation] = useState({ lat: 39.7392, lon: -104.9903 }); // Default: Denver
  const [calculationResults, setCalculationResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Mock API call to fetch solar and financial data
  const fetchCalculations = async (parameters) => {
    setLoading(true);
    setError(null);
    
    try {
      // In a real implementation, this would be an API call
      // For demonstration, we'll simulate an API response with timeout
      await new Promise(resolve => setTimeout(resolve, 1500));
      
      // Mock calculation response
      const mockResponse = generateMockResponse(location, parameters);
      setCalculationResults(mockResponse);
    } catch (err) {
      console.error('Calculation error:', err);
      setError('Failed to calculate results. Please try again.');
    } finally {
      setLoading(false);
    }
  };
  
  // Generate mock response data for demonstration purposes
  const generateMockResponse = (location, params) => {
    // Create a deterministic "random" value based on location
    const locationSeed = location.lat + location.lon;
    const randomFactor = (Math.sin(locationSeed) + 1) / 2; // 0-1 range
    
    // Calculate solar radiation based on latitude and random factor
    // Higher values near equator, lower near poles
    const latitudeFactor = 1 - Math.abs(location.lat) / 90;
    const baseGHI = 3.5 + 3.0 * latitudeFactor;
    const ghi = baseGHI * (0.9 + 0.2 * randomFactor);
    
    // Annual production depends on system size and solar radiation
    const nrelProduction = params.systemCapacity * 1600 * (ghi / 5.0);
    const nasaProduction = nrelProduction * (0.75 + 0.1 * randomFactor);
    
    // Generate monthly data (higher in summer, lower in winter)
    const nrelMonthly = [];
    const nasaMonthly = [];
    
    for (let i = 0; i < 12; i++) {
      // Northern hemisphere seasonal pattern (adjust for southern hemisphere if needed)
      const monthFactor = Math.sin((i + 3) * Math.PI / 6);
      const seasonalFactor = 0.5 + 0.5 * monthFactor;
      
      nrelMonthly.push(nrelProduction / 12 * seasonalFactor * 1.5);
      nasaMonthly.push(nasaProduction / 12 * seasonalFactor * 1.5);
    }
    
    // Calculate financial metrics
    const systemCost = params.systemCapacity * params.systemCostPerWatt * 1000;
    const incentiveAmount = systemCost * (params.incentivePercent / 100);
    const netSystemCost = systemCost - incentiveAmount;
    
    // Utility rate varies by location (mock data)
    const utilityRate = 0.10 + 0.05 * randomFactor;
    
    // Annual energy savings
    const averageProduction = (nrelProduction + nasaProduction) / 2;
    const annualSavings = averageProduction * utilityRate;
    
    // Simple payback calculation
    const rawPayback = netSystemCost / annualSavings;
    const paybackPeriod = Math.max(0.1, Math.min(params.analysisYears, rawPayback));
    
    // ROI calculation
    const totalSavings = annualSavings * params.analysisYears;
    const maintenanceCosts = params.systemCapacity * 20 * params.analysisYears; // $20/kW/year
    const netSavings = totalSavings - maintenanceCosts;
    const roi = (netSavings / netSystemCost) * 100;
    
    // Generate yearly cash flows
    const yearlyFlows = [];
    let cumulativeCashFlow = -netSystemCost;
    
    for (let year = 1; year <= params.analysisYears; year++) {
      const electricityInflation = 1 + (0.025 * year);
      const yearProduction = averageProduction * Math.pow(0.995, year - 1); // 0.5% degradation per year
      const yearSavings = yearProduction * utilityRate * electricityInflation;
      const yearMaintenance = params.systemCapacity * 20 * (1 + 0.02 * (year - 1)); // 2% inflation
      const yearInverterReplacement = year === 15 ? params.systemCapacity * 300 : 0; // $300/kW at year 15
      
      const yearNetCashFlow = yearSavings - yearMaintenance - yearInverterReplacement;
      cumulativeCashFlow += yearNetCashFlow;
      
      yearlyFlows.push({
        year,
        energy_savings: yearSavings,
        maintenance_cost: yearMaintenance,
        inverter_replacement: yearInverterReplacement,
        net_cash_flow: yearNetCashFlow,
        cumulative_cash_flow: cumulativeCashFlow
      });
    }
    
    return {
      production: {
        location: {
          lat: location.lat,
          lon: location.lon
        },
        system_parameters: {
          capacity_kw: params.systemCapacity,
          module_type: params.moduleType,
          losses_percent: params.losses,
          array_type: params.arrayType,
          tilt_degrees: params.tilt,
          azimuth_degrees: params.azimuth
        },
        nrel: {
          annual_production_kwh: nrelProduction,
          monthly_production_kwh: nrelMonthly,
          capacity_factor_percent: (nrelProduction / (params.systemCapacity * 8760)) * 100,
          production_per_kw: nrelProduction / params.systemCapacity
        },
        nasa: {
          annual_production_kwh: nasaProduction,
          monthly_production_kwh: nasaMonthly,
          production_per_kw: nasaProduction / params.systemCapacity
        },
        comparison: {
          absolute_difference_kwh: nrelProduction - nasaProduction,
          percent_difference: ((nrelProduction - nasaProduction) / nasaProduction) * 100,
          average_production_kwh: (nrelProduction + nasaProduction) / 2,
          conservative_estimate_kwh: Math.min(nrelProduction, nasaProduction),
          optimistic_estimate_kwh: Math.max(nrelProduction, nasaProduction)
        }
      },
      financials: {
        system_details: {
          capacity_kw: params.systemCapacity,
          annual_production_kwh: (nrelProduction + nasaProduction) / 2,
          electricity_rate_per_kwh: utilityRate
        },
        costs: {
          system_cost: systemCost,
          cost_per_watt: params.systemCostPerWatt,
          incentives: {
            federal_itc: incentiveAmount,
            state_incentive: 0,
            utility_rebate: 0,
            total_incentives: incentiveAmount
          },
          net_system_cost: netSystemCost,
          annual_maintenance_initial: params.systemCapacity * 20
        },
        financial_metrics: {
          payback_period_years: paybackPeriod,
          roi_percent: roi,
          npv: netSavings - netSystemCost,
          irr_percent: 8.5 + 2 * randomFactor, // Mock IRR value
          lcoe_per_kwh: netSystemCost / (averageProduction * params.analysisYears),
          first_year_savings: annualSavings,
          total_lifetime_savings: totalSavings,
          total_lifetime_revenue: totalSavings,
          total_lifetime_costs: maintenanceCosts
        },
        yearly_cash_flows: yearlyFlows
      }
    };
  };

  // Handle location selection from map
  const handleLocationSelect = (newLocation) => {
    setLocation(newLocation);
    // Clear previous calculation results when location changes
    setCalculationResults(null);
  };
  
  // Handle form submission
  const handleCalculate = (formValues) => {
    fetchCalculations(formValues);
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <header className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Energy Investment Decision Support System</h1>
        <p className="text-gray-600 mt-2">
          Analyze renewable energy potential and financial returns for any location
        </p>
      </header>
      
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Left column: Map */}
        <div className="lg:col-span-2">
          <SolarMapComponent 
            onLocationSelect={handleLocationSelect} 
            initialLocation={location} 
          />
        </div>
        
        {/* Right column: Parameters form */}
        <div>
          <SystemParameterForm 
            onCalculate={handleCalculate} 
            loading={loading} 
          />
        </div>
        
        {/* Full width: Results dashboard */}
        <div className="lg:col-span-3 mt-8">
          {error && (
            <div className="bg-red-50 border-l-4 border-red-500 p-4 mb-6">
              <div className="flex">
                <div className="flex-shrink-0">
                  <svg className="h-5 w-5 text-red-500" viewBox="0 0 20 20" fill="currentColor">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                  </svg>
                </div>
                <div className="ml-3">
                  <p className="text-sm text-red-700">{error}</p>
                </div>
              </div>
            </div>
          )}
          
          {loading && (
            <div className="flex justify-center items-center p-12">
              <div className="animate-spin rounded-full h-16 w-16 border-t-2 border-b-2 border-blue-500"></div>
              <span className="ml-4 text-lg font-medium text-gray-700">Calculating results...</span>
            </div>
          )}
          
          {!loading && calculationResults && (
            <ResultsDashboard results={calculationResults} location={location} />
          )}
          
          {!loading && !calculationResults && !error && (
            <div className="bg-blue-50 border-l-4 border-blue-500 p-4">
              <div className="flex">
                <div className="flex-shrink-0">
                  <svg className="h-5 w-5 text-blue-500" viewBox="0 0 20 20" fill="currentColor">
                    <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2h-1V9z" clipRule="evenodd" />
                  </svg>
                </div>
                <div className="ml-3">
                  <p className="text-sm text-blue-700">
                    Select a location on the map and enter system parameters, then click "Calculate Results" to analyze renewable energy potential.
                  </p>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
      
      <footer className="mt-16 pt-8 border-t border-gray-200 text-center text-gray-500 text-sm">
        <p>Energy Investment Decision Support System &copy; {new Date().getFullYear()}</p>
        <p className="mt-1">Powered by NREL and NASA POWER APIs</p>
      </footer>
    </div>
  );
};

export default EnergyInvestmentApp;