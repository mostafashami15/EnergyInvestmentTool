# tests/test_financial_modeling.py
import unittest
from unittest.mock import patch, MagicMock
import os
import sys
from server.src.financial_modeling import FinancialModel

class TestFinancialModel(unittest.TestCase):
    def setUp(self):
        self.model = FinancialModel()
        
    def test_loan_calculation(self):
        # Test loan payment calculation
        result = self.model.calculate_loan_payments(
            system_cost=28000,
            loan_amount_percent=70,
            loan_term_years=20,
            loan_rate_percent=5.5,
            loan_fees_percent=1.0
        )
        
        # Verify loan amount
        self.assertEqual(result["loan_amount"], 19600)  # 70% of 28000
        
        # Verify loan fees
        self.assertEqual(result["loan_fees"], 196)  # 1% of 19600
        
        # Verify monthly payment calculation
        # Expected monthly payment can be calculated using the formula:
        # P = L * [r(1+r)^n] / [(1+r)^n - 1]
        # where L = loan amount + fees, r = monthly rate, n = number of payments
        total_loan = 19600 + 196
        monthly_rate = 0.055 / 12
        num_payments = 20 * 12
        
        # This is a simplified calculation for expected monthly payment
        expected_monthly = total_loan * (monthly_rate * (1 + monthly_rate)**num_payments) / ((1 + monthly_rate)**num_payments - 1)
        self.assertAlmostEqual(result["monthly_payment"], expected_monthly, delta=0.01)
        
    def test_detailed_financials(self):
        # Test detailed financial projections
        result = self.model.calculate_detailed_financials(
            system_capacity_kw=10,
            annual_production_kwh=15000,
            electricity_rate=0.12,
            params={
                "system_cost_per_watt": 2.80,
                "federal_itc_percent": 30,
                "loan_amount_percent": 70,
                "loan_term_years": 20,
                "loan_rate_percent": 5.5,
                "analysis_period_years": 25
            }
        )
        
        # Verify the structure of the result
        self.assertIn("financial_metrics", result)
        self.assertIn("yearly_cash_flows", result)
        
        # Verify financial metrics
        metrics = result["financial_metrics"]
        self.assertIn("payback_period_years", metrics)
        self.assertIn("roi_percent", metrics)
        self.assertIn("npv", metrics)
        self.assertIn("irr_percent", metrics)
        
        # Verify cash flows
        cash_flows = result["yearly_cash_flows"]
        self.assertEqual(len(cash_flows), 25)  # 25 years total
        
    @patch.object(FinancialModel, '_calculate_irr')
    def test_perform_scenario_analysis(self, mock_irr):
        # Mock the IRR calculation to avoid numerical issues
        mock_irr.return_value = 0.08  # 8% IRR
        
        # Test scenario analysis
        scenarios = self.model.perform_scenario_analysis(
            system_capacity_kw=10,
            annual_production_kwh=15000,
            electricity_rate=0.12,
            base_params={
                "federal_itc_percent": 30,
                "loan_amount_percent": 70,
                "loan_term_years": 20,
                "loan_rate_percent": 5.5
            }
        )
        
        # Verify the structure of the result
        self.assertIn("scenarios", scenarios)
        self.assertIn("comparison", scenarios)
        
        # Verify that all expected scenarios are present
        self.assertIn("base_case", scenarios["scenarios"])
        self.assertIn("optimistic", scenarios["scenarios"])
        self.assertIn("pessimistic", scenarios["scenarios"])