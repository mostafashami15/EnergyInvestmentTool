"""
Unified Calculation Engine for Energy Investment Decision Support System.

This module provides a unified interface for calculating solar energy production
and financial metrics using data from either NREL or NASA POWER APIs.
"""
import sys
import os
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple, Union
import math

# Add the parent directory to the path to import config and data sources
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from data_sources.nrel import NRELDataSource
from data_sources.nasa import NASAPowerDataSource
import config

class CalculationEngine:
    """Unified calculation engine for renewable energy calculations."""
    
    def __init__(self, nrel_api_key: Optional[str] = None):
        """Initialize the calculation engine with data sources."""
        self.nrel = NRELDataSource(nrel_api_key)
        self.nasa = NASAPowerDataSource()
    
    def calculate_solar_production(self, 
                                 lat: float, 
                                 lon: float,
                                 system_capacity: float = 4,
                                 module_type: int = 1,
                                 losses: float = 14,
                                 array_type: int = 1,
                                 tilt: float = 20,
                                 azimuth: float = 180,
                                 data_source: str = "both") -> Dict[str, Any]:
        """Calculate solar energy production using specified data source.
        
        Args:
            lat: Latitude
            lon: Longitude
            system_capacity: System size in kW (default: 4)
            module_type: Module type (1=standard, 2=premium, 3=thin film)
            losses: System losses in % (default: 14)
            array_type: Array type (1=fixed open rack, 2=fixed roof mount, 3=1-axis, etc.)
            tilt: Array tilt in degrees (default: 20)
            azimuth: Array azimuth in degrees (default: 180 - south-facing)
            data_source: Which data source to use ("nrel", "nasa", or "both")
            
        Returns:
            Dictionary containing production calculations and comparisons if both sources used
        """
        result = {
            "location": {
                "lat": lat,
                "lon": lon
            },
            "system_parameters": {
                "capacity_kw": system_capacity,
                "module_type": module_type,
                "losses_percent": losses,
                "array_type": array_type,
                "tilt_degrees": tilt,
                "azimuth_degrees": azimuth
            },
            "data_sources_used": data_source
        }
        
        # Get NREL data if requested
        if data_source.lower() in ["nrel", "both"]:
            try:
                nrel_data = self.nrel.get_pvwatts(
                    lat, lon, system_capacity, module_type, 
                    losses, array_type, tilt, azimuth
                )
                
                # Extract annual and monthly production
                nrel_annual = nrel_data["outputs"]["ac_annual"]
                nrel_monthly = nrel_data["outputs"]["ac_monthly"]
                
                # Add to results
                result["nrel"] = {
                    "annual_production_kwh": nrel_annual,
                    "monthly_production_kwh": nrel_monthly,
                    "capacity_factor_percent": nrel_data["outputs"]["capacity_factor"],
                    "production_per_kw": nrel_annual / system_capacity
                }
            except Exception as e:
                result["nrel"] = {"error": str(e)}
        
        # Get NASA data if requested
        if data_source.lower() in ["nasa", "both"]:
            try:
                # Set efficiency based on module type
                if module_type == 1:  # Standard
                    efficiency = 0.15
                elif module_type == 2:  # Premium
                    efficiency = 0.19
                else:  # Thin film
                    efficiency = 0.10
                
                # Adjust performance ratio based on losses
                performance_ratio = (100 - losses) / 100
                
                # Adjust for array type
                array_factor = 1.0
                if array_type == 3:  # 1-axis tracking
                    array_factor = 1.2
                elif array_type == 4:  # 1-axis backtracking
                    array_factor = 1.15
                elif array_type == 5:  # 2-axis tracking
                    array_factor = 1.3
                
                # Calculate using NASA data
                nasa_data = self.nasa.calculate_solar_potential(
                    lat, lon, system_capacity, 
                    efficiency * array_factor, performance_ratio
                )
                
                # Extract from NASA result
                nasa_annual = nasa_data["annual_production_kWh"]
                nasa_monthly = [month["production_kWh"] for month in nasa_data["monthly_production_kWh"]]
                
                # Add to results
                result["nasa"] = {
                    "annual_production_kwh": nasa_annual,
                    "monthly_production_kwh": nasa_monthly,
                    "production_per_kw": nasa_annual / system_capacity
                }
            except Exception as e:
                result["nasa"] = {"error": str(e)}
        
        # Compare results if both sources used
        if data_source.lower() == "both" and "error" not in result.get("nrel", {}) and "error" not in result.get("nasa", {}):
            nrel_annual = result["nrel"]["annual_production_kwh"]
            nasa_annual = result["nasa"]["annual_production_kwh"]
            
            # Calculate difference
            absolute_diff = nrel_annual - nasa_annual
            percent_diff = (absolute_diff / nasa_annual) * 100
            
            # Add comparison to results
            result["comparison"] = {
                "absolute_difference_kwh": absolute_diff,
                "percent_difference": percent_diff,
                "average_production_kwh": (nrel_annual + nasa_annual) / 2,
                "conservative_estimate_kwh": min(nrel_annual, nasa_annual),
                "optimistic_estimate_kwh": max(nrel_annual, nasa_annual)
            }
        
        return result
    
    def get_utility_rates(self, lat: float, lon: float) -> Dict[str, Any]:
        """Get utility rate information for a location.
        
        Args:
            lat: Latitude
            lon: Longitude
            
        Returns:
            Dictionary with utility rate data
        """
        try:
            utility_data = self.nrel.get_utility_rates(lat, lon)
            
            # Extract the most relevant information
            result = {
                "location": {
                    "lat": lat,
                    "lon": lon
                },
                "utility": utility_data["outputs"]["utility_name"],
                "commercial_rate": utility_data["outputs"]["commercial"],
                "residential_rate": utility_data["outputs"]["residential"],
                "industrial_rate": utility_data["outputs"]["industrial"]
            }
            
            return result
        except Exception as e:
            return {"error": str(e)}
    
    def calculate_financial_metrics(self,
                                  production_data: Dict[str, Any],
                                  utility_rates: Dict[str, Any],
                                  system_cost_per_watt: float = 2.80,
                                  incentive_percent: float = 0,
                                  incentive_fixed: float = 0,
                                  discount_rate: float = 0.04,
                                  electricity_inflation: float = 0.025,
                                  analysis_period_years: int = 25,
                                  maintenance_cost_per_kw_year: float = 20,
                                  include_sensitivity: bool = False) -> Dict[str, Any]:
        """Calculate financial metrics for a solar installation.
        
        Args:
            production_data: Output from calculate_solar_production()
            utility_rates: Output from get_utility_rates()
            system_cost_per_watt: Cost per watt in USD (default: $2.80)
            incentive_percent: Percentage incentive (e.g., 30 for 30% tax credit)
            incentive_fixed: Fixed incentive amount in USD
            discount_rate: Annual discount rate for NPV calculation (default: 4%)
            electricity_inflation: Annual electricity price inflation (default: 2.5%)
            analysis_period_years: Years to analyze (default: 25)
            maintenance_cost_per_kw_year: Annual maintenance cost per kW (default: $20)
            include_sensitivity: Whether to include sensitivity analysis
            
        Returns:
            Dictionary with financial metrics
        """
        # Extract necessary data
        system_capacity_kw = production_data["system_parameters"]["capacity_kw"]
        system_capacity_w = system_capacity_kw * 1000
        
        # Determine which production estimate to use
        if "comparison" in production_data:
            # If we have both sources, use the average
            annual_production_kwh = production_data["comparison"]["average_production_kwh"]
        elif "nrel" in production_data and "error" not in production_data["nrel"]:
            annual_production_kwh = production_data["nrel"]["annual_production_kwh"]
        elif "nasa" in production_data and "error" not in production_data["nasa"]:
            annual_production_kwh = production_data["nasa"]["annual_production_kwh"]
        else:
            return {"error": "No valid production data available"}
        
        # Get electricity rate
        if "error" in utility_rates:
            return {"error": f"Unable to get utility rates: {utility_rates['error']}"}
        
        electricity_rate = utility_rates["residential_rate"]
        
        # Calculate initial system cost
        initial_cost = system_capacity_w * system_cost_per_watt
        
        # Apply incentives
        incentive_amount = (initial_cost * (incentive_percent / 100)) + incentive_fixed
        net_system_cost = initial_cost - incentive_amount
        
        # Calculate annual maintenance cost
        annual_maintenance = system_capacity_kw * maintenance_cost_per_kw_year
        
        # Initialize result dictionary
        result = {
            "system_details": {
                "capacity_kw": system_capacity_kw,
                "annual_production_kwh": annual_production_kwh,
                "electricity_rate_per_kwh": electricity_rate
            },
            "costs": {
                "cost_per_watt": system_cost_per_watt,
                "initial_system_cost": initial_cost,
                "incentive_amount": incentive_amount,
                "net_system_cost": net_system_cost,
                "annual_maintenance": annual_maintenance
            }
        }
        
        # Calculate annual savings and cash flows
        annual_savings_year1 = annual_production_kwh * electricity_rate
        payback_reached = False
        cumulative_cash_flow = -net_system_cost
        payback_period = analysis_period_years
        npv = -net_system_cost
        yearly_cash_flows = []
        
        for year in range(1, analysis_period_years + 1):
            # Calculate electricity rate with inflation
            year_electricity_rate = electricity_rate * ((1 + electricity_inflation) ** (year - 1))
            
            # Calculate annual savings
            annual_savings = annual_production_kwh * year_electricity_rate
            
            # Calculate net cash flow (savings minus maintenance)
            net_cash_flow = annual_savings - annual_maintenance
            
            # Update cumulative cash flow
            cumulative_cash_flow += net_cash_flow
            
            # Check if payback reached in this year
            if not payback_reached and cumulative_cash_flow >= 0:
                # Calculate more precise payback period using linear interpolation
                prev_year_cash_flow = cumulative_cash_flow - net_cash_flow
                payback_period = year - 1 + (0 - prev_year_cash_flow) / (cumulative_cash_flow - prev_year_cash_flow)
                payback_reached = True
            
            # Calculate discounted cash flow for NPV
            discounted_cash_flow = net_cash_flow / ((1 + discount_rate) ** year)
            npv += discounted_cash_flow
            
            # Store yearly values
            yearly_cash_flows.append({
                "year": year,
                "electricity_rate": year_electricity_rate,
                "annual_savings": annual_savings,
                "maintenance_cost": annual_maintenance,
                "net_cash_flow": net_cash_flow,
                "cumulative_cash_flow": cumulative_cash_flow,
                "discounted_cash_flow": discounted_cash_flow
            })
        
        # Calculate ROI
        total_returns = sum(year["net_cash_flow"] for year in yearly_cash_flows)
        roi = (total_returns - net_system_cost) / net_system_cost * 100
        
        # Calculate IRR
        irr = self._calculate_irr([-net_system_cost] + [year["net_cash_flow"] for year in yearly_cash_flows])
        
        # Calculate LCOE (Levelized Cost of Energy)
        total_production = annual_production_kwh * analysis_period_years
        total_costs = net_system_cost + (annual_maintenance * analysis_period_years)
        lcoe = total_costs / total_production
        
        # Add financial metrics to results
        result["financial_metrics"] = {
            "annual_savings_year1": annual_savings_year1,
            "total_savings": total_returns,
            "payback_period_years": payback_period,
            "roi_percent": roi,
            "npv": npv,
            "irr_percent": irr * 100,
            "lcoe_per_kwh": lcoe
        }
        
        # Add yearly cash flows
        result["yearly_cash_flows"] = yearly_cash_flows
        
        # Add sensitivity analysis if requested
        if include_sensitivity:
            result["sensitivity_analysis"] = self._perform_sensitivity_analysis(
                production_data, utility_rates, system_cost_per_watt,
                incentive_percent, incentive_fixed, discount_rate,
                electricity_inflation, analysis_period_years, maintenance_cost_per_kw_year
            )
        
        return result
    
    def _calculate_irr(self, cash_flows: List[float], guess: float = 0.1) -> float:
        """Calculate Internal Rate of Return using Newton's method.
        
        Args:
            cash_flows: List of cash flows (negative for investments, positive for returns)
            guess: Initial guess for IRR
            
        Returns:
            IRR as a decimal (e.g., 0.08 for 8%)
        """
        tolerance = 0.0001
        max_iterations = 100
        rate = guess
        
        for i in range(max_iterations):
            npv = sum(cf / ((1 + rate) ** t) for t, cf in enumerate(cash_flows))
            if abs(npv) < tolerance:
                return rate
            
            # First derivative of NPV function
            d_npv = sum(-t * cf / ((1 + rate) ** (t + 1)) for t, cf in enumerate(cash_flows) if t > 0)
            
            # Newton's method update
            rate = rate - npv / d_npv if d_npv != 0 else rate * 1.1
            
            # Check for convergence
            if abs(npv) < tolerance:
                return rate
        
        # If we didn't converge, return the best estimate
        return rate
    
    def _perform_sensitivity_analysis(self,
                                    production_data: Dict[str, Any],
                                    utility_rates: Dict[str, Any],
                                    system_cost_per_watt: float,
                                    incentive_percent: float,
                                    incentive_fixed: float,
                                    discount_rate: float,
                                    electricity_inflation: float,
                                    analysis_period_years: int,
                                    maintenance_cost_per_kw_year: float) -> Dict[str, Any]:
        """Perform sensitivity analysis for key parameters.
        
        Returns:
            Dictionary with sensitivity analysis results
        """
        result = {}
        
        # Sensitivity to system cost
        cost_variations = [0.8, 0.9, 1.0, 1.1, 1.2]
        cost_sensitivity = []
        
        for factor in cost_variations:
            varied_cost = system_cost_per_watt * factor
            metrics = self.calculate_financial_metrics(
                production_data, utility_rates, varied_cost,
                incentive_percent, incentive_fixed, discount_rate,
                electricity_inflation, analysis_period_years, maintenance_cost_per_kw_year,
                include_sensitivity=False
            )
            
            cost_sensitivity.append({
                "system_cost_per_watt": varied_cost,
                "variation": f"{(factor - 1) * 100:+.0f}%",
                "npv": metrics["financial_metrics"]["npv"],
                "payback_period_years": metrics["financial_metrics"]["payback_period_years"],
                "roi_percent": metrics["financial_metrics"]["roi_percent"]
            })
        
        result["system_cost_sensitivity"] = cost_sensitivity
        
        # Sensitivity to electricity rates
        rate_variations = [0.8, 0.9, 1.0, 1.1, 1.2]
        rate_sensitivity = []
        
        for factor in rate_variations:
            # Create a modified utility_rates dict
            varied_rates = utility_rates.copy()
            varied_rates["residential_rate"] = utility_rates["residential_rate"] * factor
            
            metrics = self.calculate_financial_metrics(
                production_data, varied_rates, system_cost_per_watt,
                incentive_percent, incentive_fixed, discount_rate,
                electricity_inflation, analysis_period_years, maintenance_cost_per_kw_year,
                include_sensitivity=False
            )
            
            rate_sensitivity.append({
                "electricity_rate": varied_rates["residential_rate"],
                "variation": f"{(factor - 1) * 100:+.0f}%",
                "npv": metrics["financial_metrics"]["npv"],
                "payback_period_years": metrics["financial_metrics"]["payback_period_years"],
                "roi_percent": metrics["financial_metrics"]["roi_percent"]
            })
        
        result["electricity_rate_sensitivity"] = rate_sensitivity
        
        # Sensitivity to production estimates
        production_variations = [0.8, 0.9, 1.0, 1.1, 1.2]
        production_sensitivity = []
        
        for factor in production_variations:
            # Create a modified production_data dict
            varied_production = production_data.copy()
            
            # If comparison exists, modify it
            if "comparison" in varied_production:
                varied_production["comparison"] = varied_production["comparison"].copy()
                varied_production["comparison"]["average_production_kwh"] *= factor
            # Otherwise modify whichever source is available
            elif "nrel" in varied_production and "error" not in varied_production["nrel"]:
                varied_production["nrel"] = varied_production["nrel"].copy()
                varied_production["nrel"]["annual_production_kwh"] *= factor
            elif "nasa" in varied_production and "error" not in varied_production["nasa"]:
                varied_production["nasa"] = varied_production["nasa"].copy()
                varied_production["nasa"]["annual_production_kwh"] *= factor
            
            metrics = self.calculate_financial_metrics(
                varied_production, utility_rates, system_cost_per_watt,
                incentive_percent, incentive_fixed, discount_rate,
                electricity_inflation, analysis_period_years, maintenance_cost_per_kw_year,
                include_sensitivity=False
            )
            
            # Extract the annual production for reporting
            if "comparison" in varied_production:
                annual_production = varied_production["comparison"]["average_production_kwh"]
            elif "nrel" in varied_production and "error" not in varied_production["nrel"]:
                annual_production = varied_production["nrel"]["annual_production_kwh"]
            else:
                annual_production = varied_production["nasa"]["annual_production_kwh"]
            
            production_sensitivity.append({
                "annual_production_kwh": annual_production,
                "variation": f"{(factor - 1) * 100:+.0f}%",
                "npv": metrics["financial_metrics"]["npv"],
                "payback_period_years": metrics["financial_metrics"]["payback_period_years"],
                "roi_percent": metrics["financial_metrics"]["roi_percent"]
            })
        
        result["production_sensitivity"] = production_sensitivity
        
        return result