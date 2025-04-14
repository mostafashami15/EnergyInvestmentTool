# Energy Investment Decision Support System - Project Documentation

## Project Overview

The Energy Investment Decision Support System is an interactive web application that helps users make informed decisions about renewable energy investments based on location-specific data, financial parameters, and technological options. The system has been enhanced with advanced features including sensitivity analysis, user authentication, project management, and performance optimization through caching.

## Key Features

### Core Functionality
- Interactive map interface for location selection
- Financial parameter input for budget and ROI expectations
- Automated calculation of energy production potential by technology
- Comparison of different renewable energy options
- Project saving and retrieval

### Advanced Features
- **Sensitivity Analysis**: Interactive visualizations showing parameter impact
- **User Authentication**: Secure account creation and management
- **Project Management**: Save, load, and share investment scenarios
- **Data Caching**: Performance optimization with multi-tiered caching
- **Admin Dashboard**: System monitoring and cache management

### Enhanced by LLM Integration
- Natural language input processing
- Intelligent report generation
- Interactive advisor for follow-up questions
- Regulatory and incentive analysis
- Contextual knowledge enhancement

## System Architecture

The system follows a modern client-server architecture with clear separation of concerns:

```
┌───────────────────────────────────────────────────────────────────┐
│                        React Frontend                             │
├─────────────┬───────────────┬───────────────┬────────────────────┤
│ Core UI     │ Authentication│ Project       │ Advanced           │
│ Components  │ Components    │ Management    │ Visualization      │
└──────┬──────┴───────┬───────┴───────┬───────┴────────┬───────────┘
       │              │               │                │
       └──────────────┼───────────────┼────────────────┘
                      │               │
                      │  HTTP/JSON    │
                      ▼               ▼
┌───────────────────────────────────────────────────────────────────┐
│                        Flask Backend                              │
├─────────────┬───────────────┬───────────────┬────────────────────┤
│ Calculation │ Financial     │ Auth & DB     │ Sensitivity &      │
│ Engine      │ Modeling      │ Managers      │ Cache Managers     │
└──────┬──────┴───────┬───────┴───────┬───────┴────────┬───────────┘
       │              │               │                │
       │              │               │                │
┌──────▼──────┐┌──────▼──────┐┌───────▼───────┐┌───────▼───────────┐
│ NREL APIs   ││  NASA APIs  ││ SQLite        ││ Cache Store        │
└─────────────┘└─────────────┘└───────────────┘└───────────────────┘
```

## Technology Stack

### Frontend
- React.js for UI components
- Tailwind CSS for styling
- Mapping library (Leaflet)
- Data visualization (Recharts)
- Authentication management (JWT)

### Backend
- Python/Flask API
- SQLite database for user projects and calculations
- Multi-tiered caching system
- Integration with external APIs (NREL, NASA)

### Advanced Modules
- Sensitivity Analysis Engine
- Authentication Manager
- Database Manager
- Cache Manager

## Module Documentation

### Core Modules

#### Calculation Engine
The Calculation Engine serves as the core computational component, providing a unified interface for calculating solar energy production and financial metrics using data from both NREL and NASA POWER APIs.

Key features:
- Multi-source data integration
- Comparative analysis
- Financial metrics calculation
- Sensitivity analysis integration

[See detailed documentation](./Unified_Calculation_Engine_Documentation.md)

#### Financial Modeling
The Financial Modeling module provides sophisticated financial analysis capabilities for renewable energy investments, including loan calculations, detailed cash flows, and scenario analysis.

Key features:
- Comprehensive financial metrics
- Loan calculations
- Degradation modeling
- Incentive analysis
- Scenario and sensitivity analysis

[See detailed documentation](./Financial_Modeling_Module_Documentation.md)

### Advanced Modules

#### Sensitivity Analyzer
The Sensitivity Analysis module provides comprehensive functionality for analyzing how changes in key parameters affect financial outcomes for renewable energy investments.

Key features:
- Parameter sensitivity analysis
- Multi-parameter tornado charts
- Scenario comparison
- Custom scenario creation
- Data preparation for visualization

[See detailed documentation](./Sensitivity_Analysis_Module_Documentation.md)

#### Auth Manager
The Authentication Manager handles all aspects of user authentication, including registration, login, token generation, and verification.

Key features:
- Secure user registration
- User authentication
- Password management
- Token-based authentication
- User profile management

[See detailed documentation](./User_Authentication_and_Database_Management_Documentation.md)

#### Database Manager
The Database Manager handles all database operations, including user storage, project management, and data persistence.

Key features:
- User storage
- Project management
- Data persistence
- Query handling
- Project sharing

[See detailed documentation](./User_Authentication_and_Database_Management_Documentation.md)

#### Cache Manager
The Cache Manager provides a multi-tiered caching solution that optimizes performance by reducing redundant API calls and calculations.

Key features:
- Multi-tiered caching
- Memory and disk caching
- Namespace organization
- Cache invalidation
- Cache statistics
- Decorator support

[See detailed documentation](./Data_Caching_System_Documentation.md)

### Frontend Components

#### Core UI Components
- **EnergyInvestmentApp**: Main application component
- **SolarMapComponent**: Interactive map for location selection
- **SystemParameterForm**: Input form for system parameters
- **ResultsDashboard**: Visualization of calculation results

#### Authentication Components
- **AuthProvider**: Authentication context provider
- **LoginForm**: User login interface
- **RegisterForm**: New user registration interface

#### Project Management Components
- **ProjectList**: List of user's saved projects
- **SaveProjectForm**: Interface for saving and updating projects

#### Advanced Visualization Components
- **SensitivityAnalysisVisualization**: Interactive sensitivity analysis
- **CacheMonitoring**: Admin interface for cache management

[See detailed documentation](./Frontend_Components_Documentation.md)

### API Handler

The API Handler serves as the backend interface, providing RESTful endpoints for the frontend components.

Key endpoints:
- Data retrieval endpoints (solar resource, utility rates)
- Calculation endpoints (production, financials)
- Authentication endpoints (register, login, verify)
- Project management endpoints (save, load, delete)
- Cache management endpoints (stats, clear, invalidate)

[See detailed documentation](./API_Handler_Documentation.md)

## Data Flow

### Solar Calculation Flow
1. User selects location on the map
2. User configures system parameters
3. System retrieves solar resource data from NREL/NASA
4. Calculation engine computes production estimates
5. Financial model calculates ROI and other metrics
6. Results are displayed in the dashboard
7. Sensitivity analysis shows parameter impact

### Authentication Flow
1. User registers or logs in
2. System issues JWT token
3. Token is stored in browser local storage
4. Subsequent requests include token in header
5. Backend validates token for protected operations

### Project Management Flow
1. User creates a project by saving current parameters
2. Project is stored in the database
3. User can view list of saved projects
4. User can load a project to restore parameters
5. User can update or delete projects

### Caching Flow
1. API request is received
2. System checks cache for existing response
3. If found, cached response is returned
4. If not found, calculation is performed
5. Result is cached for future requests
6. Admin can manage cache through admin interface

## Development Timeline and Status

The project follows a phased approach as outlined in the roadmap:

1. ✅ **Phase 1: Foundation** (Completed)
   - Research and planning
   - Core infrastructure setup
   - MVP backend development

2. ✅ **Phase 2: Core Functionality** (Completed)
   - Frontend development
   - Algorithm development
   - Basic features implementation

3. ✅ **Phase 3: Advanced Features** (Current)
   - Enhanced visualization and analysis (Sensitivity Analysis)
   - User management system (Authentication & Projects)
   - Performance optimization (Caching System)

4. ⏳ **Phase 4: Refinement and Launch** (Next)
   - Testing and optimization
   - Documentation and deployment
   - Marketing preparation

5. 🔄 **Phase 5: Growth and Expansion** (Future)
   - Additional energy technologies
   - Integration with equipment vendor APIs
   - Mobile application development

## API Integrations

### NREL APIs
- PVWatts API: Solar energy production calculations
- Solar Resource Data API: Solar radiation values
- Utility Rates API: Electricity cost data
- DSIRE API: Incentives and policies (planned)

### NASA POWER API
- Hourly data: High-resolution solar and weather
- Daily data: Solar radiation and meteorology
- Monthly data: Long-term averages
- Climatology data: 30+ year averages

## Project Structure

```
EnergyInvestmentTool/
├── client/                # React frontend
│   ├── public/            # Static assets
│   └── src/
│       ├── components/    # React components
│       │   ├── AuthProvider.jsx
│       │   ├── CacheMonitoring.jsx
│       │   ├── EnergyInvestmentApp.jsx
│       │   ├── LoginForm.jsx
│       │   ├── ProjectList.jsx
│       │   ├── RegisterForm.jsx
│       │   ├── ResultsDashboard.jsx
│       │   ├── SaveProjectForm.jsx
│       │   ├── SensitivityAnalysisVisualization.jsx
│       │   ├── SolarMapComponent.jsx
│       │   └── SystemParameterForm.jsx
│       ├── index.css      # Global styles
│       └── index.js       # Application entry point
├── docs/                  # Documentation
│   ├── api_research/      # API research notes
│   │   ├── api_comparison.md
│   │   ├── nasa_api_notes.md
│   │   └── nrel_api_notes.md
│   ├── roadmap.md         # Project roadmap
│   └── system_design/     # Design documents
│       └── data_pipline.md
├── pyproject.toml         # Poetry configuration
├── README.md              # Project overview
└── server/                # Backend Python application
    └── src/
        ├── api_handler.py            # API endpoints
        ├── auth_manager.py           # Authentication manager
        ├── cache_manager.py          # Caching system
        ├── calculation_engine.py     # Core calculation module
        ├── config.py                 # Configuration settings
        ├── data_sources/             # API client implementations
        │   ├── __init__.py
        │   ├── nasa.py               # NASA API client
        │   └── nrel.py               # NREL API client
        ├── db_manager.py             # Database manager
        ├── financial_modeling.py     # Financial analysis module
        ├── sensitivity_analyzer.py   # Sensitivity analysis
        └── research/                 # Research and testing scripts
```

## Getting Started

### Prerequisites
- Python 3.11 or higher
- Node.js 14 or higher
- Poetry for Python dependency management

### Backend Setup
1. Clone the repository
2. Install dependencies using Poetry:
   ```
   poetry install
   ```
3. Set up environment variables:
   ```
   JWT_SECRET_KEY=your_secret_key
   NREL_API_KEY=your_nrel_api_key
   ```
4. Run the Flask server:
   ```
   poetry run python server/src/api_handler.py
   ```

### Frontend Setup
1. Navigate to the client directory:
   ```
   cd client
   ```
2. Install dependencies:
   ```
   npm install
   ```
3. Start the development server:
   ```
   npm start
   ```

## Security Considerations

### Authentication
- JWT tokens for secure authentication
- PBKDF2 with SHA-256 for password hashing
- Token expiration and validation
- Protected API endpoints

### Data Security
- Proper input validation and sanitization
- SQL injection prevention through parameterized queries
- User data isolation in the database
- Error handling without sensitive information disclosure

### API Security
- Rate limiting for API requests
- CORS configuration for production
- Admin endpoint protection
- Environment variable management for sensitive data

## Performance Optimizations

### Caching Strategy
- Short-term cache (1 hour) for API responses during user sessions
- Medium-term cache (1 day) for frequently accessed locations
- Long-term cache (30 days) for slow-changing data like solar radiation

### Backend Optimization
- Efficient database queries
- Memory management in Python
- Thread-safe operations
- Asynchronous processing where appropriate

### Frontend Optimization
- React component memoization
- Efficient state management
- Lazy loading of components
- Optimized rendering for charts and maps

## Future Enhancements

### Additional Energy Technologies
- Wind energy modeling and production estimates
- Geothermal potential assessment
- Battery storage economic analysis

### Enhanced Features
- Monte Carlo simulation for risk analysis
- Integration with equipment vendors
- Regulatory compliance checks
- Mobile application development

### Enterprise Capabilities
- Multi-user organization accounts
- Role-based access control
- Advanced reporting and exports
- API access for third-party integration

## Conclusion

The Energy Investment Decision Support System provides a comprehensive solution for analyzing renewable energy investments. The advanced features implemented in the current phase significantly enhance the system's capabilities by providing deeper insights through sensitivity analysis, user-specific data persistence through authentication and project management, and improved performance through intelligent caching.

The system architecture ensures scalability and maintainability, with clear separation of concerns and well-defined interfaces between components. The project is well-positioned for the refinement and launch phase, with a solid foundation of features that meet the needs of both individual users and organizations making renewable energy investment decisions.