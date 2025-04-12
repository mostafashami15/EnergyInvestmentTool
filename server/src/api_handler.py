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
from datetime import datetime

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import calculation modules
from calculation_engine import CalculationEngine
from financial_modeling import FinancialModel

# Create Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Initialize calculation modules
calculation_engine = CalculationEngine()
financial_model = FinancialModel()

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'service': 'Energy Investment Decision Support System API'
    })

@app.route('/api/solar-resource', methods=['GET'])
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
    """Perform sensitivity analysis for key parameters."""
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
        # Use financial model to perform sensitivity analysis
        sensitivity = financial_model.perform_sensitivity_analysis(
            system_capacity, annual_production, electricity_rate, params
        )
        
        # Return data
        return jsonify(sensitivity)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Run the Flask app
    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', port=port, debug=True)