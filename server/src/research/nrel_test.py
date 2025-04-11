# erver/src/research/nrel_test.py
"""
Test script for NREL APIs.

This script tests various NREL APIs to understand their functionality
and explore available data for the Energy Investment Decision Support System.
"""
import requests
import json
import sys
import os

# Add the parent directory to the path to import from data_sources
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from data_sources.nrel import NRELDataSource

def test_pvwatts():
    """Test the PVWatts API with different parameters."""
    print("\n===== TESTING PVWATTS API =====\n")
    
    nrel = NRELDataSource()
    
    # Test locations
    locations = [
        {"name": "Denver, CO", "lat": 39.7392, "lon": -104.9903},
        {"name": "Phoenix, AZ", "lat": 33.4484, "lon": -112.0740},
        {"name": "Seattle, WA", "lat": 47.6062, "lon": -122.3321}
    ]
    
    # System capacities to test
    capacities = [4, 10, 20]  # kW
    
    for location in locations:
        print(f"\nLocation: {location['name']} ({location['lat']}, {location['lon']})")
        
        for capacity in capacities:
            try:
                print(f"\n  System Capacity: {capacity} kW")
                result = nrel.get_pvwatts(
                    lat=location['lat'],
                    lon=location['lon'],
                    system_capacity=capacity
                )
                
                # Extract key results
                annual_kwh = result['outputs']['ac_annual']
                capacity_factor = result['outputs']['capacity_factor']
                
                print(f"  Annual Production: {annual_kwh:.2f} kWh")
                print(f"  Capacity Factor: {capacity_factor:.2f}%")
                print(f"  kWh per kW: {annual_kwh/capacity:.2f}")
                
                # Sample monthly data
                print(f"  Monthly Production (kWh):")
                monthly = result['outputs']['ac_monthly']
                for i, month in enumerate(monthly):
                    month_name = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", 
                                  "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"][i]
                    print(f"    {month_name}: {month:.2f}")
                
            except Exception as e:
                print(f"  Error: {e}")
    
    # Test different tilt angles for Denver
    print("\n\nTesting different tilt angles for Denver, CO:")
    tilts = [0, 10, 20, 30, 40]
    lat, lon = 39.7392, -104.9903
    
    for tilt in tilts:
        try:
            print(f"\n  Tilt: {tilt} degrees")
            result = nrel.get_pvwatts(
                lat=lat,
                lon=lon,
                system_capacity=10,
                tilt=tilt
            )
            
            annual_kwh = result['outputs']['ac_annual']
            print(f"  Annual Production: {annual_kwh:.2f} kWh")
            
        except Exception as e:
            print(f"  Error: {e}")

def test_solar_resource():
    """Test the Solar Resource Data API."""
    print("\n===== TESTING SOLAR RESOURCE API =====\n")
    
    nrel = NRELDataSource()
    
    # Test locations
    locations = [
        {"name": "Denver, CO", "lat": 39.7392, "lon": -104.9903},
        {"name": "Phoenix, AZ", "lat": 33.4484, "lon": -112.0740},
        {"name": "Seattle, WA", "lat": 47.6062, "lon": -122.3321}
    ]
    
    for location in locations:
        try:
            print(f"\nLocation: {location['name']} ({location['lat']}, {location['lon']})")
            result = nrel.get_solar_resource(
                lat=location['lat'],
                lon=location['lon']
            )
            
            # Extract and display key data
            avg_dni = result['outputs']['avg_dni']['annual']
            avg_ghi = result['outputs']['avg_ghi']['annual']
            avg_lat_tilt = result['outputs']['avg_lat_tilt']['annual']
            
            print(f"  Annual Average DNI: {avg_dni} kWh/m²/day")
            print(f"  Annual Average GHI: {avg_ghi} kWh/m²/day")
            print(f"  Annual Average at Latitude Tilt: {avg_lat_tilt} kWh/m²/day")
            
            # Monthly data for GHI
            print(f"\n  Monthly GHI (kWh/m²/day):")
            monthly = result['outputs']['avg_ghi']['monthly']
            for month, value in monthly.items():
                print(f"    {month}: {value}")
                
        except Exception as e:
            print(f"  Error: {e}")

def test_utility_rates():
    """Test the Utility Rates API."""
    print("\n===== TESTING UTILITY RATES API =====\n")
    
    nrel = NRELDataSource()
    
    # Test locations with coordinates
    locations = [
        {"name": "Denver, CO", "lat": 39.7392, "lon": -104.9903},
        {"name": "Phoenix, AZ", "lat": 33.4484, "lon": -112.0740},
        {"name": "Seattle, WA", "lat": 47.6062, "lon": -122.3321}
    ]
    
    for location in locations:
        try:
            print(f"\nLocation: {location['name']} ({location['lat']}, {location['lon']})")
            result = nrel.get_utility_rates(
                lat=location['lat'],
                lon=location['lon']
            )
            
            # Extract and display key data
            utility = result['outputs']['utility_name']
            rate_residential = result['outputs']['residential']
            rate_commercial = result['outputs']['commercial']
            
            print(f"  Utility: {utility}")
            print(f"  Residential Rate: {rate_residential} $/kWh")
            print(f"  Commercial Rate: {rate_commercial} $/kWh")
                
        except Exception as e:
            print(f"  Error: {e}")

if __name__ == "__main__":
    # Run all tests
    print("Starting NREL API tests...")
    
    try:
        test_pvwatts()
        test_solar_resource()
        test_utility_rates()
        
        print("\nAll tests completed!")
        
    except Exception as e:
        print(f"Error running tests: {e}")
        import traceback
        traceback.print_exc()