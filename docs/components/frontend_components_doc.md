# Frontend Components Documentation

This document provides a comprehensive overview of the React components developed for the Energy Investment Decision Support System.

## Component Architecture

The frontend is structured around several React components that work together to provide a complete user experience:

```
┌────────────────────────────────────────────────────────────┐
│                 EnergyInvestmentApp                        │
├───────────┬───────────┬───────────────┬───────────────────┤
│  Solar    │ System    │  Results      │ Authentication &   │
│   Map     │ Parameter │  Dashboard    │ Project Management │
├───────────┴───────────┴───────────────┼───────────────────┤
│                                       │  AuthProvider      │
│      Core Functionality               │  LoginForm         │
│                                       │  RegisterForm      │
│                                       │  ProjectList       │
│                                       │  SaveProjectForm   │
├───────────────────────────────────────┼───────────────────┤
│  Sensitivity Analysis                 │  Cache Monitoring  │
│  SensitivityAnalysisVisualization     │  (Admin Interface) │
└───────────────────────────────────────┴───────────────────┘
```

## 1. EnergyInvestmentApp Component

### Purpose
The main application component that orchestrates the overall user experience, manages application state, and coordinates interactions between child components.

### Key Features
- Application state management (location, calculation results)
- API communication for data retrieval and calculations
- Authentication status management
- Project management
- Layout and user interface organization
- Error handling and loading states

### State Management
The component manages several key pieces of state:
- `location`: The geographic coordinates selected by the user
- `projectParams`: Parameters for system configuration
- `calculationResults`: Data returned from calculations
- `loading`: Boolean indicating if calculations are in progress
- `error`: Error message if calculation fails
- `sensitivityData`: Data for sensitivity analysis
- `selectedProject`: Currently selected project (if any)
- Modal states for showing login, register, project list, etc.

### API Integration
The component integrates with API endpoints for:
- Calculation of production and financial metrics
- Sensitivity analysis
- Project management (when authenticated)

### User Authentication
- Shows login/register buttons when not authenticated
- Shows user info, logout, and project management buttons when authenticated
- Creates modal overlays for authentication forms

### Project Management
- Allows users to save, load, and manage their projects
- Integrates with database via API endpoints
- Supports project creation and updates

## 2. SolarMapComponent

### Purpose
Provides an interactive map interface for selecting the project location and visualizing solar resource data across different geographic areas.

### Key Features
- Interactive Leaflet map for location selection
- Solar radiation visualization with color coding
- Location search by coordinates
- Geolocation support ("Use My Location")
- Solar resource data visualization

### Technical Implementation
- Uses Leaflet.js for mapping functionality
- Dynamically loads map library if not already available
- Color gradient visualization for solar resource intensity
- Custom markers and popups with location data

## 3. SystemParameterForm Component

### Purpose
Provides a user interface for inputting all the parameters required for solar system calculations and financial analysis.

### Key Features
- Comprehensive input form for system specifications
- Financial parameter inputs
- Data source selection options
- Default values for common scenarios
- Real-time validation and feedback

### Form Sections
1. **System Specifications**
   - System capacity (kW)
   - Module type (standard, premium, thin film)
   - Array type (fixed, tracking)
   - System losses (%)

2. **Array Orientation**
   - Tilt (degrees)
   - Azimuth (degrees)

3. **Financial Parameters**
   - System cost ($/watt)
   - Incentive (%)
   - Loan amount (%)
   - Loan term and rate
   - Analysis period

4. **Data Source Options**
   - NREL (US-focused)
   - NASA (global coverage)
   - Both (comparison)

## 4. ResultsDashboard Component

### Purpose
Visualizes calculation results through interactive charts, tables, and key metrics displays, providing comprehensive insights into both production and financial aspects of the solar investment.

### Key Features
- Tabbed interface for organized data presentation
- Interactive and responsive data visualizations
- Key metrics dashboard with visual indicators
- Detailed tables for in-depth analysis
- Comparative visualizations for different data sources

### Tab Sections
1. **Summary**
   - Key metrics cards
   - Production comparison chart
   - Payback period visualization

2. **Production**
   - Monthly production chart
   - Production data comparison table
   - Data source variance analysis

3. **Financial**
   - ROI breakdown
   - Financial metrics table
   - Cost-benefit visualization
   - Sensitivity analysis (when available)

4. **Cash Flow**
   - Cumulative cash flow chart
   - Annual cash flow details table
   - Payback period indicator

## 5. AuthProvider Component

### Purpose
Provides authentication context and functionality to the application, making authentication state and functions available to all components.

### Key Features
- User authentication state management
- Token storage and management
- Login and registration functionality
- Authentication persistence across sessions
- Authenticated API fetch function

### Implementation
- Uses React Context API for global state management
- Stores authentication token in localStorage
- Provides hooks for accessing authentication state and functions
- Handles token verification and renewal
- Supports logout functionality

## 6. LoginForm Component

### Purpose
Provides a user interface for logging into the application with username/email and password.

### Key Features
- Username/email and password input fields
- Form validation
- Error handling and display
- Loading state indication
- Success callback for redirects

### Authentication Flow
1. User enters credentials
2. Form validates inputs
3. Credentials sent to authentication API
4. Token received and stored
5. User state updated in AuthProvider

## 7. RegisterForm Component

### Purpose
Provides a user interface for creating a new account in the system.

### Key Features
- Username, email, and password fields
- Password confirmation
- Comprehensive form validation
- Error handling and display
- Success callback for redirects

### Registration Flow
1. User enters registration details
2. Form validates inputs (password strength, email format, etc.)
3. Registration request sent to API
4. Account created and token received
5. User automatically logged in

## 8. ProjectList Component

### Purpose
Displays a list of the authenticated user's saved projects and provides management functionality.

### Key Features
- List of saved projects with details
- Project loading functionality
- Project deletion with confirmation
- Empty state for new users
- Sorting and filtering options

### Project Management
- Fetches projects from database via API
- Handles project selection and loading
- Supports project deletion with confirmation
- Shows sharing status for shared projects (if applicable)

## 9. SaveProjectForm Component

### Purpose
Provides a form for saving a new project or updating an existing one.

### Key Features
- Project name and description fields
- Display of project parameters and location
- Create/update functionality
- Cancel option
- Success confirmation

### Project Saving Flow
1. User enters project name and description
2. Form shows summary of data to be saved
3. User submits form
4. Project saved to database via API
5. Success confirmation shown

## 10. SensitivityAnalysisVisualization Component

### Purpose
Provides interactive visualization of parameter sensitivity analysis for energy investment decisions.

### Key Features
- Tornado charts showing parameter impact
- Scenario comparison charts
- Interactive parameter sliders for custom scenarios
- Metric selection for different financial indicators
- Real-time recalculation of custom scenarios

### Visualization Types
1. **Parameter Impact** (Tornado Chart)
   - Shows how changes in each parameter affect the selected financial metric
   - Displays both positive and negative impacts
   - Sorted by impact magnitude

2. **Scenario Comparison**
   - Compares predefined scenarios (optimistic, pessimistic, etc.)
   - Shows relative performance across scenarios
   - Includes percentage change vs. baseline

3. **Custom Scenario**
   - Interactive sliders for adjusting parameters
   - Real-time calculation of custom scenario results
   - Side-by-side comparison with baseline

### Parameter Definitions
Includes definitions, ranges, and formatting for key parameters:
- System cost ($/W)
- Electricity rate ($/kWh)
- Loan interest rate (%)
- Incentives (%)
- Electricity inflation (%)
- Panel degradation (%)

### Metric Definitions
Supports analysis of multiple financial metrics:
- Net Present Value (NPV)
- Return on Investment (ROI)
- Payback Period
- Internal Rate of Return (IRR)
- Levelized Cost of Energy (LCOE)
- Lifetime Savings

## 11. CacheMonitoring Component

### Purpose
Provides an admin interface for monitoring and managing the caching system's performance.

### Key Features
- Cache statistics visualization
- Tiered cache monitoring (short-term, medium-term, long-term)
- Cache management actions (clear, invalidate, cleanup)
- Performance metrics and charts
- Admin-only access control

### Monitoring Sections
1. **Cache Overview**
   - Memory and disk cache statistics
   - Hit ratio visualization
   - Cache size and entry counts

2. **Cache Tier Details**
   - Statistics for each cache tier
   - Time-to-live (TTL) settings
   - Usage patterns and performance

3. **Cache Management**
   - Clear cache (full or by tier)
   - Invalidate namespace
   - Cleanup expired entries
   - Refresh statistics

### Technical Implementation
- Uses Recharts for data visualization
- Real-time update capability
- Admin authentication check
- API integration for cache management

## Integration and Data Flow

### Authentication Flow
```
User Input → LoginForm/RegisterForm → AuthProvider → API → Token Storage
                                                        ↓
        Protected Components ← AuthProvider Context ← Authenticated State
```

### Project Management Flow
```
User Selects Project → ProjectList → API → Database
                                      ↓
App State ← EnergyInvestmentApp ← Project Data
   ↓
UI Update (Map, Form, Results)
```

### Sensitivity Analysis Flow
```
Calculation Results → API Request → Sensitivity Data
                                       ↓
User Input → Parameter Sliders → Custom Scenario Request → Updated Results
                                                             ↓
                                                      Visualization Update
```

## Responsive Design Implementation

All components implement responsive design principles:
- Flexible layouts using CSS Grid and Flexbox
- Mobile-first approach with breakpoints
- Appropriate spacing and sizing for different devices
- Touch-friendly interaction targets

## Performance Optimizations

### Rendering Optimizations
- Conditional rendering to minimize DOM updates
- Appropriate React key usage for list rendering
- Memoization of expensive calculations

### Data Processing
- Data transformation performed once, results cached
- Chart data prepared efficiently
- Pagination for large datasets (project list, cash flow table)

### Resource Loading
- Leaflet library loaded on-demand
- Efficient chart rendering with ResponsiveContainer
- Appropriate use of React hooks for lifecycle management

## Best Practices for Component Usage

### Authentication & Security
- Always wrap application with AuthProvider at the root
- Use the provided authFetch function for authenticated API calls
- Handle token expiration gracefully

### Project Management
- Refresh project list after save/delete operations
- Confirm before deleting projects
- Validate required fields before saving

### Sensitivity Analysis
- Provide clear explanations of metrics and parameters
- Use appropriate chart types for different data
- Implement user-friendly parameter controls