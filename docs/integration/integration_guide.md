# Energy Investment Decision Support System - Integration Guide

This guide provides comprehensive instructions for integrating all components of the Energy Investment Decision Support System. It covers the connections between frontend and backend components, data flow between modules, and best practices for ensuring proper system operation.

## System Integration Overview

The Energy Investment Decision Support System integrates multiple components across frontend and backend, as shown in this architecture diagram:

```
┌─────────────────────────────────────────────────────────────────┐
│                        React Frontend                           │
│                                                                 │
│  ┌────────────────┐   ┌────────────────┐   ┌────────────────┐  │
│  │ Core Components│   │ Auth Components│   │Project & Admin │  │
│  ├────────────────┤   ├────────────────┤   ├────────────────┤  │
│  │SolarMapComponent│──►│  AuthProvider  │◄──┤  ProjectList   │  │
│  │SystemParamForm  │   │  LoginForm     │   │  SaveProject   │  │
│  │ResultsDashboard │   │  RegisterForm  │   │CacheMonitoring │  │
│  │SensitivityViz   │   └────────────────┘   └────────────────┘  │
│  └────────────────┘            │                    │           │
│           │                    │                    │           │
└───────────┼────────────────────┼────────────────────┼───────────┘
            │                    │                    │
            ▼                    ▼                    ▼
┌───────────────────────────────────────────────────────────────────┐
│                           API Handler                             │
│                                                                   │
│  ┌─────────────────┐  ┌─────────────────┐  ┌────────────────────┐│
│  │ Data Endpoints  │  │ Auth Endpoints  │  │ Project & Admin    ││
│  ├─────────────────┤  ├─────────────────┤  ├────────────────────┤│
│  │/solar-resource  │  │/auth/register   │  │/projects           ││
│  │/utility-rates   │  │/auth/login      │  │/admin/cache        ││
│  │/calculate-all   │  │/auth/verify     │  └────────────────────┘│
│  │/sensitivity     │  └─────────────────┘            │           │
│  └─────────────────┘            │                    │           │
│           │                     │                    │           │
└───────────┼─────────────────────┼────────────────────┼───────────┘
            │                     │                    │
            ▼                     ▼                    ▼
┌─────────────────────┐  ┌────────────────┐  ┌─────────────────────┐
│ Calculation Modules │  │ Auth Manager   │  │ DB & Cache Managers │
├─────────────────────┤  ├────────────────┤  ├─────────────────────┤
│CalculationEngine    │  │User Registration│  │Project Storage      │
│FinancialModel       │  │Authentication   │  │Data Persistence     │
│SensitivityAnalyzer  │  │Token Handling   │  │Cache Management     │
└─────────────────────┘  └────────────────┘  └─────────────────────┘
```

## Key Integration Points

### 1. Frontend to Backend Communication

All frontend-to-backend communication happens through the API Handler via RESTful endpoints. The main integration points are:

#### Core Calculation Flow

```
SolarMapComponent         SystemParameterForm
       │                         │
       └─────────────┬───────────┘
                     ▼
              /api/calculate-all
                     │
                     ▼
              ResultsDashboard
                     │
                     ▼
        /api/sensitivity-analysis
                     │
                     ▼
       SensitivityAnalysisVisualization
```

#### Authentication Flow

```
   LoginForm/RegisterForm
           │
           ▼
    /api/auth/login or
    /api/auth/register
           │
           ▼
      AuthProvider
           │
           ▼
    /api/auth/verify
           │
           ▼
Protected Components/Operations
```

#### Project Management Flow

```
    SaveProjectForm
          │
          ▼
   /api/projects POST
          │
          ▼
     ProjectList
          │
          ▼
   /api/projects GET
          │
          ▼
  /api/projects/{id}
```

#### Admin Operations Flow

```
    CacheMonitoring
          │
          ▼
  /api/admin/cache/stats
  /api/admin/cache/clear
  /api/admin/cache/invalidate
  /api/admin/cache/cleanup
```

### 2. Backend Module Integration

The backend modules are integrated through the API handler, which coordinates interactions between different components:

#### Calculation Module Integration

```python
# API Handler
from calculation_engine import CalculationEngine
from financial_modeling import FinancialModel
from sensitivity_analyzer import SensitivityAnalyzer

# Initialize modules
calculation_engine = CalculationEngine()
financial_model = FinancialModel()

# Integration in endpoints
@app.route('/api/calculate-all', methods=['POST'])
def calculate_all():
    # Extract parameters from request
    # ...
    
    # Calculate production using calculation engine
    production_data = calculation_engine.calculate_solar_production(...)
    
    # Calculate financials using financial model
    financial_data = calculation_engine.calculate_financial_metrics(...)
    
    # Return combined results
    return jsonify({
        'production': production_data,
        'financials': financial_data
    })

@app.route('/api/sensitivity-analysis', methods=['POST'])
def sensitivity_analysis():
    # Create analyzer with existing engines
    analyzer = SensitivityAnalyzer(calculation_engine, financial_model)
    
    # Perform analysis based on request type
    if analysis_type == 'tornado':
        result = analyzer.analyze_multiple_parameters(base_params)
    elif analysis_type == 'scenario':
        result = analyzer.compare_scenarios(base_params, scenarios)
    elif analysis_type == 'custom':
        result = analyzer.create_custom_scenario(base_params, custom_params)
    
    return jsonify(result)
```

#### Authentication and Database Integration

```python
# API Handler
from auth_manager import AuthManager, token_required
from db_manager import DatabaseManager

# Initialize managers
auth_manager = AuthManager()
db_manager = DatabaseManager()

@app.route('/api/auth/register', methods=['POST'])
def register():
    # Extract user data from request
    # ...
    
    # Register user through auth manager
    user = auth_manager.register_user(username, email, password)
    
    return jsonify(user)

@app.route('/api/projects', methods=['GET'])
@token_required
def get_projects(user_id, username):
    # Use database manager to get projects for user
    projects = db_manager.get_user_projects(user_id)
    
    return jsonify({'projects': projects})
```

#### Cache Integration

```python
# API Handler
from cache_manager import CacheManager
from functools import wraps

# Initialize cache manager
cache_manager = CacheManager()

# Create cache middleware
def cache_middleware(namespace, tier='short'):
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            # Generate cache key from parameters
            # ...
            
            # Check for cached response
            cached_response = cache_manager.get(namespace, params, tier)
            if cached_response:
                return jsonify(cached_response)
            
            # Call original function if no cache hit
            result = f(*args, **kwargs)
            
            # Cache the result
            cache_manager.set(namespace, params, response.get_json(), tier)
            
            return result
        return wrapped
    return decorator

# Apply middleware to endpoints
@app.route('/api/solar-resource', methods=['GET'])
@cache_middleware('solar_resource', 'long')
def get_solar_resource():
    # Implementation that will be cached
    # ...
```

### 3. Frontend Component Integration

#### Authentication Integration

All components that need authentication should be wrapped with the `AuthProvider` component, and use the `useAuth` hook to access authentication state and functions:

```jsx
// index.js
import React from 'react';
import ReactDOM from 'react-dom';
import App from './App';
import AuthProvider from './components/AuthProvider';

ReactDOM.render(
  <React.StrictMode>
    <AuthProvider>
      <App />
    </AuthProvider>
  </React.StrictMode>,
  document.getElementById('root')
);

// Any component that needs authentication
import { useAuth } from './AuthProvider';

function ProtectedComponent() {
  const { isAuthenticated, user, authFetch } = useAuth();
  
  // Use authentication state and functions
  // ...
  
  // Use authFetch for authenticated API calls
  const fetchData = async () => {
    const response = await authFetch('/api/protected-endpoint');
    // ...
  };
  
  return (
    // Component implementation
  );
}
```

#### Project Management Integration

The project management components should be integrated into the main application component:

```jsx
// EnergyInvestmentApp.jsx
import { useState } from 'react';
import { useAuth } from './AuthProvider';
import ProjectList from './ProjectList';
import SaveProjectForm from './SaveProjectForm';

function EnergyInvestmentApp() {
  const { isAuthenticated } = useAuth();
  const [showProjectList, setShowProjectList] = useState(false);
  const [showSaveForm, setShowSaveForm] = useState(false);
  const [selectedProject, setSelectedProject] = useState(null);
  
  // Handle project selection
  const handleProjectSelect = (project) => {
    setSelectedProject(project);
    // Update app state with project data
    // ...
  };
  
  return (
    <div>
      {/* Header with buttons */}
      <header>
        {isAuthenticated && (
          <button onClick={() => setShowProjectList(true)}>
            My Projects
          </button>
        )}
        {/* Other header content */}
      </header>
      
      {/* Main content */}
      <main>
        {/* Core components */}
        {/* ... */}
        
        {/* Project save button */}
        {isAuthenticated && calculationResults && (
          <button onClick={() => setShowSaveForm(true)}>
            {selectedProject ? 'Update Project' : 'Save Project'}
          </button>
        )}
      </main>
      
      {/* Modal overlays */}
      {showProjectList && (
        <Modal onClose={() => setShowProjectList(false)}>
          <ProjectList 
            onProjectSelect={handleProjectSelect} 
            onCreateNew={() => setShowProjectList(false)}
          />
        </Modal>
      )}
      
      {showSaveForm && (
        <Modal onClose={() => setShowSaveForm(false)}>
          <SaveProjectForm 
            projectData={parameters}
            location={location}
            calculationResults={calculationResults}
            existingProject={selectedProject}
            onSuccess={() => setShowSaveForm(false)}
            onCancel={() => setShowSaveForm(false)}
          />
        </Modal>
      )}
    </div>
  );
}
```

#### Sensitivity Analysis Integration

The sensitivity analysis component should be integrated into the results display:

```jsx
// ResultsDashboard.jsx
import { useState, useEffect } from 'react';
import SensitivityAnalysisVisualization from './SensitivityAnalysisVisualization';

function ResultsDashboard({ results, parameters }) {
  const [sensitivityData, setSensitivityData] = useState(null);
  const [loading, setLoading] = useState(false);
  
  // Fetch sensitivity data when results are available
  useEffect(() => {
    if (results) {
      fetchSensitivityData();
    }
  }, [results]);
  
  // Fetch sensitivity analysis data
  const fetchSensitivityData = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/sensitivity-analysis', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          base_params: parameters,
          analysis_type: 'tornado'
        })
      });
      
      const data = await response.json();
      setSensitivityData(data);
    } catch (error) {
      console.error('Error fetching sensitivity data:', error);
    } finally {
      setLoading(false);
    }
  };
  
  // Handle parameter change for custom scenario
  const handleParameterChange = async (customParams) => {
    // Implementation for custom scenario
    // ...
  };
  
  return (
    <div>
      {/* Core results display */}
      {/* ... */}
      
      {/* Sensitivity Analysis Section */}
      <div className="mt-8">
        <h2>Sensitivity Analysis</h2>
        <SensitivityAnalysisVisualization
          sensitivityData={sensitivityData}
          onParameterChange={handleParameterChange}
          baselineValues={parameters}
          loading={loading}
        />
      </div>
    </div>
  );
}
```

## Integration Testing

To ensure proper integration between components, the following tests should be performed:

### Backend Integration Tests

1. **API to Calculation Tests**: Verify that API endpoints correctly invoke calculation modules and return proper results.
   
   ```python
   def test_calculation_integration():
       # Make a request to calculate-all endpoint
       response = client.post('/api/calculate-all', json={
           # Test parameters
       })
       
       # Verify response structure and content
       assert response.status_code == 200
       assert 'production' in response.json
       assert 'financials' in response.json
   ```

2. **API to Authentication Tests**: Verify that protected endpoints correctly enforce authentication.
   
   ```python
   def test_auth_integration():
       # Try accessing protected endpoint without authentication
       response = client.get('/api/projects')
       assert response.status_code == 401
       
       # Register and login a test user
       register_response = client.post('/api/auth/register', json={
           'username': 'testuser',
           'email': 'test@example.com',
           'password': 'password123'
       })
       assert register_response.status_code == 200
       token = register_response.json['token']
       
       # Access protected endpoint with authentication
       auth_response = client.get('/api/projects', headers={
           'Authorization': f'Bearer {token}'
       })
       assert auth_response.status_code == 200
   ```

3. **Sensitivity Analysis Integration**: Verify that sensitivity analysis correctly uses calculation and financial modules.
   
   ```python
   def test_sensitivity_integration():
       # Make a request to sensitivity-analysis endpoint
       response = client.post('/api/sensitivity-analysis', json={
           'base_params': {
               # Test parameters
           },
           'analysis_type': 'tornado'
       })
       
       # Verify response structure and content
       assert response.status_code == 200
       assert 'tornado_data' in response.json
   ```

### Frontend Integration Tests

1. **Authentication Flow**: Verify that login, registration, and authentication state are properly managed.
   
   ```javascript
   test('authentication flow', async () => {
     render(<App />);
     
     // Click login button
     fireEvent.click(screen.getByText(/login/i));
     
     // Fill login form
     fireEvent.change(screen.getByLabelText(/username/i), {
       target: { value: 'testuser' }
     });
     fireEvent.change(screen.getByLabelText(/password/i), {
       target: { value: 'password123' }
     });
     
     // Submit form
     fireEvent.click(screen.getByText(/sign in/i));
     
     // Verify authenticated state
     await waitFor(() => {
       expect(screen.getByText(/welcome, testuser/i)).toBeInTheDocument();
     });
   });
   ```

2. **Project Management Flow**: Verify that projects can be saved, listed, and loaded.
   
   ```javascript
   test('project management flow', async () => {
     // Mock authentication state
     mockAuthContext.isAuthenticated = true;
     mockAuthContext.user = { username: 'testuser' };
     
     render(<App />);
     
     // Click save project button
     fireEvent.click(screen.getByText(/save project/i));
     
     // Fill save form
     fireEvent.change(screen.getByLabelText(/project name/i), {
       target: { value: 'Test Project' }
     });
     
     // Submit form
     fireEvent.click(screen.getByText(/save project/i));
     
     // Verify success message
     await waitFor(() => {
       expect(screen.getByText(/project saved successfully/i)).toBeInTheDocument();
     });
     
     // Click my projects button
     fireEvent.click(screen.getByText(/my projects/i));
     
     // Verify project in list
     await waitFor(() => {
       expect(screen.getByText(/test project/i)).toBeInTheDocument();
     });
     
     // Click load project
     fireEvent.click(screen.getByText(/load/i));
     
     // Verify project loaded
     await waitFor(() => {
       expect(screen.getByDisplayValue(/test project/i)).toBeInTheDocument();
     });
   });
   ```

3. **Sensitivity Analysis Integration**: Verify that sensitivity analysis visualizations correctly display data.
   
   ```javascript
   test('sensitivity analysis integration', async () => {
     // Mock results and parameters
     const mockResults = { /* mock result data */ };
     const mockParameters = { /* mock parameter data */ };
     
     render(<ResultsDashboard results={mockResults} parameters={mockParameters} />);
     
     // Verify sensitivity analysis section
     await waitFor(() => {
       expect(screen.getByText(/sensitivity analysis/i)).toBeInTheDocument();
     });
     
     // Verify charts are rendered
     await waitFor(() => {
       const charts = document.querySelectorAll('svg');
       expect(charts.length).toBeGreaterThan(0);
     });
   });
   ```

## Data Flow Examples

### Example 1: Complete Calculation Flow

```
1. User selects Denver, CO on map (lat: 39.7392, lon: -104.9903)
2. User configures system: 10kW, standard modules, 20° tilt
3. User clicks "Calculate Results"
4. Frontend sends POST to /api/calculate-all with parameters
5. API handler invokes calculate_solar_production() with parameters
6. API handler invokes calculate_financial_metrics() with production data
7. API returns combined production and financial data
8. ResultsDashboard displays production and financial metrics
9. ResultsDashboard requests sensitivity analysis data
10. SensitivityAnalysisVisualization displays tornado charts
```

### Example 2: Project Save and Load Flow

```
1. User completes calculation and views results
2. User clicks "Save Project" button
3. SaveProjectForm modal appears
4. User enters "Denver Residential 10kW" as name
5. User clicks "Save Project" button
6. Frontend sends POST to /api/projects with project data
7. DB Manager saves project to database
8. Success confirmation shown, modal closes
9. Later, user clicks "My Projects" button
10. ProjectList modal shows saved projects
11. User clicks "Load" on "Denver Residential 10kW"
12. Frontend sends GET to /api/projects/{id}
13. Project data loaded into application state
14. Map updates to Denver location
15. Form updates with 10kW configuration
16. Results dashboard shows previous calculation
```

### Example 3: Authentication Flow

```
1. New user clicks "Register" button
2. RegisterForm modal appears
3. User enters username, email, and password
4. Frontend sends POST to /api/auth/register
5. Auth Manager creates user account and issues JWT token
6. Token stored in localStorage
7. User now sees authenticated UI with username
8. User's token included in subsequent API requests
9. Protected operations (save project, etc.) now available
```

## Deployment Integration

For production deployment, the following integration considerations should be addressed:

### Environment Variables

The following environment variables should be configured on the server:

```
# Authentication
JWT_SECRET_KEY=<secure-random-key>

# API Keys
NREL_API_KEY=<your-nrel-api-key>

# Database
DB_PATH=/path/to/production/database.db

# Cache
CACHE_DB_PATH=/path/to/production/cache.db

# Server
PORT=5000
FLASK_ENV=production
```

### CORS Configuration

For production deployment, CORS should be properly configured:

```python
# Development
CORS(app)  # Allows all origins

# Production
CORS(app, resources={
    r"/api/*": {
        "origins": "https://yourdomain.com",
        "methods": ["GET", "POST", "PUT", "DELETE"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})
```

### Frontend Build

For production deployment, the frontend should be built and served from the backend:

```
# Build frontend
cd client
npm run build

# Copy to backend static folder
mkdir -p ../server/static
cp -r build/* ../server/static/

# Configure Flask to serve static files
app = Flask(__name__, static_folder='static', static_url_path='/')

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    if path != "" and os.path.exists(app.static_folder + '/' + path):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, 'index.html')
```

## Troubleshooting Common Integration Issues

### 1. Authentication Failures

**Symptoms:**
- 401 Unauthorized responses from API
- "Session expired" errors
- Unable to access protected endpoints

**Solutions:**
- Verify that JWT_SECRET_KEY is properly set and consistent
- Check that token is properly stored in localStorage
- Verify that token is included in Authorization header
- Check token expiration time
- Ensure AuthProvider is wrapping all components that need authentication

### 2. Cross-Origin Issues

**Symptoms:**
- CORS errors in browser console
- API requests fail from frontend
- "Access-Control-Allow-Origin" missing errors

**Solutions:**
- Ensure CORS is properly configured in Flask
- Check that all required headers are allowed
- Verify that the correct origin is specified in production
- For development, ensure the correct port is allowed

### 3. Cache Integration Issues

**Symptoms:**
- Cache misses despite repeated requests
- Outdated data being served
- High API request volume

**Solutions:**
- Verify cache key generation is consistent
- Check TTL settings for appropriate values
- Ensure proper namespace organization
- Verify cache middleware is correctly applied
- Use cache monitoring tools to inspect cache contents

### 4. Module Dependency Issues

**Symptoms:**
- Import errors
- Module attribute errors
- Unexpected behavior in integrated components

**Solutions:**
- Verify import paths are correct
- Check module initialization order
- Ensure all required modules are installed
- Review module versioning and compatibility
- Use dependency injection for better testability

## Best Practices for Integration

### 1. Proper Error Handling

Ensure consistent error handling across all integration points:

```python
# Backend
try:
    # Operation that might fail
    result = calculation_engine.calculate(params)
    return jsonify(result)
except ValueError as e:
    # Client error
    return jsonify({'error': str(e)}), 400
except Exception as e:
    # Server error
    logger.error(f"Calculation error: {e}")
    return jsonify({'error': 'An internal error occurred'}), 500
```

```jsx
// Frontend
try {
  const response = await fetch('/api/endpoint');
  
  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.error || 'Request failed');
  }
  
  const data = await response.json();
  // Success handling
} catch (error) {
  // Error handling
  setError(error.message);
}
```

### 2. Consistent Data Transformation

Maintain consistent data transformation between frontend and backend:

```python
# Backend
def transform_for_frontend(data):
    """Transform data structure for frontend consumption."""
    return {
        'id': data['id'],
        'name': data['name'],
        'metrics': {
            'payback': data['financials']['payback_period_years'],
            'roi': data['financials']['roi_percent']
        }
    }

@app.route('/api/data')
def get_data():
    data = db_manager.get_data()
    transformed = transform_for_frontend(data)
    return jsonify(transformed)
```

```jsx
// Frontend
function transformForDisplay(data) {
  return {
    id: data.id,
    displayName: data.name,
    paybackYears: data.metrics.payback,
    roiPercent: data.metrics.roi
  };
}

// In component
const displayData = transformForDisplay(responseData);
```

### 3. API Version Management

Implement API versioning for better maintainability:

```python
# Backend
@app.route('/api/v1/calculate')
def calculate_v1():
    # Legacy implementation
    
@app.route('/api/v2/calculate')
def calculate_v2():
    # New implementation with more features
```

```jsx
// Frontend
// Configuration
const API_VERSION = 'v2';
const API_BASE = `/api/${API_VERSION}`;

// Usage
const response = await fetch(`${API_BASE}/calculate`);
```

### 4. Authentication Middleware

Apply consistent authentication middleware:

```python
# Backend
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        auth_header = request.headers.get('Authorization')
        
        if auth_header:
            parts = auth_header.split()
            if len(parts) == 2 and parts[0].lower() == 'bearer':
                token = parts[1]
        
        if not token:
            return jsonify({'error': 'Authentication token is missing'}), 401
        
        try:
            payload = auth_manager.verify_token(token)
            kwargs['user_id'] = payload['sub']
            kwargs['username'] = payload['username']
        except ValueError as e:
            return jsonify({'error': str(e)}), 401
        
        return f(*args, **kwargs)
    return decorated

@app.route('/api/protected')
@token_required
def protected_endpoint(user_id, username):
    # Implementation
```

```jsx
// Frontend
function useAuthenticatedFetch() {
  const { getToken, logout } = useAuth();
  
  return async (url, options = {}) => {
    const token = getToken();
    
    if (!token) {
      throw new Error('Authentication required');
    }
    
    const authOptions = {
      ...options,
      headers: {
        ...options.headers,
        'Authorization': `Bearer ${token}`
      }
    };
    
    const response = await fetch(url, authOptions);
    
    if (response.status === 401) {
      logout();
      throw new Error('Session expired');
    }
    
    return response;
  };
}
```

## Conclusion

This integration guide provides a comprehensive overview of how to connect all components of the Energy Investment Decision Support System. By following these guidelines, developers can ensure proper communication between frontend and backend components, correct data flow between modules, and consistent behavior across the application.

The most critical aspects of integration are:

1. **Authentication flow**: Ensuring proper user authentication and authorization
2. **Data transformation**: Maintaining consistent data structures between components
3. **Error handling**: Implementing robust error handling across integration points
4. **Caching strategy**: Applying appropriate caching for performance optimization

With proper integration, the system provides a seamless user experience while maintaining modularity and extensibility for future enhancements.