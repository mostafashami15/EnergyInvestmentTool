# NASA POWER API Research Notes

## API Overview
NASA's POWER (Prediction of Worldwide Energy Resources) API provides global solar radiation, meteorological, and climatological data useful for renewable energy analysis and planning. We have successfully integrated and tested multiple endpoints of this API.

**API Base URLs:**
- Hourly: `https://power.larc.nasa.gov/api/temporal/hourly/point`
- Daily: `https://power.larc.nasa.gov/api/temporal/daily/point`
- Monthly: `https://power.larc.nasa.gov/api/temporal/monthly/point`
- Climatology: `https://power.larc.nasa.gov/api/temporal/climatology/point`

**Authentication:** No API key required

## Key Endpoints Implemented

### 1. Hourly Data API
**Endpoint:** `https://power.larc.nasa.gov/api/temporal/hourly/point`

**Purpose:** Provides hourly solar radiation and meteorological data for detailed analysis.

**Key Parameters:**
- `latitude` & `longitude`: Location coordinates
- `start` & `end`: Date range in YYYYMMDD format
- `parameters`: Comma-separated list of data parameters
- `community`: Data community (RE for Renewable Energy)
- `format`: Response format (JSON, CSV, etc.)

**Example Response Structure:**
```json
{
  "properties": {
    "parameter": {
      "ALLSKY_SFC_SW_DWN": {
        "2023010100": 0.0,
        "2023010101": 0.0,
        "2023010102": 0.0,
        "...": "..."
      }
    }
  },
  "parameters": {
    "ALLSKY_SFC_SW_DWN": {
      "longname": "All Sky Surface Shortwave Downward Irradiance",
      "units": "Wh/m^2"
    }
  }
}
```

**Test Results:**
- Successfully retrieved hourly data for test locations
- Data shows expected diurnal patterns (0 at night, peak at midday)
- Unit is Wh/m² (different from daily data units)
- Night hours consistently show 0 radiation as expected

**Use in Project:**
- Detailed solar production modeling
- Time-of-day analysis
- Battery storage sizing

### 2. Daily Data API
**Endpoint:** `https://power.larc.nasa.gov/api/temporal/daily/point`

**Purpose:** Provides daily solar radiation and meteorological data.

**Key Parameters:**
- `latitude` & `longitude`: Location coordinates
- `start` & `end`: Date range in YYYYMMDD format
- `parameters`: Comma-separated list of data parameters
- `community`: Data community (RE for Renewable Energy)
- `format`: Response format (JSON, CSV, etc.)

**Example Response Structure:**
```json
{
  "properties": {
    "parameter": {
      "ALLSKY_SFC_SW_DWN": {
        "20230101": 1.62,
        "20230102": 0.82,
        "20230103": 2.07,
        "...": "..."
      }
    }
  },
  "parameters": {
    "ALLSKY_SFC_SW_DWN": {
      "longname": "All Sky Surface Shortwave Downward Irradiance",
      "units": "kW-hr/m^2/day"
    }
  }
}
```

**Test Results:**
- Successfully retrieved daily data for Jan 1-7, 2023
- Denver values ranged from 0.82-3.06 kWh/m²/day
- Weather effects clearly visible in day-to-day variations
- Format consistent and easy to parse

**Use in Project:**
- Historical performance analysis
- Daily production estimates
- Weather pattern impacts

### 3. Monthly Data API
**Endpoint:** `https://power.larc.nasa.gov/api/temporal/monthly/point`

**Purpose:** Provides monthly averages of solar and meteorological data.

**Key Parameters:**
- `latitude` & `longitude`: Location coordinates
- `start` & `end`: Year-month range in YYYYMM format
- `parameters`: Comma-separated list of data parameters
- `community`: Data community (RE for Renewable Energy)
- `format`: Response format (JSON, CSV, etc.)

**Example Response Structure:** Similar to daily data but with YYYYMM keys

**Test Results:**
- Successfully retrieved monthly data
- Seasonal patterns clearly visible
- Consistent with NREL monthly averages

**Use in Project:**
- Seasonal production forecasting
- Long-term trend analysis

### 4. Climatology API
**Endpoint:** `https://power.larc.nasa.gov/api/temporal/climatology/point`

**Purpose:** Provides long-term climate averages (typically 30+ years) for each month.

**Key Parameters:**
- `latitude` & `longitude`: Location coordinates
- `parameters`: Comma-separated list of data parameters
- `community`: Data community (RE for Renewable Energy)
- `format`: Response format (JSON, CSV, etc.)

**Example Response Structure:**
```json
{
  "properties": {
    "parameter": {
      "ALLSKY_SFC_SW_DWN": {
        "JAN": 2.57,
        "FEB": 3.51,
        "MAR": 4.72,
        "APR": 5.74,
        "MAY": 6.44,
        "JUN": 7.21,
        "JUL": 6.98,
        "AUG": 6.29,
        "SEP": 5.38,
        "OCT": 3.98,
        "NOV": 2.86,
        "DEC": 2.26,
        "ANN": 4.83
      }
    }
  },
  "parameters": {
    "ALLSKY_SFC_SW_DWN": {
      "longname": "All Sky Surface Shortwave Downward Irradiance",
      "units": "kW-hr/m^2/day"
    }
  }
}
```

**Test Results:**
- Successfully retrieved climatology data
- Denver annual average GHI: 4.83 kWh/m²/day (exactly matches NREL)
- Seasonal patterns clearly visible
- Month format uses three-letter abbreviations (JAN, FEB) instead of numbers

**Use in Project:**
- Long-term energy production estimates
- System sizing and ROI calculations
- Regional comparative analysis

## Implementation Details

### API Module Structure
```python
class NASAPowerDataSource:
    def __init__(self):
        self.hourly_url = "https://power.larc.nasa.gov/api/temporal/hourly/point"
        self.daily_url = "https://power.larc.nasa.gov/api/temporal/daily/point"
        self.monthly_url = "https://power.larc.nasa.gov/api/temporal/monthly/point"
        self.climatology_url = "https://power.larc.nasa.gov/api/temporal/climatology/point"
    
    def get_hourly_data(self, lat, lon, start_date, end_date, parameters=None):
        # Implementation for hourly data retrieval
        
    def get_solar_data(self, lat, lon, start_date, end_date, parameters=None):
        # Implementation for daily data retrieval
        
    def get_monthly_data(self, lat, lon, start_date, end_date, parameters=None):
        # Implementation for monthly data retrieval
        
    def get_monthly_climatology(self, lat, lon, parameters=None):
        # Implementation for climatology data retrieval
        
    def calculate_solar_potential(self, lat, lon, system_capacity=4, efficiency=0.15, performance_ratio=0.75):
        # Implementation for solar production calculations
```

### Key Findings & Challenges

1. **API Response Structure Variations:**
   - Each endpoint returns data in a slightly different structure
   - Daily/Hourly data use YYYYMMDD or YYYYMMDDHH keys
   - Climatology data uses three-letter month abbreviations (JAN, FEB)
   - Solution: Custom parsers for each endpoint

2. **Date Format Requirements:**
   - API only accepts historical dates (not future)
   - Different endpoints require different date formats
   - Hourly/Daily: YYYYMMDD
   - Monthly: YYYYMM
   - Solution: Date format validation before API calls

3. **Solar Production Calculations:**
   - Implemented custom calculation from raw radiation data
   - Applied system size, efficiency, and performance ratio
   - Results lower than NREL PVWatts by ~30-40%
   - Possible reasons: Different assumptions about losses and system efficiency

4. **Regional Variation Example:**
   - Denver annual GHI: 4.83 kWh/m²/day
   - Annual production (10kW): 10,917 kWh/year
   - Monthly variations follow expected seasonal patterns

### Solar Potential Calculation Method

Our implementation calculates solar energy production from NASA climatology data:

1. Retrieve long-term monthly solar radiation averages
2. For each month:
   - Calculate solar panel area based on system capacity (~5.5 m²/kW)
   - Apply efficiency factor (default: 15%)
   - Apply performance ratio (default: 75%)
   - Multiply by days in month
   - Result: Monthly kWh production
3. Sum monthly values for annual production

**Code Example:**
```python
# Simplified calculation example
monthly_kwh = (
    daily_kwh_per_m2 * days_in_month * 
    solar_panel_area * efficiency * performance_ratio
)
```

## Comparison with NREL Data

### Solar Resource Values (GHI)
- **Denver Annual Average:**
  - NASA: 4.83 kWh/m²/day
  - NREL: 4.83 kWh/m²/day
  - Finding: Identical annual averages

### Monthly Values Example (Denver)
| Month | NASA (kWh/m²/day) | NREL (kWh/m²/day) |
|-------|-------------------|-------------------|
| Jan   | 2.57              | 2.51              |
| Jun   | 7.21              | 7.21              |
| Dec   | 2.26              | 2.26              |

### Production Estimates (10kW system in Denver)
- **NASA Calculation:** 10,917 kWh/year (1,092 kWh/kW)
- **NREL PVWatts:** 16,133 kWh/year (1,613 kWh/kW)
- **Finding:** NREL estimates ~48% higher production

## Limitations and Considerations

1. **No Authentication Required:**
   - Easier to implement than NREL (no API key)
   - Potential concerns about reliability for production use
   - No clear rate limits documented

2. **Data Coverage:**
   - Global coverage (advantage over NREL)
   - Spatial resolution moderate (0.5° × 0.5°)
   - Temporal coverage excellent (back to 1981)

3. **Calculation Assumptions:**
   - Our solar calculations are simplified
   - Does not account for all system losses that PVWatts includes
   - Conservative estimates compared to NREL

## Next Steps

1. ✅ Validate data against NREL sources - COMPLETED
2. ✅ Implement solar production calculations - COMPLETED
3. Refine calculation methodology to better align with industry standards
4. Explore additional parameters (temperature, wind, humidity)
5. Implement caching strategy for API responses
6. Add visualization tools for temporal data

## Implementation Recommendations

1. Use NASA data for global locations outside NREL coverage
2. Use NASA hourly data for detailed temporal analysis
3. Consider presenting both NASA and NREL production estimates to users
4. Cache climatology data long-term (changes very rarely)
5. Implement proper error handling for rate limits and service outages