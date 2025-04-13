"""
Financial Modeling Module for Energy Investment Decision Support System.

This module provides advanced financial analysis for renewable energy investments,
including ROI calculations, NPV, IRR, and scenario modeling.
"""
import sys
import os
from typing import Dict, Any, List, Optional, Tuple, Union
import math
import numpy as np
from datetime import datetime, date

class FinancialModel:
    """Financial modeling for renewable energy investments."""
    
    def __init__(self):
        """Initialize the financial model."""
        # Default financial parameters
        self.default_params = {
            # System cost parameters
            "system_cost_per_watt": 2.80,  # $2.80/W for residential solar (2023)
            "balance_of_system_percent": 60,  # BoS as percent of total cost
            "inverter_cost_percent": 10,  # Inverter as percent of total cost
            
            # Incentives and rebates
            "federal_itc_percent": 30,  # Federal Investment Tax Credit (%)
            "state_incentive_percent": 0,  # State tax credits/rebates (%)
            "utility_rebate_per_watt": 0,  # Utility rebates ($/W)
            "srec_price": 0,  # Solar Renewable Energy Credit price ($/MWh)
            "srec_years": 0,  # Years of SREC eligibility
            
            # Loan parameters
            "loan_amount_percent": 0,  # Percent of system cost financed (0 = cash purchase)
            "loan_term_years": 20,  # Loan term in years
            "loan_rate_percent": 5.5,  # Loan interest rate (%)
            "loan_fees_percent": 1.0,  # Loan origination fees (%)
            
            # Operation parameters
            "analysis_period_years": 25,  # Analysis period (typically 25-30 years)
            "panel_degradation_percent": 0.5,  # Annual panel degradation rate (%)
            "maintenance_cost_per_kw_year": 20,  # Annual maintenance cost ($/kW)
            "insurance_cost_percent": 0.5,  # Annual insurance as % of system cost
            "inverter_replacement_year": 15,  # Year to replace inverter
            "inverter_replacement_cost_percent": 8,  # Cost as % of initial system cost
            
            # Economic parameters
            "electricity_inflation_percent": 3.0,  # Annual electricity price inflation (%)
            "general_inflation_percent": 2.5,  # General inflation rate (%)
            "discount_rate_percent": 6.0,  # Discount rate for NPV (%)
            "tax_rate_percent": 22,  # Effective income tax rate (%)
            
            # Utility parameters
            "net_metering": True,  # Whether net metering is available
            "export_rate_percent": 100,  # Value of exported electricity (% of retail rate)
            "fixed_charge_monthly": 0,  # Fixed monthly utility charges ($)
            "demand_charge_monthly": 0  # Demand charges for commercial systems ($/kW)
        }
    
    def calculate_loan_payments(self, 
                              system_cost: float,
                              loan_amount_percent: float,
                              loan_term_years: int,
                              loan_rate_percent: float,
                              loan_fees_percent: float) -> Dict[str, Any]:
        """Calculate loan parameters and payment schedule.
        
        Args:
            system_cost: Total system cost ($)
            loan_amount_percent: Percentage of system cost financed
            loan_term_years: Term of loan in years
            loan_rate_percent: Annual interest rate (%)
            loan_fees_percent: Loan origination fees (%)
            
        Returns:
            Dictionary with loan details and payment schedule
        """
        loan_amount = system_cost * (loan_amount_percent / 100)
        
        # If no loan, return empty structure
        if loan_amount <= 0:
            return {
                "loan_amount": 0,
                "down_payment": system_cost,
                "monthly_payment": 0,
                "annual_payment": 0,
                "total_payments": 0,
                "total_interest": 0,
                "loan_fees": 0,
                "payment_schedule": []
            }
        
        # Calculate loan parameters
        loan_fees = loan_amount * (loan_fees_percent / 100)
        financed_amount = loan_amount + loan_fees
        down_payment = system_cost - loan_amount
        
        # Monthly interest rate
        monthly_rate = (loan_rate_percent / 100) / 12
        
        # Number of payments
        num_payments = loan_term_years * 12
        
        # Calculate monthly payment using the PMT formula
        if monthly_rate == 0:
            # Special case for 0% loans
            monthly_payment = financed_amount / num_payments
        else:
            monthly_payment = financed_amount * (monthly_rate * (1 + monthly_rate)**num_payments) / ((1 + monthly_rate)**num_payments - 1)
        
        # Generate payment schedule
        remaining_balance = financed_amount
        payment_schedule = []
        total_interest = 0
        
        for payment_num in range(1, num_payments + 1):
            interest_payment = remaining_balance * monthly_rate
            principal_payment = monthly_payment - interest_payment
            remaining_balance -= principal_payment
            total_interest += interest_payment
            
            # Add payment details to schedule
            payment_schedule.append({
                "payment_number": payment_num,
                "date": self._get_payment_date(payment_num),
                "payment_amount": monthly_payment,
                "principal": principal_payment,
                "interest": interest_payment,
                "remaining_balance": max(0, remaining_balance)  # Avoid negative due to rounding
            })
        
        return {
            "loan_amount": loan_amount,
            "financed_amount": financed_amount,
            "down_payment": down_payment,
            "monthly_payment": monthly_payment,
            "annual_payment": monthly_payment * 12,
            "total_payments": monthly_payment * num_payments,
            "total_interest": total_interest,
            "loan_fees": loan_fees,
            "payment_schedule": payment_schedule
        }
    
    def _get_payment_date(self, payment_number: int) -> str:
        """Calculate payment date string based on payment number.
        
        Args:
            payment_number: Payment number (1-indexed)
            
        Returns:
            Date string in YYYY-MM format
        """
        # Assuming payments start next month
        today = date.today()
        year = today.year + ((today.month - 1 + payment_number) // 12)
        month = (today.month - 1 + payment_number) % 12 + 1
        return f"{year}-{month:02d}"
    
    def calculate_detailed_financials(self,
                                    system_capacity_kw: float,
                                    annual_production_kwh: float,
                                    electricity_rate: float,
                                    params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Calculate detailed financial projections for a renewable energy system.
        
        Args:
            system_capacity_kw: System capacity in kW
            annual_production_kwh: Annual energy production in kWh
            electricity_rate: Current electricity rate ($/kWh)
            params: Dictionary of financial parameters (will use defaults for any missing)
            
        Returns:
            Dictionary with detailed financial analysis
        """
        # Merge provided params with defaults
        p = self.default_params.copy()
        if params:
            p.update(params)
        
        # System cost calculations
        system_capacity_w = system_capacity_kw * 1000
        system_cost = system_capacity_w * p["system_cost_per_watt"]
        
        # Incentive calculations
        federal_itc = system_cost * (p["federal_itc_percent"] / 100)
        state_incentive = system_cost * (p["state_incentive_percent"] / 100)
        utility_rebate = system_capacity_w * p["utility_rebate_per_watt"]
        total_incentives = federal_itc + state_incentive + utility_rebate
        
        # Net cost after incentives
        net_system_cost = system_cost - total_incentives
        
        # Loan calculations
        loan_details = self.calculate_loan_payments(
            system_cost,
            p["loan_amount_percent"],
            p["loan_term_years"],
            p["loan_rate_percent"],
            p["loan_fees_percent"]
        )
        
        # Annual calculations
        yearly_cash_flows = []
        cumulative_cash_flow = -net_system_cost + total_incentives
        payback_reached = False
        payback_period = p["analysis_period_years"]
        
        # For NPV calculations
        discount_rate = p["discount_rate_percent"] / 100
        npv = -net_system_cost + total_incentives  # Initial investment (negative)
        
        # For IRR calculations
        cash_flows = [-net_system_cost + total_incentives]
        
        # Calculate annual maintenance and insurance costs
        annual_maintenance = system_capacity_kw * p["maintenance_cost_per_kw_year"]
        annual_insurance = system_cost * (p["insurance_cost_percent"] / 100)
        
        # Monthly fixed charges
        annual_fixed_charges = p["fixed_charge_monthly"] * 12
        
        for year in range(1, p["analysis_period_years"] + 1):
            # Calculate degraded production
            degradation_factor = (1 - p["panel_degradation_percent"] / 100) ** (year - 1)
            year_production_kwh = annual_production_kwh * degradation_factor
            
            # Calculate electricity rate with inflation
            year_electricity_rate = electricity_rate * ((1 + p["electricity_inflation_percent"] / 100) ** (year - 1))
            
            # Calculate annual energy savings
            annual_savings = year_production_kwh * year_electricity_rate
            
            # Calculate SREC revenue
            srec_revenue = 0
            if year <= p["srec_years"]:
                srec_revenue = (year_production_kwh / 1000) * p["srec_price"]  # SRECs are per MWh
            
            # Calculate annual costs
            year_maintenance = annual_maintenance * ((1 + p["general_inflation_percent"] / 100) ** (year - 1))
            year_insurance = annual_insurance * ((1 + p["general_inflation_percent"] / 100) ** (year - 1))
            
            # Calculate inverter replacement cost
            inverter_replacement = 0
            if year == p["inverter_replacement_year"]:
                inverter_replacement = system_cost * (p["inverter_replacement_cost_percent"] / 100)
            
            # Calculate loan payment for this year
            year_loan_payment = 0
            if year <= p["loan_term_years"]:
                year_loan_payment = loan_details["annual_payment"]
            
            # Calculate net cash flow
            net_cash_flow = annual_savings + srec_revenue - year_maintenance - year_insurance - inverter_replacement - year_loan_payment
            
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
            
            # Add cash flow for IRR calculation
            cash_flows.append(net_cash_flow)
            
            # Store yearly values
            yearly_cash_flows.append({
                "year": year,
                "production_kwh": year_production_kwh,
                "electricity_rate": year_electricity_rate,
                "energy_savings": annual_savings,
                "srec_revenue": srec_revenue,
                "maintenance_cost": year_maintenance,
                "insurance_cost": year_insurance,
                "inverter_replacement": inverter_replacement,
                "loan_payment": year_loan_payment,
                "net_cash_flow": net_cash_flow,
                "cumulative_cash_flow": cumulative_cash_flow,
                "discounted_cash_flow": discounted_cash_flow
            })
        
        # Calculate IRR
        irr = self._calculate_irr(cash_flows)
        
        # Calculate LCOE (Levelized Cost of Energy)
        total_production = sum(year["production_kwh"] for year in yearly_cash_flows)
        total_costs = net_system_cost + sum(year["maintenance_cost"] + year["insurance_cost"] + year["inverter_replacement"] for year in yearly_cash_flows)
        lcoe = total_costs / total_production
        
        # Calculate ROI
        total_returns = sum(year["energy_savings"] + year["srec_revenue"] for year in yearly_cash_flows)
        total_costs = net_system_cost + sum(year["maintenance_cost"] + year["insurance_cost"] + year["inverter_replacement"] for year in yearly_cash_flows)
        roi = (total_returns - total_costs) / net_system_cost * 100
        
        # Return comprehensive financial analysis
        return {
            "system_details": {
                "capacity_kw": system_capacity_kw,
                "annual_production_kwh_initial": annual_production_kwh,
                "electricity_rate_initial": electricity_rate
            },
            "costs": {
                "system_cost": system_cost,
                "cost_per_watt": p["system_cost_per_watt"],
                "incentives": {
                    "federal_itc": federal_itc,
                    "state_incentive": state_incentive,
                    "utility_rebate": utility_rebate,
                    "total_incentives": total_incentives
                },
                "net_system_cost": net_system_cost,
                "annual_maintenance_initial": annual_maintenance,
                "annual_insurance_initial": annual_insurance
            },
            "loan": loan_details,
            "financial_metrics": {
                "payback_period_years": payback_period,
                "roi_percent": roi,
                "npv": npv,
                "irr_percent": irr * 100,
                "lcoe_per_kwh": lcoe,
                "first_year_savings": yearly_cash_flows[0]["energy_savings"],
                "total_lifetime_savings": sum(year["energy_savings"] for year in yearly_cash_flows),
                "total_lifetime_revenue": sum(year["energy_savings"] + year["srec_revenue"] for year in yearly_cash_flows),
                "total_lifetime_costs": sum(year["maintenance_cost"] + year["insurance_cost"] + year["inverter_replacement"] for year in yearly_cash_flows),
                "lifetime_roi": (sum(year["net_cash_flow"] for year in yearly_cash_flows) / net_system_cost) * 100
            },
            "yearly_cash_flows": yearly_cash_flows
        }
    
    def _calculate_irr(self, cash_flows, max_iterations=100, tolerance=1e-6):
        """
        Calculate Internal Rate of Return using iterative approach.
        
        Args:
            cash_flows: List of cash flows, starting with initial investment (negative)
            max_iterations: Maximum number of iterations
            tolerance: Convergence tolerance
            
        Returns:
            IRR as a decimal (e.g., 0.05 for 5%)
        """
        # Basic validation
        if not cash_flows or len(cash_flows) < 2:
            return 0.0
        
        # Check if calculation is possible
        if all(cf <= 0 for cf in cash_flows) or all(cf >= 0 for cf in cash_flows):
            return 0.0  # No solution possible if all cash flows are same sign
        
        # Start with a reasonable guess
        rate = 0.1  # 10% initial guess
        
        # Newton's method converges quadratically for well-behaved functions
        for _ in range(max_iterations):
            try:
                # Calculate NPV at current rate
                npv = 0
                for t, cf in enumerate(cash_flows):
                    # Use safer calculation to avoid overflow
                    if t == 0:
                        npv += cf
                    else:
                        # Limit the exponent to avoid overflow
                        if t > 100 or (1 + rate) ** t > 1e100:
                            denominator = float('inf')
                        else:
                            denominator = (1 + rate) ** t
                        npv += cf / denominator
                
                # If NPV is very close to zero, we've found the IRR
                if abs(npv) < tolerance:
                    return rate
                
                # Calculate derivative of NPV function
                dnpv = 0
                for t, cf in enumerate(cash_flows):
                    if t > 0:  # Skip initial investment
                        try:
                            # Safer derivative calculation
                            if t > 100 or (1 + rate) ** (t + 1) > 1e100:
                                continue
                            dnpv -= t * cf / ((1 + rate) ** (t + 1))
                        except (OverflowError, ZeroDivisionError):
                            continue
                
                # Avoid division by zero
                if abs(dnpv) < 1e-10:
                    # Adjust rate by a small amount and try again
                    rate = rate + 0.01
                    continue
                
                # Newton's method formula: r_next = r - f(r) / f'(r)
                new_rate = rate - npv / dnpv
                
                # Sanity check on new rate
                if new_rate <= -1 or new_rate > 1:
                    # If the rate goes out of reasonable bounds, constrain it
                    new_rate = max(min(new_rate, 0.5), -0.5)
                
                # Check for convergence
                if abs(new_rate - rate) < tolerance:
                    return new_rate
                
                rate = new_rate
                
            except (OverflowError, ZeroDivisionError, ValueError):
                # If we encounter numerical issues, try a different approach
                rate = rate * 0.9  # Try a smaller rate
                
                # If rate gets too small, return a default value
                if abs(rate) < 1e-6:
                    return 0.0
        
        # If we couldn't converge, return the best estimate
        return rate
    
    def perform_scenario_analysis(self,
                                system_capacity_kw: float,
                                annual_production_kwh: float,
                                electricity_rate: float,
                                base_params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Perform scenario analysis with different parameter sets.
        
        Args:
            system_capacity_kw: System capacity in kW
            annual_production_kwh: Annual energy production in kWh
            electricity_rate: Current electricity rate ($/kWh)
            base_params: Base financial parameters (will use defaults for any missing)
            
        Returns:
            Dictionary with scenario analysis results
        """
        # Merge provided params with defaults
        base = self.default_params.copy()
        if base_params:
            base.update(base_params)
        
        scenarios = {
            "base_case": self.calculate_detailed_financials(
                system_capacity_kw, annual_production_kwh, electricity_rate, base
            ),
            
            "optimistic": self.calculate_detailed_financials(
                system_capacity_kw, annual_production_kwh * 1.1, electricity_rate * 1.1,
                {**base, 
                 "system_cost_per_watt": base["system_cost_per_watt"] * 0.9,
                 "electricity_inflation_percent": base["electricity_inflation_percent"] + 1.0,
                 "panel_degradation_percent": base["panel_degradation_percent"] * 0.8}
            ),
            
            "pessimistic": self.calculate_detailed_financials(
                system_capacity_kw, annual_production_kwh * 0.9, electricity_rate * 0.9,
                {**base, 
                 "system_cost_per_watt": base["system_cost_per_watt"] * 1.1,
                 "electricity_inflation_percent": base["electricity_inflation_percent"] - 0.5,
                 "panel_degradation_percent": base["panel_degradation_percent"] * 1.2,
                 "maintenance_cost_per_kw_year": base["maintenance_cost_per_kw_year"] * 1.2}
            ),
            
            "high_financing": self.calculate_detailed_financials(
                system_capacity_kw, annual_production_kwh, electricity_rate,
                {**base, 
                 "loan_amount_percent": 80,
                 "loan_rate_percent": 7.0,
                 "loan_term_years": 15}
            ),
            
            "cash_purchase": self.calculate_detailed_financials(
                system_capacity_kw, annual_production_kwh, electricity_rate,
                {**base, "loan_amount_percent": 0}
            )
        }
        
        # Extract key metrics for comparison
        comparison = {}
        for scenario_name, scenario_data in scenarios.items():
            comparison[scenario_name] = {
                "payback_years": scenario_data["financial_metrics"]["payback_period_years"],
                "roi_percent": scenario_data["financial_metrics"]["roi_percent"],
                "npv": scenario_data["financial_metrics"]["npv"],
                "irr_percent": scenario_data["financial_metrics"]["irr_percent"],
                "lcoe_per_kwh": scenario_data["financial_metrics"]["lcoe_per_kwh"],
                "lifetime_savings": scenario_data["financial_metrics"]["total_lifetime_savings"]
            }
        
        return {
            "scenarios": scenarios,
            "comparison": comparison
        }
    
    def perform_sensitivity_analysis(self,
                                   system_capacity_kw: float,
                                   annual_production_kwh: float,
                                   electricity_rate: float,
                                   base_params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Perform sensitivity analysis for key parameters.
        
        Args:
            system_capacity_kw: System capacity in kW
            annual_production_kwh: Annual energy production in kWh
            electricity_rate: Current electricity rate ($/kWh)
            base_params: Base financial parameters (will use defaults for any missing)
            
        Returns:
            Dictionary with sensitivity analysis results
        """
        # Merge provided params with defaults
        base = self.default_params.copy()
        if base_params:
            base.update(base_params)
        
        result = {}
        
        # Parameters to analyze with variation ranges
        sensitivity_params = {
            "system_cost_per_watt": [-20, -10, 0, 10, 20],  # % change
            "electricity_rate": [-20, -10, 0, 10, 20],  # % change
            "annual_production": [-20, -10, 0, 10, 20],  # % change
            "electricity_inflation_percent": [-2, -1, 0, 1, 2],  # absolute change
            "panel_degradation_percent": [-0.2, -0.1, 0, 0.1, 0.2],  # absolute change
            "discount_rate_percent": [-2, -1, 0, 1, 2],  # absolute change
            "loan_rate_percent": [-2, -1, 0, 1, 2]  # absolute change
        }
        
        # Run analysis for each parameter
        for param_name, variations in sensitivity_params.items():
            param_results = []
            
            for variation in variations:
                # Create modified parameters
                modified_params = base.copy()
                
                if param_name == "electricity_rate":
                    # This is an input parameter, not in the params dict
                    modified_electricity_rate = electricity_rate * (1 + variation / 100)
                    modified_params = base
                    var_electricity_rate = modified_electricity_rate
                    var_production = annual_production_kwh
                elif param_name == "annual_production":
                    # This is an input parameter, not in the params dict
                    modified_production = annual_production_kwh * (1 + variation / 100)
                    modified_params = base
                    var_electricity_rate = electricity_rate
                    var_production = modified_production
                else:
                    # For parameters in the params dict
                    if param_name in ["electricity_inflation_percent", "panel_degradation_percent", 
                                     "discount_rate_percent", "loan_rate_percent"]:
                        # Absolute change
                        modified_params[param_name] = base[param_name] + variation
                    else:
                        # Percentage change
                        modified_params[param_name] = base[param_name] * (1 + variation / 100)
                    
                    var_electricity_rate = electricity_rate
                    var_production = annual_production_kwh
                
                # Calculate financials with modified parameters
                financials = self.calculate_detailed_financials(
                    system_capacity_kw, var_production, var_electricity_rate, modified_params
                )
                
                # Extract key metrics
                param_results.append({
                    "variation": variation,
                    "variation_type": "absolute" if param_name in ["electricity_inflation_percent", 
                                                                 "panel_degradation_percent", 
                                                                 "discount_rate_percent",
                                                                 "loan_rate_percent"] else "percent",
                    "payback_years": financials["financial_metrics"]["payback_period_years"],
                    "npv": financials["financial_metrics"]["npv"],
                    "roi_percent": financials["financial_metrics"]["roi_percent"],
                    "irr_percent": financials["financial_metrics"]["irr_percent"],
                    "lcoe_per_kwh": financials["financial_metrics"]["lcoe_per_kwh"]
                })
            
            result[param_name] = param_results
        
        return result