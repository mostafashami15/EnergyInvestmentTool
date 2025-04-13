# tests/conftest.py
import pytest
from unittest.mock import MagicMock

@pytest.fixture
def mock_nrel_data():
    """Fixture providing mock NREL API response data."""
    return {
        "outputs": {
            "ac_annual": 15000,
            "capacity_factor": 18.5,
            "ac_monthly": [1000, 1100, 1300, 1400, 1500, 1600, 1600, 1500, 1400, 1300, 1100, 1000]
        }
    }

@pytest.fixture
def mock_nasa_data():
    """Fixture providing mock NASA API response data."""
    return {
        "annual_production_kWh": 12000,
        "monthly_production_kWh": [
            {"month": "January", "production_kWh": 800},
            {"month": "February", "production_kWh": 900},
            # ... other months
        ]
    }

@pytest.fixture
def calculation_engine():
    """Fixture providing a calculation engine instance with mocked API clients."""
    from server.src.calculation_engine import CalculationEngine
    from server.src.data_sources.nrel import NRELDataSource
    from server.src.data_sources.nasa import NASAPowerDataSource
    
    # Create the calculation engine
    engine = CalculationEngine()
    
    # Replace the API clients with mocks
    engine.nrel = MagicMock(spec=NRELDataSource)
    engine.nasa = MagicMock(spec=NASAPowerDataSource)
    
    return engine