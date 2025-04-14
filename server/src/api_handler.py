"""
API Handler for Energy Investment Decision Support System.

This module provides Flask API endpoints for the frontend to request
calculations and data related to renewable energy investments.
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import sys
import json
import hashlib
from datetime import datetime
from functools import wraps
from auth_manager import AuthManager, token_required
from db_manager import DatabaseManager
from cache_manager import CacheManager

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import calculation modules
try:
    from calculation_engine import CalculationEngine
    from financial_modeling import FinancialModel
except ImportError:
    # Adjust import path based on project structure
    from server.src.calculation_engine import CalculationEngine
    from server.src.financial_modeling import FinancialModel

# Create Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Initialize managers
auth_manager = AuthManager()
db_manager = DatabaseManager()
cache_manager = CacheManager()

# Initialize calculation modules
calculation_engine = CalculationEngine()
financial_model = FinancialModel()

# Add cache middleware to wrap API responses in caching logic
def cache_middleware(namespace, tier='short'):
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            # Check if path parameters are in kwargs
            params = {}
            for key, value in kwargs.items():
                if key != 'user_id' and key != 'username':  # Skip auth params
                    params[key] = value
                    
            # Add query parameters from request
            for key, value in request.args.items():
                params[key] = value
                
            # For POST/PUT requests, add a hash of the body
            if request.method in ['POST', 'PUT'] and request.is_json:
                body_hash = hashlib.md5(json.dumps(request.get_json(), sort_keys=True).encode()).hexdigest()
                params['body_hash'] = body_hash
            
            # Try to get cached response
            cached_response = cache_manager.get(namespace, params, tier)
            if cached_response:
                return jsonify(cached_response)
            
            # Call the original function
            result = f(*args, **kwargs)
            
            # Cache the result if it's a JSON response
            if isinstance(result, tuple):
                response, status_code = result
                if status_code == 200 and hasattr(response, 'get_json'):
                    cache_manager.set(namespace, params, response.get_json(), tier)
            else:
                if hasattr(result, 'get_json'):
                    cache_manager.set(namespace, params, result.get_json(), tier)
            
            return result
        return wrapped
    return decorator

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'service': 'Energy Investment Decision Support System API'
    })

@app.route('/api/solar-resource', methods=['GET'])
@cache_middleware('solar_resource', 'long')  # Cache solar resource data for 30 days
def get_solar_resource():
    """Get solar resource data for a specific location."""
    # Get parameters from request
    try:
        lat = float(request.args.get('lat'))
        lon = float(request.args.get('lon'))
    except (TypeError, ValueError):
        return jsonify({'error': 'Invalid latitude or longitude parameters'}), 400
    
    try:
        # Use calculation engine to fetch solar resource data
        nrel_data = calculation_engine.nrel.get_solar_resource(lat, lon)
        
        # Return data
        return jsonify(nrel_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/utility-rates', methods=['GET'])
@cache_middleware('utility_rates', 'medium')  # Cache utility rates for 1 day
def get_utility_rates():
    """Get utility rate data for a specific location."""
    # Get parameters from request
    try:
        lat = float(request.args.get('lat'))
        lon = float(request.args.get('lon'))
    except (TypeError, ValueError):
        return jsonify({'error': 'Invalid latitude or longitude parameters'}), 400
    
    try:
        # Use calculation engine to fetch utility rate data
        utility_data = calculation_engine.get_utility_rates(lat, lon)
        
        # Return data
        return jsonify(utility_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/calculate-production', methods=['POST'])
@cache_middleware('production_calculation', 'medium')  # Cache calculations for 1 day
def calculate_production():
    """Calculate solar energy production for given parameters."""
    # Get JSON data from request
    try:
        data = request.get_json()
        
        # Extract required parameters
        lat = float(data.get('latitude'))
        lon = float(data.get('longitude'))
        system_capacity = float(data.get('systemCapacity', 4.0))
        module_type = int(data.get('moduleType', 1))
        array_type = int(data.get('arrayType', 1))
        losses = float(data.get('losses', 14.0))
        tilt = float(data.get('tilt', 20.0))
        azimuth = float(data.get('azimuth', 180.0))
        data_source = data.get('dataSource', 'both')
        
    except (TypeError, ValueError) as e:
        return jsonify({'error': f'Invalid parameter: {str(e)}'}), 400
    
    try:
        # Use calculation engine to calculate production
        production_data = calculation_engine.calculate_solar_production(
            lat, lon, system_capacity, module_type, losses, 
            array_type, tilt, azimuth, data_source
        )
        
        # Return data
        return jsonify(production_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/calculate-financials', methods=['POST'])
def calculate_financials():
    """Calculate financial metrics for a solar installation."""
    # Get JSON data from request
    try:
        data = request.get_json()
        
        # Check if production data is provided
        if 'production' not in data:
            return jsonify({'error': 'Production data is required'}), 400
        
        production_data = data['production']
        
        # Get utility rates
        lat = float(production_data.get('location', {}).get('lat'))
        lon = float(production_data.get('location', {}).get('lon'))
        utility_rates = calculation_engine.get_utility_rates(lat, lon)
        
        # Extract financial parameters
        system_cost_per_watt = float(data.get('systemCostPerWatt', 2.80))
        incentive_percent = float(data.get('incentivePercent', 0.0))
        incentive_fixed = float(data.get('incentiveFixed', 0.0))
        discount_rate = float(data.get('discountRate', 4.0))
        electricity_inflation = float(data.get('electricityInflation', 2.5))
        analysis_period_years = int(data.get('analysisYears', 25))
        maintenance_cost_per_kw_year = float(data.get('maintenanceCost', 20.0))
        include_sensitivity = bool(data.get('includeSensitivity', False))
        
    except (TypeError, ValueError) as e:
        return jsonify({'error': f'Invalid parameter: {str(e)}'}), 400
    
    try:
        # Use calculation engine to calculate financials
        financial_data = calculation_engine.calculate_financial_metrics(
            production_data, utility_rates, system_cost_per_watt,
            incentive_percent, incentive_fixed, discount_rate / 100,
            electricity_inflation / 100, analysis_period_years,
            maintenance_cost_per_kw_year, include_sensitivity
        )
        
        # Return data
        return jsonify(financial_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/calculate-all', methods=['POST'])
def calculate_all():
    """Calculate both production and financial data in one request."""
    # Get JSON data from request
    try:
        data = request.get_json()
        
        # Extract required parameters
        lat = float(data.get('latitude'))
        lon = float(data.get('longitude'))
        system_capacity = float(data.get('systemCapacity', 4.0))
        module_type = int(data.get('moduleType', 1))
        array_type = int(data.get('arrayType', 1))
        losses = float(data.get('losses', 14.0))
        tilt = float(data.get('tilt', 20.0))
        azimuth = float(data.get('azimuth', 180.0))
        data_source = data.get('dataSource', 'both')
        
        # Financial parameters
        system_cost_per_watt = float(data.get('systemCostPerWatt', 2.80))
        incentive_percent = float(data.get('incentivePercent', 0.0))
        loan_percent = float(data.get('loanPercent', 0.0))
        loan_term = int(data.get('loanTerm', 20))
        loan_rate = float(data.get('loanRate', 5.5))
        analysis_period_years = int(data.get('analysisYears', 25))
        include_sensitivity = bool(data.get('includeSensitivity', False))
        
    except (TypeError, ValueError) as e:
        return jsonify({'error': f'Invalid parameter: {str(e)}'}), 400
    
    try:
        # Step 1: Calculate production
        production_data = calculation_engine.calculate_solar_production(
            lat, lon, system_capacity, module_type, losses, 
            array_type, tilt, azimuth, data_source
        )
        
        # Step 2: Get utility rates
        utility_rates = calculation_engine.get_utility_rates(lat, lon)
        
        # Step 3: Calculate financials
        financial_data = calculation_engine.calculate_financial_metrics(
            production_data, utility_rates, system_cost_per_watt,
            incentive_percent, 0, 0.04, 0.025, analysis_period_years,
            20, include_sensitivity
        )
        
        # If loan parameters are provided, add detailed financial model
        if loan_percent > 0:
            # Get detailed financials from financial model
            system_capacity_kw = system_capacity
            average_production = None
            
            # Determine which production estimate to use
            if 'comparison' in production_data:
                # If we have both sources, use the average
                average_production = production_data['comparison']['average_production_kwh']
            elif 'nrel' in production_data and 'error' not in production_data['nrel']:
                average_production = production_data['nrel']['annual_production_kwh']
            elif 'nasa' in production_data and 'error' not in production_data['nasa']:
                average_production = production_data['nasa']['annual_production_kwh']
            
            if average_production:
                electricity_rate = utility_rates.get('residential_rate', 0.12)
                
                # Create parameters for detailed financial model
                financial_params = {
                    "system_cost_per_watt": system_cost_per_watt,
                    "federal_itc_percent": incentive_percent,
                    "loan_amount_percent": loan_percent,
                    "loan_term_years": loan_term,
                    "loan_rate_percent": loan_rate,
                    "analysis_period_years": analysis_period_years
                }
                
                detailed_financials = financial_model.calculate_detailed_financials(
                    system_capacity_kw, average_production, electricity_rate, financial_params
                )
                
                # Add to results
                financial_data['detailed_financials'] = detailed_financials
        
        # Return complete results
        return jsonify({
            'production': production_data,
            'financials': financial_data
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/scenario-analysis', methods=['POST'])
def scenario_analysis():
    """Perform scenario analysis with different parameter sets."""
    # Get JSON data from request
    try:
        data = request.get_json()
        
        # Extract required parameters
        system_capacity = float(data.get('systemCapacity', 4.0))
        annual_production = float(data.get('annualProduction'))
        electricity_rate = float(data.get('electricityRate', 0.12))
        
        # Optional financial parameters
        params = data.get('financialParams', {})
        
    except (TypeError, ValueError) as e:
        return jsonify({'error': f'Invalid parameter: {str(e)}'}), 400
    
    try:
        # Use financial model to perform scenario analysis
        scenarios = financial_model.perform_scenario_analysis(
            system_capacity, annual_production, electricity_rate, params
        )
        
        # Return data
        return jsonify(scenarios)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/sensitivity-analysis', methods=['POST'])
def sensitivity_analysis():
    """Perform sensitivity analysis for given parameters."""
    try:
        data = request.get_json()
        
        # Import the sensitivity analyzer
        from sensitivity_analyzer import SensitivityAnalyzer
        
        # Create analyzer with existing calculation engine and financial model
        analyzer = SensitivityAnalyzer(calculation_engine, financial_model)
        
        # Extract base parameters from request
        base_params = data.get('base_params', {})
        analysis_type = data.get('analysis_type', 'tornado')
        
        if analysis_type == 'tornado':
            # Generate tornado chart data
            result = analyzer.analyze_multiple_parameters(base_params)
        elif analysis_type == 'scenario':
            # Compare predefined scenarios
            scenarios = data.get('scenarios', {})
            result = analyzer.compare_scenarios(base_params, scenarios)
        elif analysis_type == 'custom':
            # Create custom scenario
            custom_params = data.get('custom_params', {})
            result = analyzer.create_custom_scenario(base_params, custom_params)
        else:
            return jsonify({'error': 'Invalid analysis type'}), 400
            
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Authentication endpoints
@app.route('/api/auth/register', methods=['POST'])
def register():
    """Register a new user."""
    try:
        data = request.get_json()
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        
        if not username or not email or not password:
            return jsonify({'error': 'Missing required fields'}), 400
        
        user = auth_manager.register_user(username, email, password)
        return jsonify(user)
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/auth/login', methods=['POST'])
def login():
    """Authenticate a user and return a token."""
    try:
        data = request.get_json()
        username_or_email = data.get('username_or_email')
        password = data.get('password')
        
        if not username_or_email or not password:
            return jsonify({'error': 'Missing username/email or password'}), 400
        
        user = auth_manager.login_user(username_or_email, password)
        return jsonify(user)
    except ValueError as e:
        return jsonify({'error': str(e)}), 401
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/auth/verify', methods=['GET'])
@token_required
def verify_token(user_id, username):
    """Verify a user's authentication token."""
    try:
        user = auth_manager.get_user_profile(user_id)
        return jsonify(user)
    except ValueError as e:
        return jsonify({'error': str(e)}), 401
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Project management endpoints
@app.route('/api/projects', methods=['GET'])
@token_required
def get_projects(user_id, username):
    """Get all projects for the current user."""
    try:
        projects = db_manager.get_user_projects(user_id)
        return jsonify({'projects': projects})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/projects/<project_id>', methods=['GET'])
@token_required
def get_project(project_id, user_id, username):
    """Get a project by ID."""
    try:
        project = db_manager.get_project(project_id, user_id)
        if not project:
            return jsonify({'error': 'Project not found'}), 404
        return jsonify(project)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/projects', methods=['POST'])
@token_required
def create_project(user_id, username):
    """Create a new project."""
    try:
        data = request.get_json()
        
        if not data.get('name'):
            return jsonify({'error': 'Project name is required'}), 400
        
        project_id = db_manager.save_project(
            user_id=user_id,
            name=data.get('name'),
            description=data.get('description'),
            location_lat=data.get('location_lat'),
            location_lon=data.get('location_lon'),
            parameters=data.get('parameters'),
            results=data.get('results')
        )
        
        project = db_manager.get_project(project_id)
        return jsonify(project), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/projects/<project_id>', methods=['PUT'])
@token_required
def update_project(project_id, user_id, username):
    """Update an existing project."""
    try:
        # First check if project exists and belongs to user
        existing_project = db_manager.get_project(project_id, user_id)
        if not existing_project:
            return jsonify({'error': 'Project not found'}), 404
        
        data = request.get_json()
        
        if not data.get('name'):
            return jsonify({'error': 'Project name is required'}), 400
        
        db_manager.save_project(
            user_id=user_id,
            name=data.get('name'),
            description=data.get('description'),
            location_lat=data.get('location_lat'),
            location_lon=data.get('location_lon'),
            parameters=data.get('parameters'),
            results=data.get('results'),
            project_id=project_id
        )
        
        updated_project = db_manager.get_project(project_id)
        return jsonify(updated_project)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/projects/<project_id>', methods=['DELETE'])
@token_required
def delete_project(project_id, user_id, username):
    """Delete a project."""
    try:
        result = db_manager.delete_project(project_id, user_id)
        if not result:
            return jsonify({'error': 'Project not found'}), 404
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Admin cache endpoints
@app.route('/api/admin/cache/stats', methods=['GET'])
@token_required
def get_cache_stats(user_id, username):
    """Get cache statistics."""
    # Check if user is admin (implement your admin check)
    is_admin = True  # Replace with actual admin check
    if not is_admin:
        return jsonify({'error': 'Admin access required'}), 403
    
    stats = cache_manager.get_stats()
    return jsonify(stats)

@app.route('/api/admin/cache/clear', methods=['POST'])
@token_required
def clear_cache(user_id, username):
    """Clear the cache."""
    # Check if user is admin
    is_admin = True  # Replace with actual admin check
    if not is_admin:
        return jsonify({'error': 'Admin access required'}), 403
    
    data = request.get_json()
    tier = data.get('tier') if data else None
    
    count = cache_manager.clear(tier)
    return jsonify({'success': True, 'count': count})

@app.route('/api/admin/cache/invalidate', methods=['POST'])
@token_required
def invalidate_cache(user_id, username):
    """Invalidate cache entries by namespace."""
    # Check if user is admin
    is_admin = True  # Replace with actual admin check
    if not is_admin:
        return jsonify({'error': 'Admin access required'}), 403
    
    data = request.get_json()
    if not data or 'namespace' not in data:
        return jsonify({'error': 'Namespace is required'}), 400
    
    namespace = data['namespace']
    key_components = data.get('key_components')
    
    count = cache_manager.invalidate(namespace, key_components)
    return jsonify({'success': True, 'count': count})

@app.route('/api/admin/cache/cleanup', methods=['POST'])
@token_required
def cleanup_cache(user_id, username):
    """Clean up expired cache entries."""
    # Check if user is admin
    is_admin = True  # Replace with actual admin check
    if not is_admin:
        return jsonify({'error': 'Admin access required'}), 403
    
    count = cache_manager.cleanup_expired()
    return jsonify({'success': True, 'count': count})

if __name__ == '__main__':
    # Run the Flask app
    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', port=port, debug=True)