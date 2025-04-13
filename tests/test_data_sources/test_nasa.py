# tests/test_data_sources/test_nasa.py
import unittest
from unittest.mock import patch, MagicMock
import requests
from server.src.data_sources.nasa import NASAPowerDataSource

class TestNASAPowerDataSource(unittest.TestCase):
    def setUp(self):
        self.nasa = NASAPowerDataSource()
        
    @patch('requests.get')
    def test_get_solar_data(self, mock_get):
        # Mock response from NASA API
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "properties": {
                "parameter": {
                    "ALLSKY_SFC_SW_DWN": {
                        "JAN": 4.5,
                        "FEB": 5.1,
                        "MAR": 5.8,
                        "APR": 6.2,
                        "MAY": 6.5,
                        "JUN": 7.0,
                        "JUL": 7.1,
                        "AUG": 6.8,
                        "SEP": 6.0,
                        "OCT": 5.5,
                        "NOV": 4.8,
                        "DEC": 4.2,
                        "ANN": 5.8
                    }
                }
            }
        }
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response
        
        # Call the method
        result = self.nasa.get_solar_data(
            lat=39.7392, 
            lon=-104.9903, 
            start_date="20230101", 
            end_date="20231231"
        )
        
        # Verify the request was made correctly
        mock_get.assert_called_once()
        args, kwargs = mock_get.call_args
        self.assertEqual(args[0], self.nasa.daily_url)
        self.assertEqual(kwargs['params']['latitude'], 39.7392)
        self.assertEqual(kwargs['params']['longitude'], -104.9903)
        
        # Verify the result was processed correctly
        self.assertEqual(result, mock_response.json())
        
    @patch('requests.get')
    def test_calculate_solar_potential(self, mock_get):
        # Mock response from NASA API
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "properties": {
                "parameter": {
                    "ALLSKY_SFC_SW_DWN": {
                        "JAN": 4.5,
                        "FEB": 5.1,
                        "MAR": 5.8,
                        "APR": 6.2,
                        "MAY": 6.5,
                        "JUN": 7.0,
                        "JUL": 7.1,
                        "AUG": 6.8,
                        "SEP": 6.0,
                        "OCT": 5.5,
                        "NOV": 4.8,
                        "DEC": 4.2,
                        "ANN": 5.8
                    },
                    "T2M": {
                        "JAN": 0.5,
                        "FEB": 2.1,
                        "MAR": 5.8,
                        "APR": 11.2,
                        "MAY": 16.5,
                        "JUN": 22.0,
                        "JUL": 25.1,
                        "AUG": 24.8,
                        "SEP": 19.0,
                        "OCT": 12.5,
                        "NOV": 6.8,
                        "DEC": 1.2,
                        "ANN": 12.3
                    }
                }
            }
        }
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response
        
        # Call the method
        result = self.nasa.calculate_solar_potential(
            lat=39.7392, 
            lon=-104.9903,
            system_capacity=10,
            efficiency=0.15,
            performance_ratio=0.75
        )
        
        # Verify the request was made correctly
        mock_get.assert_called_once()
        
        # Verify the result structure
        self.assertIn("monthly_production_kWh", result)
        self.assertIn("annual_production_kWh", result)
        self.assertEqual(result["system_capacity_kW"], 10)
        self.assertEqual(result["efficiency"], 0.15)
        self.assertEqual(result["performance_ratio"], 0.75)
        
        # Verify the annual production is the sum of monthly values
        monthly_total = sum(month["production_kWh"] for month in result["monthly_production_kWh"])
        self.assertAlmostEqual(result["annual_production_kWh"], monthly_total, delta=1.0)