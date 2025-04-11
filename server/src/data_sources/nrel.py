# server/src/data_sources/nrel.py
"""
NREL (National Renewable Energy Laboratory) API interface module.

This module provides functions to access various NREL APIs for renewable energy data.
"""
import requests
from typing import Dict, Any, Optional
import sys
import os

# Add the parent directory to the path to import config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

class NRELDataSource:
    """Class for interacting with NREL APIs."""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize with API key."""
        self.api_key = api_key or config.NREL_API_KEY
        self.base_url = "https://developer.nrel.gov/api"
    
    def get_solar_resource(self, lat: float, lon: float) -> Dict[str, Any]:
        """Get solar resource data for a specific location.
        
        Args:
            lat: Latitude
            lon: Longitude
            
        Returns:
            Dictionary containing solar resource data
        """
        url = f"{self.base_url}/solar/solar_resource/v1.json"
        params = {
            "api_key": self.api_key,
            "lat": lat,
            "lon": lon
        }
        
        response = requests.get(url, params=params)
        response.raise_for_status()  # Raise exception for HTTP errors
        return response.json()
    
    def get_pvwatts(self, 
                   lat: float, 
                   lon: float,
                   system_capacity: float = 4,
                   module_type: int = 1,
                   losses: float = 14,
                   array_type: int = 1,
                   tilt: float = 20,
                   azimuth: float = 180) -> Dict[str, Any]:
        """Calculate solar PV energy production using NREL's PVWatts API.
        
        Args:
            lat: Latitude
            lon: Longitude
            system_capacity: System size in kW (default: 4)
            module_type: Module type (1=standard, 2=premium, 3=thin film)
            losses: System losses in % (default: 14)
            array_type: Array type (1=fixed open rack, 2=fixed roof mount, 3=1-axis tracking, 
                                  4=1-axis backtracking, 5=2-axis tracking)
            tilt: Array tilt in degrees (default: 20)
            azimuth: Array azimuth in degrees (default: 180 - south-facing)
            
        Returns:
            Dictionary containing PVWatts calculation results
        """
        url = f"{self.base_url}/pvwatts/v6.json"
        params = {
            "api_key": self.api_key,
            "lat": lat,
            "lon": lon,
            "system_capacity": system_capacity,
            "module_type": module_type,
            "losses": losses,
            "array_type": array_type,
            "tilt": tilt,
            "azimuth": azimuth
        }
        
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    
    def get_utility_rates(self, lat: float, lon: float, radius: float = 0) -> Dict[str, Any]:
        """Get utility rate data for a specific location.
        
        Args:
            lat: Latitude
            lon: Longitude
            radius: Radius in miles to search (default: 0)
                
        Returns:
            Dictionary containing utility rate data
        """
        url = f"{self.base_url}/utility_rates/v3.json"
        params = {
            "api_key": self.api_key,
            "lat": lat,
            "lon": lon,
            "radius": radius
        }
        
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    
    def get_wind_resource(self, lat: float, lon: float) -> Dict[str, Any]:
        """Get wind resource data from the Wind Toolkit.
        
        Args:
            lat: Latitude
            lon: Longitude
            
        Returns:
            Dictionary containing wind resource data
        """
        url = f"{self.base_url}/wind-toolkit/v2/wind/wtk-download"
        params = {
            "api_key": self.api_key,
            "lat": lat,
            "lon": lon,
            "attributes": "windspeed_80m,windspeed_100m,winddirection_100m",
            "names": f"lat{lat}_lon{lon}",
            "email": "youremail@example.com"  # Required for this API
        }
        
        # Note: This endpoint initiates an asynchronous download
        # For actual implementation, you'll need to handle the email response
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    
    def get_energy_incentives(self, address: str) -> Dict[str, Any]:
        """Get energy incentives and policies from DSIRE API.
        
        Args:
            address: Address string (e.g., "123 Main St, Denver, CO")
            
        Returns:
            Dictionary containing incentives data
        """
        url = f"{self.base_url}/energy_incentives/v2.json"
        params = {
            "api_key": self.api_key,
            "address": address
        }
        
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()


# Example usage
if __name__ == "__main__":
    # Create an instance of the data source
    nrel = NRELDataSource()
    
    # Test with Denver, CO coordinates
    lat, lon = 39.7392, -104.9903
    
    # Get solar resource data
    try:
        solar_data = nrel.get_solar_resource(lat, lon)
        print("Solar Resource Data:")
        print(solar_data)
        print("\n" + "-"*50 + "\n")
    except Exception as e:
        print(f"Error fetching solar resource data: {e}")
    
    # Get PVWatts calculation
    try:
        pvwatts_data = nrel.get_pvwatts(lat, lon)
        print("PVWatts Data:")
        print(f"Annual AC Energy: {pvwatts_data['outputs']['ac_annual']} kWh")
        print(f"Capacity Factor: {pvwatts_data['outputs']['capacity_factor']}%")
        print("\n" + "-"*50 + "\n")
    except Exception as e:
        print(f"Error fetching PVWatts data: {e}")
    
    # Get utility rates
    try:
        utility_data = nrel.get_utility_rates(lat, lon)
        print("Utility Rate Data:")
        print(utility_data)
    except Exception as e:
        print(f"Error fetching utility rate data: {e}")