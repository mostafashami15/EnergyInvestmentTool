# Energy Investment Tool - Data Pipeline Design

## Overview

This document outlines the data pipeline for the Energy Investment Decision Support System, describing how data flows from external APIs through our system to provide actionable insights to users. Based on our successful API integrations, we've refined the pipeline design.

## Data Sources

### Primary Sources (Implemented ✅)
1. **NREL APIs**
   - ✅ PVWatts API (solar energy production)
   - ✅ Solar Resource Data API (solar radiation)
   - ✅ Utility Rates API (electricity costs)
   - DSIRE API (incentives and policies) - Planned

2. **NASA POWER API**
   - ✅ Hourly data (high-resolution solar and weather)
   - ✅ Daily data (solar radiation and meteorology)
   - ✅ Monthly data (long-term averages)
   - ✅ Climatology data (30+ year averages)

3. **Supplementary Sources** (Planned)
   - Economic data (inflation rates, energy prices)
   - Equipment cost databases
   - Geographic information (elevation, land use)

## Data Flow Architecture

```
┌───────────┐     ┌───────────┐     ┌───────────┐
│  External │     │   Cache   │     │ Processing│
│   APIs    │────▶│   Layer   │────▶│   Layer   │
└───────────┘     └───────────┘     └───────────┘
                                           │
┌───────────┐     ┌───────────┐     ┌─────▼─────┐
│    UI     │◀───▶│    API    │◀───▶│  Storage  │
│   Layer   │     │  Gateway  │     │   Layer   │
└───────────┘     └───────────┘     └───────────┘
```

## Pipeline Components

### 1. Data Retrieval Module (Implemented ✅)

**Purpose:** Fetch data from external APIs while managing rate limits and error handling.

**Implementation Status:**
- ✅ Created API client classes for NREL and NASA
- ✅ Implemented error handling and parameter validation
- ✅ Created standardized interfaces for data access
- ✅ Tested with multiple locations and configurations

**Next Steps:**
- Add retry logic and backoff strategies
- Implement usage tracking for API rate limits
- Add support for DSIRE API

### 2. Caching Layer (Planned)

**Purpose:** Minimize external API calls by caching frequently accessed or slow-changing data.

**Caching Strategy:**
- **Short-term cache** (1 hour): For API responses during user sessions
- **Medium-term cache** (1 day): For frequently accessed locations
- **Long-term cache** (30+ days): For slow-changing data like solar radiation

**Implementation Plan:**
- In-memory cache for active sessions
- Redis/database for persistent caching
- Invalidation rules based on data type

### 3. Data Processing Module (Partially Implemented)

**Purpose:** Transform raw API data into useful calculations and insights.

**Implementation Status:**
- ✅ Solar production calculations using NREL PVWatts data
- ✅ Alternative solar calculations using NASA data
- ✅ Data parsing and normalization for both APIs

**Next Steps:**
- Financial analysis using utility rate data
- Comparative analysis between energy technologies
- Sensitivity analysis for key parameters

### 4. Storage Layer (Planned)

**Purpose:** Persist user projects, calculations, and shared data.

**Data Models:**
- User projects and saved scenarios
- Calculation results
- Reference data (equipment specs, costs)
- Regional data (solar resources, incentives)

**Implementation Plan:**
- Relational database for structured data
- Document storage for complex calculation results
- Data versioning for tracking changes

### 5. API Gateway (Planned)

**Purpose:** Provide unified access to the system's capabilities.

**Endpoints:**
- Resource data retrieval
- Calculation requests
- Project management
- User authentication
- LLM-powered assistance

**Implementation Plan:**
- RESTful API with consistent patterns
- Authentication and rate limiting
- Versioned API for backward compatibility

### 6. UI Data Integration (In Research)

**Purpose:** Connect frontend components with backend data.

**Implementation Status:**
- ✅ Tested Leaflet map integration
- ✅ Explored data visualization approaches

**Next Steps:**
- Implement interactive map with solar data overlay
- Create input forms for system parameters
- Develop results dashboard with visualizations

## Data Transformation Process

### Example: Solar Energy Production Calculation (Implemented ✅)

1. **Input Collection:**
   - Location coordinates (lat/lon)
   - System parameters (size, type, orientation)
   - Financial parameters (budget, expected ROI)

2. **Data Retrieval:**
   - ✅ Solar resource data from NREL/NASA
   - ✅ Local electricity rates
   - Available incentives (planned)

3. **Processing Steps:**
   - ✅ Calculate monthly/annual energy production
   - Determine system costs and financial returns
   - Compare against other energy options
   - Generate optimized recommendations

4. **Output Generation:**
   - ✅ Production estimates with multiple methodologies
   - Financial projections and ROI analysis
   - Visual comparisons and charts
   - Narrative explanations (LLM-enhanced)

## Key Insights from Implementation

### 1. API Response Variability

The NREL and NASA APIs return data in different structures:
- NREL: Consistent JSON structure with predictable paths
- NASA: Structure varies between endpoints (hourly, daily, climatology)
- Solution: Created custom parsers for each endpoint

### 2. Production Estimate Differences

There are significant differences in production estimates:
- NREL PVWatts: 1,613 kWh/kW for Denver
- NASA Calculation: 1,092 kWh/kW for Denver
- Solution: Present both with confidence ranges

### 3. Parameter Sensitivities

System parameters significantly impact results:
- Tilt angle: 22% production difference (0° vs 40°)
- Location: 58% production difference (Seattle vs Phoenix)
- Utility rates: 54% price difference (Seattle vs Phoenix)
- Solution: Sensitivity analysis for key parameters

## Error Handling and Fallback Strategies

1. **API Unavailability:**
   - ✅ Implemented error detection and reporting
   - Planned: Primary/secondary API source pattern
   - Planned: Graceful degradation with cached data

2. **Incomplete Data:**
   - ✅ Added checks for missing data fields
   - Planned: Interpolation strategies for missing values
   - Planned: Default values with user override options

3. **Calculation Errors:**
   - ✅ Added validation for input parameters
   - Planned: More sophisticated bounds checking
   - Planned: User-friendly error messages

## Performance Considerations

1. **Optimization Strategies:**
   - ✅ Identified high-latency API calls
   - Planned: Batch API requests where possible
   - Planned: Pre-calculation of common scenarios

2. **Scaling Approach:**
   - Planned: Horizontal scaling of processing nodes
   - Planned: Distributed caching
   - Planned: Background processing for intensive calculations

## LLM Integration Points (Planned)

1. **Data Interpretation:**
   - Converting technical data to natural language explanations
   - Highlighting key insights from calculation results
   - Generating comparative analyses

2. **User Assistance:**
   - Helping users understand input parameters
   - Suggesting optimizations based on calculated results
   - Answering follow-up questions about recommendations

3. **Report Generation:**
   - Creating narrative summary reports
   - Explaining technical details in user-appropriate language
   - Highlighting key decision factors

## Next Steps in Pipeline Development

1. **Immediate Tasks:**
   - ✅ Implement basic data retrieval modules for NREL and NASA - COMPLETED
   - Design database schema for storing calculation results
   - Create caching strategy implementation

2. **Secondary Tasks:**
   - ✅ Develop unified data model across sources - PARTIALLY COMPLETED
   - Implement financial calculation modules
   - Create user project storage and retrieval

3. **Advanced Features:**
   - Build optimization algorithms
   - Implement LLM-driven insights generation
   - Develop anomaly detection for unreliable data