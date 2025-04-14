# API Handler Documentation

## Overview

The API Handler (`api_handler.py`) serves as the backend interface for the Energy Investment Decision Support System, providing RESTful endpoints that connect the frontend user interface with the calculation, financial modeling, authentication, project management, and caching modules. It handles requests for solar resource data, utility rates, production calculations, financial analysis, user authentication, project management, and cache administration.

## Key Features

1. **RESTful API design**: Well-structured endpoints following REST principles
2. **Request validation**: Input validation and error handling
3. **Calculation orchestration**: Coordinates between different calculation modules
4. **Cross-origin support**: Enables frontend-backend communication
5. **Authentication**: User registration, login, and token verification
6. **Project management**: Saving, loading, and deleting user projects
7. **Caching system**: Performance optimization with multi-tiered caching
8. **Comprehensive documentation**: Endpoint descriptions and usage examples

## Architecture

```
┌───────────────────────────────────────────────────────────────────────┐
│                        Flask Application                              │
├───────────┬───────────┬───────────────┬───────────────┬───────────────┤
│   Data    │Calculation│  Financial    │  Auth & User  │    Cache      │
│ Endpoints │ Endpoints │  Endpoints    │  Management   │  Management   │
├───────────┼───────────┼───────────────┼───────────────┼───────────────┤
│/solar-    │/calculate-│/scenario-     │/auth/register │/admin/cache/  │
│resource   │production │analysis       │/auth/login    │stats          │
├───────────┼───────────┼───────────────┼───────────────┼───────────────┤
│/utility-  │/calculate-│/sensitivity-  │/auth/verify   │/admin/cache/  │
│rates      │financials │analysis       │/projects      │clear          │
├───────────┼───────────┼───────────────┼───────────────┼───────────────┤
│           │/calculate-│               │               │/admin/cache/  │
│           │all        │               │               │invalidate     │
└─────┬─────┴─────┬─────┴───────┬───────┴────────┬──────┴───────┬───────┘
      │           │             │                │              │
┌─────▼─────┐┌────▼──────┐┌─────▼─────┐┌─────────▼───────┐┌─────▼──────┐
│Calculation││Financial  ││Sensitivity││  Auth & DB      ││   Cache    │
│  Engine   ││   Model   ││ Analyzer  ││   Managers      ││  Manager   │
└───────────┘└───────────┘└───────────┘└─────────────────┘└────────────┘
```

## Core Modules Integration

The API Handler integrates with five main backend modules:

1. **Calculation Engine**: For solar production calculations and utility rate data
2. **Financial Model**: For financial metrics, scenario analysis, and ROI calculations
3. **Sensitivity Analyzer**: For parameter impact analysis and scenario comparison
4. **Auth/DB Managers**: For user authentication and project data persistence
5. **Cache Manager**: For optimizing performance through multi-tiered caching

## Endpoint Documentation

### 1. Health Check

```
GET /api/health
```

Returns the current status of the API service.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-04-12T14:30:00.000Z",
  "service": "Energy Investment Decision Support System API"
}
```

### 2. Solar Resource Data

```
GET /api/solar-resource?lat=<latitude>&lon=<longitude>
```

Retrieves solar resource data for a specific geographic location.

**Parameters:**
- `lat` (float): Latitude of the location
- `lon` (float): Longitude of the location

**Response:**
```json
{
  "version": "1.0.0",
  "metadata": {
    "sources": ["NREL Solar Resource Database"]
  },
  "outputs": {
    "avg_dni": {
      "annual": 6.32,
      "monthly": [5.1, 5.7, 6.2, 6.4, 6.7, 7.1, 7.3, 7.0, 6.5, 6.0, 5.5, 5.0]
    },
    "avg_ghi": {
      "annual": 5.21,
      "monthly": [3.5, 4.2, 5.0, 5.8, 6.2, 6.5, 6.4, 6.0, 5.4, 4.5, 3.7, 3.2]
    }
  }
}
```

### 3. Utility Rates

```
GET /api/utility-rates?lat=<latitude>&lon=<longitude>&radius=<radius>
```

Retrieves utility rate data for a specific geographic location.

**Parameters:**
- `lat` (float): Latitude of the location
- `lon` (float): Longitude of the location
- `radius` (float, optional): Radius in miles to search (default: 0)

**Response:**
```json
{
  "location": {
    "lat": 39.7392,
    "lon": -104.9903
  },
  "utility": "Xcel Energy",
  "commercial_rate": 0.1034,
  "residential_rate": 0.1275,
  "industrial_rate": 0.0891
}
```

### 4. Calculate Production

```
POST /api/calculate-production
```

Calculates solar energy production for a given location and system parameters.

**Request Body:**
```json
{
  "latitude": 39.7392,
  "longitude": -104.9903,
  "systemCapacity": 10.0,
  "moduleType": 1,
  "arrayType": 2,
  "losses": 14.0,
  "tilt": 20.0,
  "azimuth": 180.0,
  "dataSource": "both"
}
```

**Response:**
See the Calculation Engine documentation for the detailed response structure.

### 5. Calculate Financials

```
POST /api/calculate-financials
```

Calculates financial metrics for a solar installation based on production data.

**Request Body:**
```json
{
  "production": {
    // Production data object from calculate-production
  },
  "systemCostPerWatt": 2.80,
  "incentivePercent": 30.0,
  "incentiveFixed": 0.0,
  "discountRate": 4.0,
  "electricityInflation": 2.5,
  "analysisYears": 25,
  "maintenanceCost": 20.0,
  "includeSensitivity": true
}
```

**Response:**
See the Financial Modeling documentation for the detailed response structure.

### 6. Calculate All

```
POST /api/calculate-all
```

Comprehensive endpoint that performs both production and financial calculations in one request.

**Request Body:**
```json
{
  "latitude": 39.7392,
  "longitude": -104.9903,
  "systemCapacity": 10.0,
  "moduleType": 1,
  "arrayType": 2,
  "losses": 14.0,
  "tilt": 20.0,
  "azimuth": 180.0,
  "dataSource": "both",
  "systemCostPerWatt": 2.80,
  "incentivePercent": 30.0,
  "loanPercent": 70.0,
  "loanTerm": 20,
  "loanRate": 5.5,
  "analysisYears": 25,
  "includeSensitivity": false
}
```

**Response:**
Combined response with both production and financial data.
```json
{
  "production": {
    // Production calculation results
  },
  "financials": {
    // Financial calculation results
  }
}
```

### 7. Scenario Analysis

```
POST /api/scenario-analysis
```

Performs scenario analysis with different parameter sets.

**Request Body:**
```json
{
  "systemCapacity": 10.0,
  "annualProduction": 15000.0,
  "electricityRate": 0.12,
  "financialParams": {
    "system_cost_per_watt": 2.80,
    "federal_itc_percent": 30.0,
    "loan_amount_percent": 70.0,
    "loan_term_years": 20,
    "loan_rate_percent": 5.5
  }
}
```

**Response:**
See the Financial Modeling documentation for the detailed scenario analysis response structure.

### 8. Sensitivity Analysis

```
POST /api/sensitivity-analysis
```

Performs sensitivity analysis for key parameters.

**Request Body:**
```json
{
  "base_params": {
    "latitude": 39.7392,
    "longitude": -104.9903,
    "systemCapacity": 10.0,
    "moduleType": 1,
    "arrayType": 2,
    "losses": 14.0,
    "tilt": 20.0,
    "azimuth": 180.0,
    "systemCostPerWatt": 2.80,
    "incentivePercent": 30.0
  },
  "analysis_type": "tornado"
}
```

**Response:**
See the Sensitivity Analyzer documentation for the detailed sensitivity analysis response structure.

### 9. User Registration

```
POST /api/auth/register
```

Registers a new user in the system.

**Request Body:**
```json
{
  "username": "user123",
  "email": "user@example.com",
  "password": "securepassword"
}
```

**Response:**
```json
{
  "user_id": "a1b2c3d4-e5f6-7890-a1b2-c3d4e5f67890",
  "username": "user123",
  "email": "user@example.com",
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

### 10. User Login

```
POST /api/auth/login
```

Authenticates a user and returns a token.

**Request Body:**
```json
{
  "username_or_email": "user123",
  "password": "securepassword"
}
```

**Response:**
```json
{
  "user_id": "a1b2c3d4-e5f6-7890-a1b2-c3d4e5f67890",
  "username": "user123",
  "email": "user@example.com",
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

### 11. Token Verification

```
GET /api/auth/verify
```

Verifies a user's authentication token and returns user information.

**Headers:**
- `Authorization`: Bearer token

**Response:**
```json
{
  "user_id": "a1b2c3d4-e5f6-7890-a1b2-c3d4e5f67890",
  "username": "user123",
  "email": "user@example.com",
  "created_at": "2025-01-15T12:30:45.000Z",
  "last_login": "2025-04-12T14:30:00.000Z"
}
```

### 12. Get Projects List

```
GET /api/projects
```

Retrieves all projects for the authenticated user.

**Headers:**
- `Authorization`: Bearer token

**Response:**
```json
{
  "projects": [
    {
      "id": "p1q2r3s4-t5u6-7890-v1w2-x3y4z5a67890",
      "name": "Residential Solar Project",
      "description": "10kW system for my home",
      "location_lat": 39.7392,
      "location_lon": -104.9903,
      "created_at": "2025-03-10T15:20:30.000Z",
      "updated_at": "2025-03-15T09:45:12.000Z"
    },
    // More projects...
  ]
}
```

### 13. Get Project Details

```
GET /api/projects/<project_id>
```

Retrieves details for a specific project.

**Headers:**
- `Authorization`: Bearer token

**Parameters:**
- `project_id`: Project ID

**Response:**
```json
{
  "id": "p1q2r3s4-t5u6-7890-v1w2-x3y4z5a67890",
  "name": "Residential Solar Project",
  "description": "10kW system for my home",
  "location_lat": 39.7392,
  "location_lon": -104.9903,
  "parameters": {
    "systemCapacity": 10.0,
    "moduleType": 1,
    // Other parameters...
  },
  "results": {
    "production": {
      // Production data
    },
    "financials": {
      // Financial data
    }
  },
  "created_at": "2025-03-10T15:20:30.000Z",
  "updated_at": "2025-03-15T09:45:12.000Z"
}
```

### 14. Create Project

```
POST /api/projects
```

Creates a new project.

**Headers:**
- `Authorization`: Bearer token

**Request Body:**
```json
{
  "name": "Residential Solar Project",
  "description": "10kW system for my home",
  "location_lat": 39.7392,
  "location_lon": -104.9903,
  "parameters": {
    "systemCapacity": 10.0,
    "moduleType": 1,
    // Other parameters...
  },
  "results": {
    // Calculation results
  }
}
```

**Response:**
The created project object.

### 15. Update Project

```
PUT /api/projects/<project_id>
```

Updates an existing project.

**Headers:**
- `Authorization`: Bearer token

**Parameters:**
- `project_id`: Project ID

**Request Body:**
Same as for creating a project.

**Response:**
The updated project object.

### 16. Delete Project

```
DELETE /api/projects/<project_id>
```

Deletes a project.

**Headers:**
- `Authorization`: Bearer token

**Parameters:**
- `project_id`: Project ID

**Response:**
```json
{
  "success": true
}
```

### 17. Cache Statistics

```
GET /api/admin/cache/stats
```

Gets statistics about the cache system.

**Headers:**
- `Authorization`: Bearer token (admin)

**Response:**
```json
{
  "memory_cache": {
    "enabled": true,
    "size": 245,
    "max_size": 1000,
    "hits": 1245,
    "misses": 567,
    "hit_ratio": 0.687,
    "inserts": 812,
    "evictions": 45
  },
  "disk_cache": {
    "enabled": true,
    "tiers": {
      "short": {
        "count": 150,
        "size_bytes": 2456789,
        "hits": 789,
        "misses": 234,
        "hit_ratio": 0.771,
        "inserts": 385,
        "evictions": 35,
        "ttl_seconds": 3600,
        "description": "Short-term cache for API responses during user sessions"
      },
      // Other tiers...
    },
    "total": {
      "count": 450,
      "size_bytes": 8456789,
      "hits": 2345,
      "misses": 678,
      "hit_ratio": 0.776,
      "inserts": 1128,
      "evictions": 112
    }
  }
}
```

### 18. Clear Cache

```
POST /api/admin/cache/clear
```

Clears the cache.

**Headers:**
- `Authorization`: Bearer token (admin)

**Request Body:**
```json
{
  "tier": "short"  // Optional: clear specific tier or all tiers if null
}
```

**Response:**
```json
{
  "success": true,
  "count": 150  // Number of entries cleared
}
```

### 19. Invalidate Cache

```
POST /api/admin/cache/invalidate
```

Invalidates cache entries by namespace.

**Headers:**
- `Authorization`: Bearer token (admin)

**Request Body:**
```json
{
  "namespace": "solar_resource",
  "key_components": null  // Optional: specific key components or null for entire namespace
}
```

**Response:**
```json
{
  "success": true,
  "count": 87  // Number of entries invalidated
}
```

### 20. Cleanup Expired Cache Entries

```
POST /api/admin/cache/cleanup
```

Cleans up expired cache entries.

**Headers:**
- `Authorization`: Bearer token (admin)

**Response:**
```json
{
  "success": true,
  "count": 45  // Number of expired entries removed
}
```

## Implementation Details

### Authentication and Authorization

The API uses JWT (JSON Web Token) for authentication and authorization:

1. **Token Generation**: On login or registration, a JWT token is generated and returned to the client
2. **Token Verification**: Requests to protected endpoints require the token in the Authorization header
3. **Token Required Decorator**: The `token_required` decorator is used to protect endpoints

```python
@token_required
def protected_endpoint(user_id, username):
    # This endpoint is protected
    # user_id and username are extracted from the token
    pass
```

### Project Management

Project management endpoints implement CRUD operations:

1. **Create**: Save a new project to the database
2. **Read**: Retrieve project details by ID or all projects for a user
3. **Update**: Modify an existing project
4. **Delete**: Remove a project from the database

The endpoints ensure that users can only access their own projects.

### Caching Middleware

The API implements a caching middleware that:

1. **Checks Cache**: Looks for cached responses before executing the handler
2. **Stores Results**: Caches the response if not already cached
3. **Tiered Approach**: Uses different cache tiers based on data characteristics

```python
@cache_middleware('namespace', 'tier')
def cacheable_endpoint():
    # This endpoint's responses will be cached
    pass
```

### Error Handling

The API implements a consistent error handling approach:

1. **Parameter validation errors**: 400 Bad Request
2. **Authentication errors**: 401 Unauthorized
3. **Authorization errors**: 403 Forbidden
4. **Resource not found**: 404 Not Found
5. **Calculation errors**: 500 Internal Server Error

Example error response:
```json
{
  "error": "Invalid parameter: latitude must be between -90 and 90"
}
```

## Security Considerations

1. **JWT Authentication**: Secure token-based authentication
2. **Password Hashing**: PBKDF2 with SHA-256 for secure password storage
3. **Parameter Validation**: All inputs validated to prevent injection attacks
4. **HTTPS Requirement**: API should be deployed behind HTTPS in production
5. **Admin Access Control**: Restricted access to admin endpoints

## Performance Optimizations

1. **Multi-tiered Caching**:
   - Short-term (1 hour): For API responses during user sessions
   - Medium-term (1 day): For frequently accessed locations
   - Long-term (30 days): For slow-changing data like solar radiation

2. **Response Caching**:
   - Calculation results cached to reduce computation
   - Solar resource data cached to reduce API calls
   - Utility rate data cached to improve response time

3. **Database Optimization**:
   - Indexed queries for user projects
   - Efficient project storage and retrieval

## Deployment Considerations

1. **Environment Variables**:
   - `JWT_SECRET_KEY`: Secret key for JWT token signing
   - `DB_PATH`: Path to SQLite database file
   - `CACHE_DB_PATH`: Path to cache database file
   - `PORT`: Server port (default: 5001)

2. **Production Server**:
   - Use a production WSGI server (Gunicorn, uWSGI)
   - Run behind a reverse proxy (Nginx, Apache)
   - Implement proper logging

3. **Error Logging**:
   - Use structured logging for errors
   - Configure log rotation and management

## Integration with Frontend

The API is designed to integrate seamlessly with the React frontend:

1. **Authentication Flow**:
   - Frontend stores JWT token in localStorage
   - Token included in Authorization header for API requests
   - Token refreshed as needed

2. **Project Management**:
   - Frontend provides project list and management UI
   - API handles data persistence and validation

3. **Calculation Flow**:
   - Frontend collects user inputs
   - API performs calculations and returns results
   - Frontend visualizes the results