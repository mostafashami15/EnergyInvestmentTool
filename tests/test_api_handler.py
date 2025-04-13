# tests/test_api_handler.py
import unittest
import json
from unittest.mock import patch, MagicMock
from server.src.api_handler import app
from server.src.calculation_engine import CalculationEngine
from server.src.financial_modeling import FinancialModel

class TestAPIHandler(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
        
    def test_health_endpoint(self):
        response = self.app.get('/api/health')
        data = json.loads(response.data)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['status'], 'healthy')
        
    @patch.object(CalculationEngine, 'calculate_solar_production')
    def test_calculate_production_endpoint(self, mock_calculate):
        # Mock the calculate_solar_production method
        mock_calculate.return_value = {
            "nrel": {"annual_production_kwh": 15000},
            "nasa": {"annual_production_kwh": 12000}
        }
        
        # Test API endpoint
        request_data = {
            "latitude": 39.7392,
            "longitude": -104.9903,
            "systemCapacity": 10.0,
            "moduleType": 1,
            "arrayType": 2,
            "losses": 14.0,
            "tilt": 20.0,
            "azimuth": 180.0,
            "dataSource": "both"
        }
        
        response = self.app.post(
            '/api/calculate-production',
            data=json.dumps(request_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn("nrel", data)
        self.assertIn("nasa", data)

    def test_utility_rates_endpoint(self):
        # Mock the get_utility_rates method
        with patch.object(CalculationEngine, 'get_utility_rates') as mock_utility_rates:
            mock_utility_rates.return_value = {
                "residential_rate": 0.12,
                "commercial_rate": 0.10,
                "utility_name": "Test Utility"
            }
            
            # Test API endpoint
            response = self.app.get('/api/utility-rates?lat=39.7392&lon=-104.9903')
            
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.data)
            self.assertEqual(data["residential_rate"], 0.12)