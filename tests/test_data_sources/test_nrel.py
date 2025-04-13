# tests/test_data_sources/test_nrel.py
import unittest
from unittest.mock import patch, MagicMock
from server.src.data_sources.nrel import NRELDataSource

class TestNRELDataSource(unittest.TestCase):
    def setUp(self):
        self.nrel = NRELDataSource()
        
    @patch('requests.get')
    def test_get_solar_resource(self, mock_get):
        # Mock response
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "inputs": {
                "lat": 39.7392,
                "lon": -104.9903
            },
            "outputs": {
                "avg_dni": {"annual": 6.32},
                "avg_ghi": {"annual": 5.21}
            }
        }
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response
        
        # Call method
        result = self.nrel.get_solar_resource(39.7392, -104.9903)
        
        # Verify request
        mock_get.assert_called_once()
        args, kwargs = mock_get.call_args
        self.assertTrue('developer.nrel.gov/api/solar/solar_resource' in args[0])
        self.assertEqual(kwargs['params']['lat'], 39.7392)
        
        # Verify result
        self.assertEqual(result, mock_response.json())