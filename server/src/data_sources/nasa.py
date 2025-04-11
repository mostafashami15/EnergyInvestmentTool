"""
NASA POWER API interface module.

This module provides functions to access NASA's POWER (Prediction of Worldwide Energy Resource) API
for solar and meteorological data at hourly, daily, monthly, and climatology time scales.
"""
import requests
from typing import Dict, Any, List, Optional
import json

class NASAPowerDataSource:
    """Class for interacting with NASA POWER API."""
    
    def __init__(self):
        """Initialize with the base URLs for different endpoints."""
        self.hourly_url = "https://power.larc.nasa.gov/api/temporal/hourly/point"
        self.daily_url = "https://power.larc.nasa.gov/api/temporal/daily/point"
        self.monthly_url = "https://power.larc.nasa.gov/api/temporal/monthly/point"
        self.climatology_url = "https://power.larc.nasa.gov/api/temporal/climatology/point"
    
    def get_hourly_data(self, 
                      lat: float, 
                      lon: float, 
                      start_date: str, 
                      end_date: str,
                      parameters: Optional[List[str]] = None) -> Dict[str, Any]:
        """Get hourly solar radiation and related meteorological data.
        
        Args:
            lat: Latitude
            lon: Longitude
            start_date: Start date in format YYYYMMDD
            end_date: End date in format YYYYMMDD
            parameters: List of parameters to retrieve (defaults to common solar parameters)
            
        Returns:
            Dictionary containing NASA POWER data
        """
        if parameters is None:
            # Default solar-related parameters
            parameters = [
                "ALLSKY_SFC_SW_DWN",  # All Sky Surface Shortwave Downward Irradiance (W/m^2)
                "T2M",                # Temperature at 2 Meters (°C)
                "RH2M",               # Relative Humidity at 2 Meters (%)
                "WS10M"               # Wind Speed at 10 Meters (m/s)
            ]
        
        params = {
            "parameters": ",".join(parameters),
            "community": "RE",  # Renewable Energy community
            "longitude": lon,
            "latitude": lat,
            "start": start_date,
            "end": end_date,
            "format": "JSON"
        }
        
        response = requests.get(self.hourly_url, params=params)
        response.raise_for_status()
        return response.json()
    
    def get_solar_data(self, 
                      lat: float, 
                      lon: float, 
                      start_date: str, 
                      end_date: str,
                      parameters: Optional[List[str]] = None) -> Dict[str, Any]:
        """Get daily solar radiation and related meteorological data.
        
        Args:
            lat: Latitude
            lon: Longitude
            start_date: Start date in format YYYYMMDD
            end_date: End date in format YYYYMMDD
            parameters: List of parameters to retrieve (defaults to common solar parameters)
            
        Returns:
            Dictionary containing NASA POWER data
        """
        if parameters is None:
            # Default solar-related parameters
            parameters = [
                "ALLSKY_SFC_SW_DWN",  # All Sky Surface Shortwave Downward Irradiance (W/m^2)
                "ALLSKY_SFC_SW_DNI",  # Direct Normal Irradiance (W/m^2)
                "ALLSKY_SFC_SW_DIFF", # Diffuse Irradiance (W/m^2)
                "T2M",                # Temperature at 2 Meters (°C)
                "WS10M",              # Wind Speed at 10 Meters (m/s)
                "RH2M"                # Relative Humidity at 2 Meters (%)
            ]
        
        params = {
            "parameters": ",".join(parameters),
            "community": "RE",  # Renewable Energy community
            "longitude": lon,
            "latitude": lat,
            "start": start_date,
            "end": end_date,
            "format": "JSON"
        }
        
        response = requests.get(self.daily_url, params=params)
        response.raise_for_status()
        return response.json()
    
    def get_monthly_data(self, 
                        lat: float, 
                        lon: float, 
                        start_date: str, 
                        end_date: str,
                        parameters: Optional[List[str]] = None) -> Dict[str, Any]:
        """Get monthly average data.
        
        Args:
            lat: Latitude
            lon: Longitude
            start_date: Start date in format YYYYMM
            end_date: End date in format YYYYMM
            parameters: List of parameters to retrieve (defaults to common solar parameters)
            
        Returns:
            Dictionary containing NASA POWER data
        """
        if parameters is None:
            # Default solar-related parameters
            parameters = [
                "ALLSKY_SFC_SW_DWN",  # All Sky Surface Shortwave Downward Irradiance (W/m^2)
                "ALLSKY_SFC_SW_DNI",  # Direct Normal Irradiance (W/m^2)
                "T2M",                # Temperature at 2 Meters (°C)
                "WS10M"               # Wind Speed at 10 Meters (m/s)
            ]
        
        params = {
            "parameters": ",".join(parameters),
            "community": "RE",  # Renewable Energy community
            "longitude": lon,
            "latitude": lat,
            "start": start_date,
            "end": end_date,
            "format": "JSON"
        }
        
        response = requests.get(self.monthly_url, params=params)
        response.raise_for_status()
        return response.json()
    
    def get_monthly_climatology(self, 
                               lat: float, 
                               lon: float, 
                               parameters: Optional[List[str]] = None) -> Dict[str, Any]:
        """Get monthly climatology data (long-term averages).
        
        Args:
            lat: Latitude
            lon: Longitude
            parameters: List of parameters to retrieve (defaults to common solar parameters)
            
        Returns:
            Dictionary containing monthly averages
        """
        if parameters is None:
            # Default solar-related parameters
            parameters = [
                "ALLSKY_SFC_SW_DWN",  # All Sky Surface Shortwave Downward Irradiance (W/m^2)
                "ALLSKY_SFC_SW_DNI",  # Direct Normal Irradiance (W/m^2)
                "T2M",                # Temperature at 2 Meters (°C)
                "WS10M"               # Wind Speed at 10 Meters (m/s)
            ]
        
        params = {
            "parameters": ",".join(parameters),
            "community": "RE",  # Renewable Energy community
            "longitude": lon,
            "latitude": lat,
            "format": "JSON"
        }
        
        response = requests.get(self.climatology_url, params=params)
        response.raise_for_status()
        return response.json()
    
    def calculate_solar_potential(self, 
                                lat: float, 
                                lon: float,
                                system_capacity: float = 4,
                                efficiency: float = 0.15,
                                performance_ratio: float = 0.75) -> Dict[str, Any]:
        """Calculate potential solar energy production using NASA POWER climatology data.
        
        Args:
            lat: Latitude
            lon: Longitude
            system_capacity: System size in kW (default: 4)
            efficiency: System efficiency (default: 0.15)
            performance_ratio: System performance ratio (default: 0.75)
            
        Returns:
            Dictionary with estimated monthly and annual production
        """
        # Get climatology data
        climate_data = self.get_monthly_climatology(
            lat, lon, ["ALLSKY_SFC_SW_DWN", "T2M"]
        )
        
        # Initialize results
        result = {
            "monthly_production_kWh": [],
            "annual_production_kWh": 0,
            "system_capacity_kW": system_capacity,
            "efficiency": efficiency,
            "performance_ratio": performance_ratio
        }
        
        # Extract the monthly data if available
        try:
            # New structure: data is in properties.parameter.ALLSKY_SFC_SW_DWN with month abbreviations
            radiation_data = climate_data.get("properties", {}).get("parameter", {}).get("ALLSKY_SFC_SW_DWN", {})
            
            # Month names for output and mapping
            month_names = [
                "January", "February", "March", "April", "May", "June",
                "July", "August", "September", "October", "November", "December"
            ]
            
            # Map three-letter abbreviations to month numbers
            month_abbr_map = {
                "JAN": 1, "FEB": 2, "MAR": 3, "APR": 4, "MAY": 5, "JUN": 6,
                "JUL": 7, "AUG": 8, "SEP": 9, "OCT": 10, "NOV": 11, "DEC": 12
            }
            
            monthly_production = []
            annual_total = 0
            
            # Process each month
            for month_abbr, solar_value in radiation_data.items():
                # Skip annual value
                if month_abbr == "ANN":
                    continue
                    
                # Get month number
                month_num = month_abbr_map.get(month_abbr)
                if month_num is None:
                    continue
                    
                # Get month name and days in month
                month_name = month_names[month_num - 1]
                days_in_month = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31][month_num - 1]
                
                # Convert kWh/m^2/day to monthly kWh
                daily_kwh_per_m2 = solar_value
                
                # Solar panel area (approximation based on system capacity)
                # Assuming roughly 5-6 m² per kW
                solar_panel_area = system_capacity * 5.5
                
                # Calculate monthly production
                monthly_kwh = (
                    daily_kwh_per_m2 * days_in_month * 
                    solar_panel_area * efficiency * performance_ratio
                )
                
                monthly_production.append({
                    "month": month_name,
                    "month_num": month_num,
                    "days": days_in_month,
                    "solar_radiation_kwh_per_m2_day": daily_kwh_per_m2,
                    "production_kWh": round(monthly_kwh, 2)
                })
                
                annual_total += monthly_kwh
            
            # Sort by month number
            monthly_production.sort(key=lambda x: x["month_num"])
            
            result["monthly_production_kWh"] = monthly_production
            result["annual_production_kWh"] = round(annual_total, 2)
            
        except Exception as e:
            result["error"] = f"Error calculating solar potential: {str(e)}"
        
        return result
        
