"""
Test script for NASA POWER API.
"""
import sys
import os
from datetime import datetime
import json

# Add the parent directory to the path to import from data_sources
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from data_sources.nasa import NASAPowerDataSource

def test_hourly_data():
    """Test fetching hourly data from NASA POWER API."""
    print("\n===== TESTING NASA POWER HOURLY DATA =====\n")
    
    nasa = NASAPowerDataSource()
    
    # Use historical dates from 2023 (one day only to limit data volume)
    start_str = "20230101"
    end_str = "20230101"  # Just one day of hourly data
    
    print(f"Using date range: {start_str} to {end_str}")
    
    # Test with Denver
    location = {"name": "Denver, CO", "lat": 39.7392, "lon": -104.9903}
    
    try:
        print(f"\nLocation: {location['name']} ({location['lat']}, {location['lon']})")
        
        result = nasa.get_hourly_data(
            lat=location['lat'],
            lon=location['lon'],
            start_date=start_str,
            end_date=end_str,
            parameters=["ALLSKY_SFC_SW_DWN", "T2M"]  # Just get these two parameters
        )
        
        # Extract and print some basic information
        header = result.get('header', {})
        print(f"  Data Source: {header.get('title', 'Unknown')}")
        
        # Get parameters from the response
        parameters = result.get('parameters', {})
        
        # Print solar radiation data if available
        if 'ALLSKY_SFC_SW_DWN' in parameters:
            solar_data = parameters['ALLSKY_SFC_SW_DWN']
            print(f"  Solar Radiation Parameter: {solar_data.get('longname', 'Unknown')}")
            print(f"  Units: {solar_data.get('units', 'Unknown')}")
            
            # Print a few hourly values
            print("\n  Sample Hourly Values:")
            data = result.get('properties', {}).get('parameter', {}).get('ALLSKY_SFC_SW_DWN', {})
            hours = list(data.keys())[:5]  # First 5 hours
            for hour in hours:
                value = data[hour]
                print(f"    {hour}: {value} {solar_data.get('units', '')}")
        else:
            print("\n  Available parameters:", list(parameters.keys()))
            
    except Exception as e:
        print(f"  Error: {e}")
        import traceback
        traceback.print_exc()

def test_daily_data():
    """Test fetching daily data from NASA POWER API."""
    print("\n===== TESTING NASA POWER DAILY DATA =====\n")
    
    nasa = NASAPowerDataSource()
    
    # Use historical dates from 2023
    start_str = "20230101"
    end_str = "20230107"  # One week of data
    
    print(f"Using date range: {start_str} to {end_str}")
    
    # Test with Denver
    location = {"name": "Denver, CO", "lat": 39.7392, "lon": -104.9903}
    
    try:
        print(f"\nLocation: {location['name']} ({location['lat']}, {location['lon']})")
        
        result = nasa.get_solar_data(
            lat=location['lat'],
            lon=location['lon'],
            start_date=start_str,
            end_date=end_str,
            parameters=["ALLSKY_SFC_SW_DWN", "T2M"]
        )
        
        # Extract and print some basic information
        header = result.get('header', {})
        print(f"  Data Source: {header.get('title', 'Unknown')}")
        
        # Get parameters from the response
        parameters = result.get('parameters', {})
        
        # Print solar radiation data if available
        if 'ALLSKY_SFC_SW_DWN' in parameters:
            solar_data = parameters['ALLSKY_SFC_SW_DWN']
            print(f"  Solar Radiation Parameter: {solar_data.get('longname', 'Unknown')}")
            print(f"  Units: {solar_data.get('units', 'Unknown')}")
            
            # Try to find where the data is in the response
            print("\n  Exploring data structure...")
            if 'properties' in result and 'parameter' in result['properties']:
                # For daily data after ~ April 2023
                daily_data = result['properties']['parameter'].get('ALLSKY_SFC_SW_DWN', {})
                if daily_data:
                    print("\n  Sample Daily Values:")
                    days = list(daily_data.keys())[:5]  # First 5 days
                    for day in days:
                        value = daily_data[day]
                        print(f"    {day}: {value} {solar_data.get('units', '')}")
                else:
                    print("  No daily data found in properties.parameter structure")
            else:
                # For older API response structure
                print("  Alternative data structures:")
                print("  Top level keys:", list(result.keys()))
                
                # Print entire response structure for debugging
                print("\n  Full response structure:")
                print(json.dumps(result, indent=2)[:1000] + "...")  # Truncate for readability
        else:
            print("\n  Available parameters:", list(parameters.keys()))
            
    except Exception as e:
        print(f"  Error: {e}")
        import traceback
        traceback.print_exc()

def test_climatology():
    """Test fetching climatology data from NASA POWER API."""
    print("\n===== TESTING NASA POWER CLIMATOLOGY DATA =====\n")
    
    nasa = NASAPowerDataSource()
    
    # Test with Denver
    location = {"name": "Denver, CO", "lat": 39.7392, "lon": -104.9903}
    
    try:
        print(f"\nLocation: {location['name']} ({location['lat']}, {location['lon']})")
        
        result = nasa.get_monthly_climatology(
            lat=location['lat'],
            lon=location['lon']
        )
        
        # Extract and print some basic information
        header = result.get('header', {})
        print(f"  Data Source: {header.get('title', 'Unknown')}")
        
        # Check if data is in the properties.parameter path (new structure)
        if 'properties' in result and 'parameter' in result['properties']:
            solar_data = result['properties']['parameter'].get('ALLSKY_SFC_SW_DWN', {})
            
            if solar_data:
                print("  Solar Radiation Parameter: All Sky Surface Shortwave Downward Irradiance")
                print("  Units: kW-hr/m^2/day")
                
                # Print monthly values
                print("\n  Monthly Average Values:")
                # Skip the annual value
                for month, value in {k: v for k, v in solar_data.items() if k != 'ANN'}.items():
                    print(f"    {month}: {value} kW-hr/m^2/day")
            else:
                print("  No solar radiation data found in properties.parameter structure")
        else:
            # Check alternative data paths
            print("  Data not found in expected structure, checking alternatives...")
            print("  Top level keys:", list(result.keys()))
            
    except Exception as e:
        print(f"  Error: {e}")
        import traceback
        traceback.print_exc()

def test_solar_potential():
    """Test calculating solar potential from NASA POWER data."""
    print("\n===== TESTING NASA POWER SOLAR POTENTIAL CALCULATION =====\n")
    
    nasa = NASAPowerDataSource()
    
    # Test with Denver
    location = {"name": "Denver, CO", "lat": 39.7392, "lon": -104.9903}
    
    # Test one system capacity
    capacity = 10  # kW
    
    try:
        print(f"\nLocation: {location['name']} ({location['lat']}, {location['lon']})")
        print(f"System Capacity: {capacity} kW")
        
        result = nasa.calculate_solar_potential(
            lat=location['lat'],
            lon=location['lon'],
            system_capacity=capacity
        )
        
        # Print annual potential
        annual = result.get('annual_production_kWh', 0)
        print(f"Annual Production Estimate: {annual:.2f} kWh")
        print(f"kWh per kW: {annual/capacity:.2f}")
        
        # Print error if present
        if 'error' in result:
            print(f"Error: {result['error']}")
        
        # Print all monthly data
        print("\nMonthly Production:")
        monthly_data = result.get('monthly_production_kWh', [])
        
        for month_data in monthly_data:
            print(f"  {month_data['month']}: {month_data['production_kWh']:.2f} kWh")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # Run all tests
    print("Starting NASA POWER API tests...")
    
    try:
        # Run tests from simplest to most complex
        test_daily_data()
        test_hourly_data()  # New hourly data test
        test_climatology()
        test_solar_potential()
        
        print("\nAll NASA POWER tests completed!")
        
    except Exception as e:
        print(f"Error running tests: {e}")
        import traceback
        traceback.print_exc()