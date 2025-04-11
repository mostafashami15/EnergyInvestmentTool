# NREL API Research Notes

## API Overview
The National Renewable Energy Laboratory (NREL) provides several APIs that are valuable for our Energy Investment Decision Support System. We have successfully integrated and tested these APIs.

**API Key:** `Zr6gLeUtWfgvxP1cVBZJBTWczSwbdAFxKiyDMaUQ`

## Key APIs Implemented

### 1. PVWatts API (v6)
**Endpoint:** `https://developer.nrel.gov/api/pvwatts/v6.json`

**Purpose:** Estimates the energy production of grid-connected photovoltaic systems.

**Key Parameters:**
- `lat` & `lon`: Location coordinates
- `system_capacity`: System size in kW
- `module_type`: Type of module (1=standard, 2=premium, 3=thin film)
- `losses`: System losses percentage (default: 14)
- `array_type`: Mounting configuration (1=fixed open rack, 2=fixed roof mount, etc.)
- `tilt`: Array tilt angle in degrees
- `azimuth`: Array azimuth angle in degrees (180=south-facing)

**Example Response Data:**
```json
{
  "inputs": {...},
  "outputs": {
    "ac_monthly": [527.19, 525.76, 639.82, ...],  // Monthly AC energy production (kWh)
    "dc_monthly": [553.31, 557.43, 680.50, ...],  // Monthly DC energy production (kWh)
    "ac_annual": 7011.83,                         // Annual AC energy production (kWh)
    "solrad_monthly": [4.97, 5.57, 6.27, ...],    // Monthly solar radiation (kWh/m2/day)
    "solrad_annual": 5.93,                        // Annual solar radiation (kWh/m2/day)
    "capacity_factor": 20.01                      // System capacity factor (%)
  }
}
```

**Test Results:**
- Successfully tested with multiple locations (Denver, Phoenix, Seattle)
- Production values range from 1,107-1,749 kWh/kW depending on location
- Tilt angle significantly impacts production (optimal ~40° for Denver)
- System size scales linearly with production

**Use in Project:**
- Core calculation engine for solar energy production
- Financial projections based on energy estimates
- System configuration recommendations

### 2. Solar Resource Data API
**Endpoint:** `https://developer.nrel.gov/api/solar/solar_resource/v1.json`

**Purpose:** Provides solar resource data for a specific location.

**Key Parameters:**
- `lat` & `lon`: Location coordinates

**Data Provided:**
- Monthly average global horizontal irradiance (GHI)
- Monthly average direct normal irradiance (DNI)
- Monthly average diffuse horizontal irradiance (DHI)

**Test Results:**
- Successfully tested with multiple locations
- GHI values match NASA data closely (4.83 kWh/m²/day for Denver)
- Significant regional variation (3.46-5.78 kWh/m²/day)
- Seasonal patterns are clearly visible in monthly data

**Use in Project:**
- Initial solar potential assessment
- Compare locations for solar suitability
- Input to other calculation engines

### 3. Utility Rates API (v3)
**Endpoint:** `https://developer.nrel.gov/api/utility_rates/v3.json`

**Purpose:** Provides utility rate data for a specific location.

**Key Parameters:**
- `lat` & `lon`: Location coordinates (requires these formats, not address)
- `radius`: Optional radius in miles (default: 0)

**Data Provided:**
- Utility company information
- Commercial and residential electricity rates
- Net metering policies

**Test Results:**
- Successfully tested with multiple locations
- Rates vary significantly by region (7.8¢-12.0¢/kWh)
- Initial tests with address parameter failed (422 error)
- Modified to use lat/lon parameters successfully

**Use in Project:**
- Financial calculations for ROI
- Payback period estimation
- Input to economic models

### 4. DSIRE Energy Incentives API
**Endpoint:** `https://developer.nrel.gov/api/energy_incentives/v2.json`

**Purpose:** Provides information on renewable energy incentives and policies.

**Key Parameters:**
- `address`: String address (e.g., "Denver, CO")

**Data Provided:**
- Available tax credits and rebates
- Renewable energy policies
- State and federal incentives

**Status:** Not fully tested yet - scheduled for next phase

**Use in Project:**
- Financial calculations for ROI
- Regulatory information display
- Policy recommendations

## Implementation Details

### API Module Structure
```python
class NRELDataSource:
    def __init__(self, api_key=None):
        self.api_key = api_key or config.NREL_API_KEY
        self.base_url = "https://developer.nrel.gov/api"
    
    def get_solar_resource(self, lat, lon):
        # Implementation for solar resource data retrieval
        
    def get_pvwatts(self, lat, lon, system_capacity=4, ...):
        # Implementation for PVWatts calculations
        
    def get_utility_rates(self, lat, lon, radius=0):
        # Implementation for utility rates retrieval
```

### Key Findings & Corrections

1. **Utility Rates API Correction:**
   - Original implementation used `address` parameter which failed
   - Corrected to use `lat` & `lon` parameters based on API documentation
   - Works correctly with coordinates for all test locations

2. **Production Estimate Comparisons:**
   - Denver: 1,613 kWh/kW
   - Phoenix: 1,749 kWh/kW
   - Seattle: 1,107 kWh/kW
   - Impact: Phoenix produces 58% more energy than Seattle

3. **Tilt Angle Optimization:**
   - Tested angles from 0-40° for Denver
   - 0° (flat): 13,786 kWh
   - 20° (typical): 16,133 kWh
   - 40° (optimal): 16,806 kWh
   - Finding: Proper tilt increases production by 22%

## Limitations and Considerations

1. **API Rate Limits:**
   - Developer key: 1,000 requests per hour
   - Need to monitor usage as application scales
   - Caching strategy required for production

2. **Data Coverage:**
   - Strong coverage for US locations
   - Limited international data
   - Rural areas may have less precise data

3. **Calculation Assumptions:**
   - PVWatts uses TMY3 (Typical Meteorological Year) data
   - Results are estimates and may differ from actual performance
   - Default assumptions may need adjustment for specific scenarios

## Next Steps

1. ✅ Expand testing to various locations - COMPLETED
2. ✅ Compare NREL data with NASA POWER data for validation - COMPLETED
3. Develop caching strategy to reduce API calls
4. ✅ Create more sophisticated wrappers around raw API data - COMPLETED
5. Test and implement DSIRE Energy Incentives API
6. Integrate with financial calculation models

## Implementation Recommendations

1. Use PVWatts as the primary solar calculation engine
2. Cache results where possible to reduce API calls
3. ✅ Implement thorough error handling for API failures - COMPLETED
4. Create user-friendly explanations of technical parameters
5. Use lat/lon coordinates for all API calls (even when user inputs address)
6. Implement mapping between user inputs and API parameters