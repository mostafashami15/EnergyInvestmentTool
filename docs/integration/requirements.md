# Energy Investment Decision Support System - Requirements and Dependencies

This document outlines all required dependencies for the Energy Investment Decision Support System project, including both backend (Python) and frontend (JavaScript/React) dependencies.

## Backend Dependencies

The backend requires Python 3.11 or higher and uses Poetry for dependency management.

### Core Dependencies

```toml
[tool.poetry.dependencies]
python = ">=3.11,<4.0"
flask = "^3.1.0"
flask-cors = "^5.0.1"
numpy = "^2.2.4"
requests = "^2.32.3"
python-dotenv = "^1.0.0"

# JWT Authentication
PyJWT = "^2.8.0"

# Date handling
python-dateutil = "^2.8.2"

# Math and calculation libraries
scipy = "^1.12.0"
pandas = "^2.2.0"
```

### Development Dependencies

```toml
[tool.poetry.group.dev.dependencies]
pytest = "^8.3.5"
black = "^24.3.0"
flake8 = "^7.0.0"
isort = "^5.13.2"
pytest-cov = "^4.1.0"
```

### API Dependencies

The system integrates with the following external APIs:

1. **NREL (National Renewable Energy Laboratory) APIs**
   - PVWatts API: Solar energy production calculation
   - Solar Resource Data API: Solar radiation values
   - Utility Rates API: Electricity cost data
   - DSIRE API: Incentives and policies (planned)

2. **NASA POWER (Prediction of Worldwide Energy Resources) API**
   - Provides global solar radiation and meteorological data
   - Supports multiple temporal resolutions (hourly, daily, monthly)

## Frontend Dependencies

The frontend requires Node.js 14 or higher and uses npm for package management.

### React and Core UI

```json
{
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-scripts": "5.0.1"
  }
}
```

### UI Components and Styling

```json
{
  "dependencies": {
    "tailwindcss": "^3.4.1",
    "postcss": "^8.4.31",
    "autoprefixer": "^10.4.16",
    "leaflet": "^1.9.4",
    "recharts": "^2.10.3"
  }
}
```

### Authentication and API Communication

```json
{
  "dependencies": {
    "jwt-decode": "^4.0.0",
    "prop-types": "^15.8.1"
  }
}
```

### Development Tools

```json
{
  "devDependencies": {
    "@testing-library/jest-dom": "^6.1.5",
    "@testing-library/react": "^14.1.2",
    "@testing-library/user-event": "^14.5.1",
    "eslint": "^8.55.0",
    "eslint-plugin-react": "^7.33.2",
    "eslint-plugin-react-hooks": "^4.6.0"
  }
}
```

## Newly Added Dependencies

### Backend (Python)

The following dependencies have been added to support the new advanced features:

```toml
# Authentication
PyJWT = "^2.8.0"

# Caching
# (Built using native Python libraries - no additional dependencies)

# Sensitivity Analysis
# (Built on top of existing numerical libraries - no additional dependencies)
```

### Frontend (JavaScript)

The following dependencies have been added to support the new advanced features:

```json
{
  "dependencies": {
    "jwt-decode": "^4.0.0",
    "prop-types": "^15.8.1"
  }
}
```

## Installation Instructions

### Backend Setup

1. Install Poetry (dependency management tool):
   ```bash
   curl -sSL https://install.python-poetry.org | python3 -
   ```

2. Set up the project with all dependencies:
   ```bash
   poetry install
   ```

3. Install PyJWT specifically for authentication:
   ```bash
   poetry add PyJWT
   ```

4. Set up environment variables:
   Create a `.env` file with the following variables:
   ```
   JWT_SECRET_KEY=your_secure_random_key
   NREL_API_KEY=your_nrel_api_key
   ```

### Frontend Setup

1. Install Node.js dependencies:
   ```bash
   cd client
   npm install
   ```

2. Install additional dependencies for new features:
   ```bash
   npm install jwt-decode prop-types
   ```

## Development Environment Requirements

### Backend Development
- Python 3.11 or higher
- Poetry 1.6 or higher
- SQLite 3.x (included with Python)
- API keys for NREL services

### Frontend Development
- Node.js 14 or higher
- npm 7 or higher
- Modern web browser with developer tools

### Recommended IDE Setup
- Visual Studio Code with the following extensions:
  - Python extension
  - React extension
  - ESLint
  - Prettier
  - SQLite Explorer

## Testing Requirements

### Backend Testing
- pytest for unit and integration testing
- pytest-cov for test coverage analysis
- API mocking for external service testing

### Frontend Testing
- Jest for unit testing
- React Testing Library for component testing
- Mock Service Worker for API mocking

## Deployment Requirements

### Server Requirements
- Linux server (Ubuntu 22.04 LTS recommended)
- Python 3.11 or higher
- Node.js 14 or higher (for frontend build)
- Nginx as a reverse proxy
- HTTPS certificate (Let's Encrypt recommended)
- Adequate disk space for database and cache

### Environment Variables for Production
```
JWT_SECRET_KEY=<secure-random-key>
NREL_API_KEY=<your-nrel-api-key>
DB_PATH=/path/to/production/database.db
CACHE_DB_PATH=/path/to/production/cache.db
FLASK_ENV=production
```

## Version Compatibility Notes

- **PyJWT**: Version 2.8.0 is required for proper JWT token handling.
- **Flask**: Version 3.1.0 or higher is recommended for improved CORS handling.
- **Recharts**: Version 2.10.3 or higher is required for proper tornado chart rendering.
- **Leaflet**: Version 1.9.4 is tested and confirmed working with the map component.

## Dependencies to Be Added in Future Phases

### Backend (Planned)
```toml
# Machine Learning (Phase 6)
scikit-learn = "^1.4.0"
tensorflow = "^2.16.0"
joblib = "^1.3.2"

# Advanced Database (Phase 5 - optional upgrade from SQLite)
sqlalchemy = "^2.0.23"
psycopg2-binary = "^2.9.9"  # For PostgreSQL
```

### Frontend (Planned)
```json
{
  "dependencies": {
    "d3": "^7.8.5",           // Advanced visualizations (Phase 5)
    "three": "^0.160.0",      // 3D visualizations (Phase 5)
    "react-router-dom": "^6.21.1",  // Routing for larger application (Phase 5)
    "i18next": "^23.7.11"     // Internationalization (Phase 5)
  }
}
```