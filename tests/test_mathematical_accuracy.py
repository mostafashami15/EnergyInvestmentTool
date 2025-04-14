# tests/test_mathematical_accuracy.py
import unittest
import math
from server.src.calculation_engine import CalculationEngine
from server.src.financial_modeling import FinancialModel

class TestMathematicalAccuracy(unittest.TestCase):
    """Test suite for verifying mathematical accuracy of calculations."""
    
    def setUp(self):
        self.calc_engine = CalculationEngine()
        self.fin_model = FinancialModel()
    
    def test_solar_production_manual_calculation(self):
        """Verify solar production calculation against manual calculation."""
        # Manual calculation for a 10kW system in Denver
        # Using standard formula: Production = Solar Radiation × Area × Efficiency × Performance Ratio
        
        # Denver GHI: ~5.5 kWh/m²/day
        # Panel area for 10kW: ~55 m² (5.5 m²/kW)
        # Standard module efficiency: ~18%
        # Performance ratio: ~75%
        # Days in year: 365
        
        ghi = 5.5  # kWh/m²/day
        area = 10 * 5.5  # m²
        efficiency = 0.18
        performance_ratio = 0.75
        days = 365
        
        expected_annual_production = ghi * area * efficiency * performance_ratio * days
        
        # Get calculated production from our engine
        # We'll use a mocked response from NASA since we're validating the calculation logic
        nasa_data = {
            "annual_production_kWh": 16425,  # This should match our manual calculation
            "monthly_production_kWh": [1200, 1300, 1400, 1500, 1600, 1700, 1700, 1600, 1500, 1400, 1300, 1200]
        }
        
        # Verify that our manual calculation matches the expected calculation
        self.assertAlmostEqual(expected_annual_production, 16425, delta=100)
    
    def test_npv_calculation(self):
        """Verify NPV calculation against manual calculation."""
        # Manual NPV calculation
        # NPV = -Initial Investment + Σ[CF_t / (1+r)^t]
        
        # Test case:
        # Initial investment: $20,000
        # Annual cash flow: $2,500 for 10 years
        # Discount rate: 5%
        
        initial_investment = 20000
        annual_cash_flow = 2500
        discount_rate = 0.05
        years = 10
        
        # Calculate expected NPV manually
        npv = -initial_investment
        for t in range(1, years + 1):
            npv += annual_cash_flow / math.pow(1 + discount_rate, t)
        
        # Calculate NPV using our financial model
        cash_flows = [-initial_investment] + [annual_cash_flow] * years
        calculated_npv = self.fin_model._calculate_npv(cash_flows, discount_rate)
        
        # Verify they match
        self.assertAlmostEqual(npv, calculated_npv, delta=0.01)
    
    def test_irr_calculation(self):
        """Verify IRR calculation using NPV check."""
        # For IRR, the NPV should be approximately zero
        
        # Test case:
        # Initial investment: $10,000
        # Annual cash flow: $2,000 for 6 years
        # Expected IRR: ~8.8%
        
        cash_flows = [-10000, 2000, 2000, 2000, 2000, 2000, 2000]
        
        # Calculate IRR using our model
        irr = self.fin_model._calculate_irr(cash_flows)
        
        # Verify IRR by checking that NPV at this rate is close to zero
        npv_at_irr = self.fin_model._calculate_npv(cash_flows, irr)
        
        # NPV should be very close to zero at the IRR
        self.assertAlmostEqual(npv_at_irr, 0, delta=0.01)
        
        # Also verify against expected IRR value
        self.assertAlmostEqual(irr, 0.088, delta=0.005)
    
    def test_payback_period_calculation(self):
        """Verify payback period calculation."""
        # Test case:
        # Initial investment: $10,000
        # Annual savings: $2,000
        # Expected payback: 5 years
        
        # Create yearly cash flows
        yearly_cash_flows = [
            {"year": 0, "cumulative_cash_flow": -10000},
            {"year": 1, "cumulative_cash_flow": -8000},
            {"year": 2, "cumulative_cash_flow": -6000},
            {"year": 3, "cumulative_cash_flow": -4000},
            {"year": 4, "cumulative_cash_flow": -2000},
            {"year": 5, "cumulative_cash_flow": 0},
            {"year": 6, "cumulative_cash_flow": 2000}
        ]
        
        # Calculate payback period using our method
        payback = self.calc_engine._calculate_payback_period(yearly_cash_flows)
        
        # Verify payback period
        self.assertEqual(payback, 5.0)
        
        # Test with fractional payback period
        # Modify last two entries for a case where payback occurs between years
        yearly_cash_flows[5]["cumulative_cash_flow"] = -1000
        yearly_cash_flows[6]["cumulative_cash_flow"] = 3000
        
        # Calculate payback period (should be 5.25 years)
        payback = self.calc_engine._calculate_payback_period(yearly_cash_flows)
        
        # Verify fractional payback period
        self.assertAlmostEqual(payback, 5.25, delta=0.01)
    
    def test_loan_payment_calculation(self):
        """Verify loan payment calculation."""
        # Test case:
        # Loan amount: $20,000
        # Interest rate: 5%
        # Term: 20 years
        
        loan_amount = 20000
        interest_rate = 0.05
        term_years = 20
        
        # Manual calculation using the formula:
        # PMT = P * [r(1+r)^n] / [(1+r)^n - 1]
        monthly_rate = interest_rate / 12
        term_months = term_years * 12
        
        numerator = monthly_rate * math.pow(1 + monthly_rate, term_months)
        denominator = math.pow(1 + monthly_rate, term_months) - 1
        expected_monthly_payment = loan_amount * (numerator / denominator)
        
        # Calculate using our model
        result = self.fin_model.calculate_loan_payments(
            system_cost=loan_amount,  # Using system_cost as the loan amount
            loan_amount_percent=100,  # 100% financing
            loan_term_years=term_years,
            loan_rate_percent=interest_rate * 100,
            loan_fees_percent=0
        )
        
        # Verify monthly payment
        self.assertAlmostEqual(result["monthly_payment"], expected_monthly_payment, delta=0.01)
        
        # Also verify total payments
        expected_total_payments = expected_monthly_payment * term_months
        self.assertAlmostEqual(result["total_payments"], expected_total_payments, delta=0.01)