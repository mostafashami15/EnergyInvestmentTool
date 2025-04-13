# tests/test_calculation_engine.py
import unittest
from unittest.mock import patch, MagicMock
import json
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from server.src.calculation_engine import CalculationEngine

class TestCalculationEngine(unittest.TestCase):
    def setUp(self):
        self.engine = CalculationEngine()
        
    @patch('server.src.data_sources.nrel.NRELDataSource.get_pvwatts')
    @patch('server.src.data_sources.nasa.NASAPowerDataSource.calculate_solar_potential')
    def test_calculate_solar_production(self, mock_nasa, mock_nrel):
        # Mock NREL response
        mock_nrel.return_value = {
            "outputs": {
                "ac_annual": 15000,
                "capacity_factor": 18.5,
                "ac_monthly": [1000, 1100, 1300, 1400, 1500, 1600, 1600, 1500, 1400, 1300, 1100, 1000]
            }
        }
        
        # Mock NASA response
        mock_nasa.return_value = {
            "annual_production_kWh": 12000,
            "monthly_production_kWh": [
                {"month": "January", "production_kWh": 800},
                {"month": "February", "production_kWh": 900},
                # ... other months
            ]
        }
        
        # Test with both data sources
        result = self.engine.calculate_solar_production(
            lat=39.7392, lon=-104.9903, system_capacity=10,
            module_type=1, losses=14, array_type=2, 
            tilt=20, azimuth=180, data_source="both"
        )
        
        # Verify the calculation results
        self.assertEqual(result["nrel"]["annual_production_kwh"], 15000)
        self.assertEqual(result["nasa"]["annual_production_kwh"], 12000)
        self.assertIn("comparison", result)
        self.assertEqual(result["comparison"]["percent_difference"], 25.0)  # (15000-12000)/12000*100
        
    def test_financial_metrics_calculation(self):
        # Test financial calculations with known values
        production_data = {
            "system_parameters": {
                "capacity_kw": 10,  # Assuming a 10kW system
                "module_type": 1,
                "losses_percent": 14,
                "array_type": 2,
                "tilt_degrees": 20,
                "azimuth_degrees": 180
            },
            "nrel": {"annual_production_kwh": 15000},
            "nasa": {"annual_production_kwh": 12000},
            "comparison": {"average_production_kwh": 13500}
        }
        
        # Update utility_rates to match the structure expected by the function
        utility_rates = {
            "residential_rate": 0.12
        }
        
        result = self.engine.calculate_financial_metrics(
            production_data, utility_rates, system_cost_per_watt=2.80,
            incentive_percent=30, incentive_fixed=0, discount_rate=0.04,
            electricity_inflation=0.025, analysis_period_years=25,
            maintenance_cost_per_kw_year=20, include_sensitivity=False
        )
        
        # Verify key financial metrics
        self.assertIn("financial_metrics", result)
        self.assertIn("payback_period_years", result["financial_metrics"])
        self.assertIn("roi_percent", result["financial_metrics"])
        self.assertIn("npv", result["financial_metrics"])
        self.assertIn("irr_percent", result["financial_metrics"])
        
        # Test with specific expected values
        # System cost: 10,000W * $2.80/W = $28,000
        # Net cost after 30% incentive: $28,000 * 0.7 = $19,600
        # Annual savings: 13,500 kWh * $0.12/kWh = $1,620
        # Simple payback: $19,600 / $1,620 = ~12.1 years
        expected_simple_payback = 19600 / 1620
        self.assertAlmostEqual(result["financial_metrics"]["payback_period_years"], 
                            expected_simple_payback, delta=1.0)