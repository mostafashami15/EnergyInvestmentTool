# server/src/sensitivity_analyzer.py
"""
Sensitivity Analysis module for the Energy Investment Decision Support System.

This module provides functionality to analyze how changes in key parameters
affect financial outcomes for renewable energy investments. It supports:
- Parameter variation analysis for individual factors
- Multi-parameter scenario comparison
- Data generation for tornado charts and other visualizations
"""
from typing import Dict, List, Tuple, Any, Optional, Union
import numpy as np
import copy
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import calculation modules (adjust import paths as needed based on your project structure)
from calculation_engine import CalculationEngine
from financial_modeling import FinancialModel

class SensitivityAnalyzer:
    """Class for performing sensitivity analysis on energy investment calculations."""
    
    def __init__(self, calculation_engine: Optional[CalculationEngine] = None, 
                financial_model: Optional[FinancialModel] = None):
        """Initialize the sensitivity analyzer with calculation engines.
        
        Args:
            calculation_engine: Instance of CalculationEngine for production calculations
            financial_model: Instance of FinancialModel for financial calculations
        """
        self.calculation_engine = calculation_engine or CalculationEngine()
        self.financial_model = financial_model or FinancialModel()
        
        # Default parameter ranges for sensitivity analysis
        self.default_ranges = {
            "system_cost_per_watt": [-20, -10, 0, 10, 20],  # Percentage change
            "electricity_rate": [-20, -10, 0, 10, 20],  # Percentage change
            "annual_production": [-20, -10, 0, 10, 20],  # Percentage change
            "electricity_inflation": [-2, -1, 0, 1, 2],  # Absolute change (percentage points)
            "panel_degradation": [-0.2, -0.1, 0, 0.1, 0.2],  # Absolute change (percentage points)
            "discount_rate": [-2, -1, 0, 1, 2],  # Absolute change (percentage points)
            "loan_rate": [-2, -1, 0, 1, 2],  # Absolute change (percentage points)
        }
        
        # Default metrics to evaluate for each parameter variation
        self.default_metrics = [
            "payback_period_years",
            "roi_percent", 
            "npv", 
            "irr_percent", 
            "lcoe_per_kwh",
            "lifetime_savings"
        ]
    
    def analyze_parameter_sensitivity(self, 
                                     base_params: Dict[str, Any],
                                     parameter_name: str,
                                     variation_range: Optional[List[float]] = None,
                                     metrics: Optional[List[str]] = None) -> Dict[str, Any]:
        """Analyze how changes in a single parameter affect financial outcomes.
        
        Args:
            base_params: Dictionary of base parameters for the calculation
            parameter_name: Name of parameter to vary
            variation_range: List of variation values (% for relative, absolute for absolute)
            metrics: List of metrics to calculate for each variation
            
        Returns:
            Dictionary with sensitivity analysis results
        """
        # Use default range if not specified
        if variation_range is None:
            variation_range = self.default_ranges.get(parameter_name, [-20, -10, 0, 10, 20])
        
        # Use default metrics if not specified
        if metrics is None:
            metrics = self.default_metrics
            
        results = {
            "parameter": parameter_name,
            "base_value": base_params.get(parameter_name),
            "variation_values": [],
            "metrics": {metric: [] for metric in metrics}
        }
        
        # Determine if parameter uses relative or absolute variations
        is_relative = parameter_name in ["system_cost_per_watt", "electricity_rate", "annual_production"]
        
        for variation in variation_range:
            # Create copy of base parameters for this variation
            params = copy.deepcopy(base_params)
            
            # Calculate new parameter value based on variation
            if is_relative:
                # Relative change (percentage)
                base_value = params[parameter_name]
                new_value = base_value * (1 + variation/100)
                params[parameter_name] = new_value
                results["variation_values"].append(f"{variation:+}%")
            else:
                # Absolute change (percentage points)
                base_value = params[parameter_name]
                new_value = base_value + variation
                params[parameter_name] = new_value
                results["variation_values"].append(f"{variation:+}")
            
            # Calculate financial metrics with this parameter variation
            try:
                financial_data = self.calculate_financial_metrics(params)
                
                # Extract and store the requested metrics
                for metric in metrics:
                    metric_value = self._extract_metric(financial_data, metric)
                    results["metrics"][metric].append(metric_value)
            except Exception as e:
                # If calculation fails, store None for all metrics
                for metric in metrics:
                    results["metrics"][metric].append(None)
                print(f"Error calculating variation {variation} for {parameter_name}: {str(e)}")
        
        # Calculate percentage change from baseline for each metric
        results["percent_changes"] = {}
        for metric in metrics:
            baseline_idx = variation_range.index(0) if 0 in variation_range else len(variation_range) // 2
            baseline_value = results["metrics"][metric][baseline_idx]
            
            if baseline_value is not None and baseline_value != 0:
                percent_changes = []
                for value in results["metrics"][metric]:
                    if value is not None:
                        percent_change = ((value - baseline_value) / abs(baseline_value)) * 100
                        percent_changes.append(percent_change)
                    else:
                        percent_changes.append(None)
                results["percent_changes"][metric] = percent_changes
            else:
                results["percent_changes"][metric] = [None] * len(variation_range)
        
        return results
    
    def analyze_multiple_parameters(self, 
                                   base_params: Dict[str, Any],
                                   parameters: Optional[List[str]] = None,
                                   metrics: Optional[List[str]] = None) -> Dict[str, Any]:
        """Analyze sensitivity for multiple parameters to generate tornado chart data.
        
        Args:
            base_params: Dictionary of base parameters for the calculation
            parameters: List of parameters to analyze (default: all standard parameters)
            metrics: List of metrics to calculate for each parameter
            
        Returns:
            Dictionary with tornado chart data for each metric
        """
        # Use default parameters if not specified
        if parameters is None:
            parameters = list(self.default_ranges.keys())
            
        # Use default metrics if not specified
        if metrics is None:
            metrics = self.default_metrics
            
        results = {
            "base_case": {},
            "parameters": parameters,
            "tornado_data": {metric: [] for metric in metrics}
        }
        
        # Calculate baseline metrics
        try:
            baseline_financials = self.calculate_financial_metrics(base_params)
            
            # Extract baseline values for each metric
            for metric in metrics:
                baseline_value = self._extract_metric(baseline_financials, metric)
                results["base_case"][metric] = baseline_value
        except Exception as e:
            print(f"Error calculating baseline metrics: {str(e)}")
            for metric in metrics:
                results["base_case"][metric] = None
        
        # Analyze each parameter
        for parameter in parameters:
            # Get appropriate range for this parameter
            variation_range = self.default_ranges.get(parameter, [-20, -10, 0, 10, 20])
            
            # We only need the min and max variations for tornado chart
            min_variation = min(variation_range)
            max_variation = max(variation_range)
            
            # Create a copy of base parameters
            min_params = copy.deepcopy(base_params)
            max_params = copy.deepcopy(base_params)
            
            # Apply min and max variations
            is_relative = parameter in ["system_cost_per_watt", "electricity_rate", "annual_production"]
            
            if is_relative:
                # Relative change (percentage)
                base_value = base_params[parameter]
                min_params[parameter] = base_value * (1 + min_variation/100)
                max_params[parameter] = base_value * (1 + max_variation/100)
            else:
                # Absolute change (percentage points)
                base_value = base_params[parameter]
                min_params[parameter] = base_value + min_variation
                max_params[parameter] = base_value + max_variation
            
            # Calculate metrics for min and max variations
            try:
                min_financials = self.calculate_financial_metrics(min_params)
                max_financials = self.calculate_financial_metrics(max_params)
                
                # Extract metrics and calculate percentage change from baseline
                for metric in metrics:
                    baseline_value = results["base_case"][metric]
                    
                    if baseline_value is not None and baseline_value != 0:
                        min_value = self._extract_metric(min_financials, metric)
                        max_value = self._extract_metric(max_financials, metric)
                        
                        min_change = ((min_value - baseline_value) / abs(baseline_value)) * 100 if min_value is not None else None
                        max_change = ((max_value - baseline_value) / abs(baseline_value)) * 100 if max_value is not None else None
                        
                        # Sort min and max for consistent tornado chart display
                        # For metrics where lower is better (like payback period), we invert the ordering
                        invert = metric in ["payback_period_years", "lcoe_per_kwh"]
                        
                        if invert:
                            low_value = max_change if (min_change is None or (max_change is not None and max_change < min_change)) else min_change
                            high_value = min_change if (max_change is None or (min_change is not None and min_change > max_change)) else max_change
                        else:
                            low_value = min_change if (max_change is None or (min_change is not None and min_change < max_change)) else max_change
                            high_value = max_change if (min_change is None or (max_change is not None and max_change > min_change)) else min_change
                        
                        results["tornado_data"][metric].append({
                            "parameter": parameter,
                            "low": low_value,
                            "high": high_value,
                            "min_value": min_value,
                            "max_value": max_value,
                            "min_variation": f"{min_variation:+}{'%' if is_relative else ''}",
                            "max_variation": f"{max_variation:+}{'%' if is_relative else ''}"
                        })
                    else:
                        # Skip parameters where baseline is zero or None
                        pass
            except Exception as e:
                print(f"Error calculating variations for parameter {parameter}: {str(e)}")
                # Still include entry for this parameter, but with None values
                for metric in metrics:
                    results["tornado_data"][metric].append({
                        "parameter": parameter,
                        "low": None,
                        "high": None,
                        "min_value": None,
                        "max_value": None,
                        "min_variation": f"{min_variation:+}{'%' if is_relative else ''}",
                        "max_variation": f"{max_variation:+}{'%' if is_relative else ''}"
                    })
        
        # Sort tornado data for each metric by impact magnitude
        for metric in metrics:
            # Calculate magnitude (absolute difference between low and high)
            for item in results["tornado_data"][metric]:
                if item["low"] is not None and item["high"] is not None:
                    item["magnitude"] = abs(item["high"] - item["low"])
                else:
                    item["magnitude"] = 0
            
            # Sort by magnitude descending
            results["tornado_data"][metric] = sorted(
                results["tornado_data"][metric], 
                key=lambda x: x.get("magnitude", 0), 
                reverse=True
            )
            
            # Remove magnitude after sorting
            for item in results["tornado_data"][metric]:
                if "magnitude" in item:
                    del item["magnitude"]
        
        return results
    
    def compare_scenarios(self, 
                         base_params: Dict[str, Any],
                         scenario_params: Dict[str, Dict[str, Any]],
                         metrics: Optional[List[str]] = None) -> Dict[str, Any]:
        """Compare multiple scenarios with different parameter sets.
        
        Args:
            base_params: Dictionary of base parameters for the calculation
            scenario_params: Dictionary of scenario names and their parameter adjustments
            metrics: List of metrics to calculate for each scenario
            
        Returns:
            Dictionary with scenario comparison results
        """
        # Use default metrics if not specified
        if metrics is None:
            metrics = self.default_metrics
            
        results = {
            "scenarios": list(scenario_params.keys()) + ["base_case"],
            "metrics": {metric: [] for metric in metrics},
            "parameters": {}
        }
        
        # Calculate metrics for base case
        try:
            base_financials = self.calculate_financial_metrics(base_params)
            
            # Store base metrics
            for metric in metrics:
                base_value = self._extract_metric(base_financials, metric)
                results["metrics"][metric].append(base_value)
                
            # Store base parameters
            for param, value in base_params.items():
                if param not in results["parameters"]:
                    results["parameters"][param] = []
                results["parameters"][param].append(value)
        except Exception as e:
            print(f"Error calculating base case metrics: {str(e)}")
            for metric in metrics:
                results["metrics"][metric].append(None)
        
        # Calculate metrics for each scenario
        for scenario_name, param_adjustments in scenario_params.items():
            # Create a copy of base parameters and apply scenario adjustments
            scenario_params = copy.deepcopy(base_params)
            scenario_params.update(param_adjustments)
            
            # Store parameter values for this scenario
            for param, value in scenario_params.items():
                if param not in results["parameters"]:
                    results["parameters"][param] = [None] * (len(results["scenarios"]) - 1)
                results["parameters"][param].append(value)
            
            try:
                scenario_financials = self.calculate_financial_metrics(scenario_params)
                
                # Store scenario metrics
                for metric in metrics:
                    scenario_value = self._extract_metric(scenario_financials, metric)
                    results["metrics"][metric].append(scenario_value)
            except Exception as e:
                print(f"Error calculating metrics for scenario {scenario_name}: {str(e)}")
                for metric in metrics:
                    results["metrics"][metric].append(None)
        
        # Calculate percentage changes from base case
        results["percent_changes"] = {}
        for metric in metrics:
            base_value = results["metrics"][metric][-1]  # Base case is the last item
            
            if base_value is not None and base_value != 0:
                percent_changes = []
                for value in results["metrics"][metric]:
                    if value is not None:
                        percent_change = ((value - base_value) / abs(base_value)) * 100
                        percent_changes.append(percent_change)
                    else:
                        percent_changes.append(None)
                results["percent_changes"][metric] = percent_changes
            else:
                results["percent_changes"][metric] = [None] * len(results["scenarios"])
        
        return results
    
    def create_custom_scenario(self, 
                              base_params: Dict[str, Any],
                              custom_params: Dict[str, Any],
                              metrics: Optional[List[str]] = None) -> Dict[str, Any]:
        """Create and evaluate a custom scenario with user-defined parameters.
        
        Args:
            base_params: Dictionary of base parameters for the calculation
            custom_params: Dictionary of parameters to override in the base case
            metrics: List of metrics to calculate
            
        Returns:
            Dictionary with calculation results and comparison to base case
        """
        # Use default metrics if not specified
        if metrics is None:
            metrics = self.default_metrics
            
        results = {
            "base_case": {},
            "custom_scenario": {},
            "parameters": {
                "base": {},
                "custom": {}
            },
            "percent_changes": {}
        }
        
        # Calculate base case
        try:
            base_financials = self.calculate_financial_metrics(base_params)
            
            # Store base metrics
            for metric in metrics:
                base_value = self._extract_metric(base_financials, metric)
                results["base_case"][metric] = base_value
                
            # Store base parameters
            results["parameters"]["base"] = base_params
        except Exception as e:
            print(f"Error calculating base case metrics: {str(e)}")
            for metric in metrics:
                results["base_case"][metric] = None
        
        # Create and calculate custom scenario
        custom_scenario_params = copy.deepcopy(base_params)
        custom_scenario_params.update(custom_params)
        
        try:
            custom_financials = self.calculate_financial_metrics(custom_scenario_params)
            
            # Store custom metrics
            for metric in metrics:
                custom_value = self._extract_metric(custom_financials, metric)
                results["custom_scenario"][metric] = custom_value
                
            # Calculate percentage changes
            for metric in metrics:
                base_value = results["base_case"][metric]
                custom_value = results["custom_scenario"][metric]
                
                if base_value is not None and base_value != 0 and custom_value is not None:
                    percent_change = ((custom_value - base_value) / abs(base_value)) * 100
                    results["percent_changes"][metric] = percent_change
                else:
                    results["percent_changes"][metric] = None
            
            # Store custom parameters
            results["parameters"]["custom"] = custom_scenario_params
        except Exception as e:
            print(f"Error calculating custom scenario metrics: {str(e)}")
            for metric in metrics:
                results["custom_scenario"][metric] = None
                results["percent_changes"][metric] = None
        
        return results
    
    def _extract_metric(self, financial_data: Dict[str, Any], metric: str) -> Optional[float]:
        """Extract a specific metric from financial calculation results.
        
        Args:
            financial_data: Dictionary of financial calculation results
            metric: Name of metric to extract
            
        Returns:
            Metric value if available, None otherwise
        """
        # Handle metrics at different nesting levels in the financial data
        try:
            if "financial_metrics" in financial_data and metric in financial_data["financial_metrics"]:
                return financial_data["financial_metrics"][metric]
            elif metric in financial_data:
                return financial_data[metric]
            elif metric == "lifetime_savings" and "financial_metrics" in financial_data:
                return financial_data["financial_metrics"].get("total_lifetime_savings")
            else:
                # Try to find metric in nested dictionaries
                for key, value in financial_data.items():
                    if isinstance(value, dict) and metric in value:
                        return value[metric]
            
            # Metric not found
            return None
        except Exception:
            return None
    
    def calculate_financial_metrics(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate financial metrics based on parameters.
        
        This is a wrapper around the appropriate calculation engine methods.
        
        Args:
            params: Dictionary of parameters for the calculation
            
        Returns:
            Dictionary with financial calculation results
        """
        # Extract relevant parameters for production calculation
        try:
            # Check if production data is already included
            if "annual_production_kwh" in params or "production" in params:
                # Use existing production data
                if "production" in params:
                    production_data = params["production"]
                else:
                    # Create minimal production data structure
                    production_data = {
                        "annual_production_kwh": params["annual_production_kwh"]
                    }
                
                # Extract utility rate
                electricity_rate = params.get("electricity_rate", 0.12)
                
                # Create utility rate data structure if not provided
                if "utility_rates" not in params:
                    utility_rates = {
                        "residential": electricity_rate,
                        "commercial": electricity_rate * 0.9  # Estimate
                    }
                else:
                    utility_rates = params["utility_rates"]
                
                # Calculate financial metrics using the financial model
                if hasattr(self.financial_model, "calculate_detailed_financials"):
                    # Use detailed financial model if available
                    system_capacity = params.get("system_capacity", 10)
                    annual_production = params.get("annual_production_kwh", 15000)
                    electricity_rate = params.get("electricity_rate", 0.12)
                    
                    # Prepare financial parameters
                    financial_params = {
                        "system_cost_per_watt": params.get("system_cost_per_watt", 2.80),
                        "federal_itc_percent": params.get("incentive_percent", 30),
                        "state_incentive": params.get("state_incentive", 0),
                        "utility_rebate": params.get("utility_rebate", 0),
                        "loan_amount_percent": params.get("loan_percent", 70),
                        "loan_term_years": params.get("loan_term", 20),
                        "loan_rate_percent": params.get("loan_rate", 5.5),
                        "discount_rate": params.get("discount_rate", 4.0),
                        "electricity_inflation": params.get("electricity_inflation", 2.5),
                        "panel_degradation": params.get("panel_degradation", 0.5),
                        "analysis_period_years": params.get("analysis_years", 25),
                        "maintenance_cost_per_kw_year": params.get("maintenance_cost", 20)
                    }
                    
                    return self.financial_model.calculate_detailed_financials(
                        system_capacity, annual_production, electricity_rate, financial_params
                    )
                else:
                    # Fall back to calculation engine's financial metrics
                    return self.calculation_engine.calculate_financial_metrics(
                        production_data, 
                        utility_rates,
                        params.get("system_cost_per_watt", 2.80),
                        params.get("incentive_percent", 30),
                        params.get("incentive_fixed", 0),
                        params.get("discount_rate", 4.0),
                        params.get("electricity_inflation", 2.5),
                        params.get("analysis_years", 25),
                        params.get("maintenance_cost", 20),
                        False  # Don't include sensitivity analysis to avoid recursion
                    )
            else:
                # Calculate production data first
                latitude = params.get("latitude")
                longitude = params.get("longitude")
                
                if latitude is None or longitude is None:
                    raise ValueError("Latitude and longitude are required for production calculation")
                
                production_data = self.calculation_engine.calculate_solar_production(
                    lat=latitude,
                    lon=longitude,
                    system_capacity=params.get("system_capacity", 10),
                    module_type=params.get("module_type", 1),
                    losses=params.get("losses", 14),
                    array_type=params.get("array_type", 2),
                    tilt=params.get("tilt", 20),
                    azimuth=params.get("azimuth", 180),
                    data_source=params.get("data_source", "both")
                )
                
                # Get utility rates
                utility_rates = self.calculation_engine.get_utility_rates(
                    lat=latitude,
                    lon=longitude
                )
                
                # Calculate financial metrics
                return self.calculation_engine.calculate_financial_metrics(
                    production_data, 
                    utility_rates,
                    params.get("system_cost_per_watt", 2.80),
                    params.get("incentive_percent", 30),
                    params.get("incentive_fixed", 0),
                    params.get("discount_rate", 4.0),
                    params.get("electricity_inflation", 2.5),
                    params.get("analysis_years", 25),
                    params.get("maintenance_cost", 20),
                    False  # Don't include sensitivity analysis to avoid recursion
                )
        except Exception as e:
            raise RuntimeError(f"Error calculating financial metrics: {str(e)}")

# Example usage
if __name__ == "__main__":
    # Create a sensitivity analyzer
    analyzer = SensitivityAnalyzer()
    
    # Example parameters (would normally come from user input or API)
    base_params = {
        "latitude": 39.7392,
        "longitude": -104.9903,
        "system_capacity": 10,
        "module_type": 1,
        "array_type": 2,
        "losses": 14,
        "tilt": 20,
        "azimuth": 180,
        "system_cost_per_watt": 2.80,
        "incentive_percent": 30,
        "loan_percent": 70,
        "loan_term": 20,
        "loan_rate": 5.5,
        "discount_rate": 4.0,
        "electricity_inflation": 2.5,
        "analysis_years": 25,
        "maintenance_cost": 20,
        "annual_production_kwh": 15000,  # Optional: can be calculated from lat/lon
        "electricity_rate": 0.12  # Optional: can be retrieved from utility rates API
    }
    
    # Analyze sensitivity for system cost
    # cost_sensitivity = analyzer.analyze_parameter_sensitivity(
    #     base_params, "system_cost_per_watt"
    # )
    # print("System Cost Sensitivity:", cost_sensitivity)
    
    # Generate tornado chart data for multiple parameters
    # tornado_data = analyzer.analyze_multiple_parameters(base_params)
    # print("Tornado Chart Data:", tornado_data)
    
    # Compare predefined scenarios
    scenarios = {
        "optimistic": {
            "system_cost_per_watt": 2.50,
            "electricity_rate": 0.13,
            "electricity_inflation": 3.0,
            "annual_production_kwh": 16500  # 10% higher
        },
        "pessimistic": {
            "system_cost_per_watt": 3.10,
            "electricity_rate": 0.11,
            "electricity_inflation": 2.0,
            "annual_production_kwh": 13500  # 10% lower
        }
    }
    
    # scenario_comparison = analyzer.compare_scenarios(base_params, scenarios)
    # print("Scenario Comparison:", scenario_comparison)
    
    # Create custom scenario with user inputs
    # custom_scenario = analyzer.create_custom_scenario(
    #     base_params,
    #     {"system_cost_per_watt": 2.65, "loan_rate": 4.5, "analysis_years": 30}
    # )
    # print("Custom Scenario:", custom_scenario)