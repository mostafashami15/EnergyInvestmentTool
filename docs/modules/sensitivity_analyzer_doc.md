# Sensitivity Analysis Module Documentation

## Overview

The Sensitivity Analysis Module (`sensitivity_analyzer.py`) provides comprehensive functionality for analyzing how changes in key parameters affect financial outcomes for renewable energy investments. It enables users to understand parameter impact, compare scenarios, and create custom parameter sets for detailed analysis.

## Key Features

1. **Parameter sensitivity analysis**: Measure how changes in individual parameters affect financial outcomes
2. **Multi-parameter tornado charts**: Visualize the relative impact of different parameters
3. **Scenario comparison**: Compare predefined scenarios (optimistic, pessimistic, etc.)
4. **Custom scenario creation**: Generate results for user-defined parameter combinations
5. **Data preparation for visualization**: Format data for frontend tornado charts and comparisons

## Architecture

```
┌────────────────────────────────────────────────────────┐
│               Sensitivity Analyzer                     │
├───────────────────┬────────────────┬──────────────────┤
│  Parameter        │  Scenario      │  Custom          │
│  Analysis         │  Comparison    │  Scenarios       │
├───────────────────┼────────────────┼──────────────────┤
│ Analyze Parameter │ Compare        │ Create Custom    │
│ Sensitivity       │ Scenarios      │ Scenario         │
├───────────────────┼────────────────┼──────────────────┤
│ Analyze Multiple  │ Calculate      │ Calculate        │
│ Parameters        │ Financial      │ Financial        │
│                   │ Metrics        │ Metrics          │
└────────────┬──────┴────────┬───────┴────────┬───────┘
             │               │                │
       ┌─────▼─────┐   ┌─────▼─────┐    ┌─────▼─────┐
       │Calculation│   │ Financial │    │  Metrics  │
       │  Engine   │   │   Model   │    │Formatting │
       └───────────┘   └───────────┘    └───────────┘
```

## Core Classes and Methods

### `SensitivityAnalyzer` Class

The main class that provides functionality for sensitivity analysis.

#### Initialization:
```python
def __init__(self, calculation_engine=None, financial_model=None):
    """Initialize the sensitivity analyzer with calculation engines.
    
    Args:
        calculation_engine: Instance of CalculationEngine for production calculations
        financial_model: Instance of FinancialModel for financial calculations
    """
    self.calculation_engine = calculation_engine or CalculationEngine()
    self.financial_model = financial_model or FinancialModel()
    
    # Default parameter ranges for sensitivity analysis
    self.default_ranges = {
        "system_cost_per_watt": [-20, -10, 0, 10, 20],  # Percentage change
        "electricity_rate": [-20, -10, 0, 10, 20],  # Percentage change
        "annual_production": [-20, -10, 0, 10, 20],  # Percentage change
        "electricity_inflation": [-2, -1, 0, 1, 2],  # Absolute change (percentage points)
        "panel_degradation": [-0.2, -0.1, 0, 0.1, 0.2],  # Absolute change (percentage points)
        "discount_rate": [-2, -1, 0, 1, 2],  # Absolute change (percentage points)
        "loan_rate": [-2, -1, 0, 1, 2],  # Absolute change (percentage points)
    }
    
    # Default metrics to evaluate
    self.default_metrics = [
        "payback_period_years",
        "roi_percent", 
        "npv", 
        "irr_percent", 
        "lcoe_per_kwh",
        "lifetime_savings"
    ]
```

#### Key Methods:

1. **`analyze_parameter_sensitivity`**
   ```python
   def analyze_parameter_sensitivity(self, 
                                   base_params, 
                                   parameter_name, 
                                   variation_range=None, 
                                   metrics=None):
       """Analyze how changes in a single parameter affect financial outcomes.
       
       Args:
           base_params: Dictionary of base parameters for the calculation
           parameter_name: Name of parameter to vary
           variation_range: List of variation values (% for relative, absolute for absolute)
           metrics: List of metrics to calculate for each variation
           
       Returns:
           Dictionary with sensitivity analysis results
       """
   ```
   This method analyzes how changes in a specific parameter affect multiple financial metrics. It generates data showing the impact of parameter variations on each metric, calculating both absolute and percentage changes from the baseline.

2. **`analyze_multiple_parameters`**
   ```python
   def analyze_multiple_parameters(self, 
                                 base_params, 
                                 parameters=None, 
                                 metrics=None):
       """Analyze sensitivity for multiple parameters to generate tornado chart data.
       
       Args:
           base_params: Dictionary of base parameters for the calculation
           parameters: List of parameters to analyze (default: all standard parameters)
           metrics: List of metrics to calculate for each parameter
           
       Returns:
           Dictionary with tornado chart data for each metric
       """
   ```
   This method analyzes the sensitivity of multiple parameters simultaneously, generating data for tornado charts that show the relative impact of each parameter on financial outcomes. It calculates the min and max impacts for each parameter and sorts them by magnitude.

3. **`compare_scenarios`**
   ```python
   def compare_scenarios(self, 
                       base_params, 
                       scenario_params, 
                       metrics=None):
       """Compare multiple scenarios with different parameter sets.
       
       Args:
           base_params: Dictionary of base parameters for the calculation
           scenario_params: Dictionary of scenario names and their parameter adjustments
           metrics: List of metrics to calculate for each scenario
           
       Returns:
           Dictionary with scenario comparison results
       """
   ```
   This method compares multiple predefined scenarios (such as optimistic, pessimistic, etc.) against a baseline scenario. It calculates financial metrics for each scenario and provides percentage changes relative to the baseline.

4. **`create_custom_scenario`**
   ```python
   def create_custom_scenario(self, 
                           base_params, 
                           custom_params, 
                           metrics=None):
       """Create and evaluate a custom scenario with user-defined parameters.
       
       Args:
           base_params: Dictionary of base parameters for the calculation
           custom_params: Dictionary of parameters to override in the base case
           metrics: List of metrics to calculate
           
       Returns:
           Dictionary with calculation results and comparison to base case
       """
   ```
   This method creates and evaluates a custom scenario with user-defined parameters. It calculates financial metrics for both the baseline and custom scenario, and provides percentage changes for each metric.

5. **`calculate_financial_metrics`**
   ```python
   def calculate_financial_metrics(self, params):
       """Calculate financial metrics based on parameters.
       
       Args:
           params: Dictionary of parameters for the calculation
           
       Returns:
           Dictionary with financial calculation results
       """
   ```
   This is a utility method that calculates financial metrics based on the provided parameters. It serves as a bridge to the calculation engine and financial model, handling parameter transformation and API interaction.

## Data Models

### Parameter Sensitivity Analysis Response

```json
{
  "parameter": "system_cost_per_watt",
  "base_value": 2.8,
  "variation_values": ["-20%", "-10%", "0%", "+10%", "+20%"],
  "metrics": {
    "payback_period_years": [8.0, 9.0, 10.0, 11.0, 12.0],
    "roi_percent": [12.5, 11.2, 10.0, 9.1, 8.3],
    "npv": [15000, 12500, 10000, 7500, 5000],
    "irr_percent": [9.5, 8.7, 8.0, 7.4, 6.9],
    "lcoe_per_kwh": [0.08, 0.09, 0.10, 0.11, 0.12],
    "lifetime_savings": [45000, 45000, 45000, 45000, 45000]
  },
  "percent_changes": {
    "payback_period_years": [-20.0, -10.0, 0.0, 10.0, 20.0],
    "roi_percent": [25.0, 12.0, 0.0, -9.0, -17.0],
    "npv": [50.0, 25.0, 0.0, -25.0, -50.0],
    "irr_percent": [18.8, 8.8, 0.0, -7.5, -13.8],
    "lcoe_per_kwh": [-20.0, -10.0, 0.0, 10.0, 20.0],
    "lifetime_savings": [0.0, 0.0, 0.0, 0.0, 0.0]
  }
}
```

### Tornado Chart Data Response

```json
{
  "base_case": {
    "payback_period_years": 10.0,
    "roi_percent": 10.0,
    "npv": 10000,
    "irr_percent": 8.0,
    "lcoe_per_kwh": 0.10,
    "lifetime_savings": 45000
  },
  "parameters": ["system_cost_per_watt", "electricity_rate", "annual_production", "electricity_inflation", "panel_degradation", "discount_rate", "loan_rate"],
  "tornado_data": {
    "npv": [
      {
        "parameter": "electricity_rate",
        "low": -25.0,
        "high": 25.0,
        "min_value": 7500,
        "max_value": 12500,
        "min_variation": "-20%",
        "max_variation": "+20%"
      },
      {
        "parameter": "system_cost_per_watt",
        "low": -20.0,
        "high": 20.0,
        "min_value": 8000,
        "max_value": 12000,
        "min_variation": "+20%",
        "max_variation": "-20%"
      },
      // ... other parameters
    ],
    // ... other metrics
  }
}
```

### Scenario Comparison Response

```json
{
  "scenarios": ["optimistic", "pessimistic", "base_case"],
  "metrics": {
    "payback_period_years": [8.5, 12.0, 10.0],
    "roi_percent": [12.0, 8.5, 10.0],
    "npv": [15000, 7000, 10000],
    "irr_percent": [9.5, 7.0, 8.0],
    "lcoe_per_kwh": [0.09, 0.12, 0.10],
    "lifetime_savings": [55000, 40000, 45000]
  },
  "percent_changes": {
    "payback_period_years": [-15.0, 20.0, 0.0],
    "roi_percent": [20.0, -15.0, 0.0],
    "npv": [50.0, -30.0, 0.0],
    "irr_percent": [18.8, -12.5, 0.0],
    "lcoe_per_kwh": [-10.0, 20.0, 0.0],
    "lifetime_savings": [22.2, -11.1, 0.0]
  },
  "parameters": {
    "system_cost_per_watt": [2.52, 3.08, 2.80],
    "electricity_rate": [0.132, 0.108, 0.120],
    "annual_production": [16500, 13500, 15000],
    // ... other parameters
  }
}
```

### Custom Scenario Response

```json
{
  "base_case": {
    "payback_period_years": 10.0,
    "roi_percent": 10.0,
    "npv": 10000,
    "irr_percent": 8.0,
    "lcoe_per_kwh": 0.10,
    "lifetime_savings": 45000
  },
  "custom_scenario": {
    "payback_period_years": 9.0,
    "roi_percent": 11.2,
    "npv": 12500,
    "irr_percent": 8.7,
    "lcoe_per_kwh": 0.09,
    "lifetime_savings": 48000
  },
  "parameters": {
    "base": {
      "system_cost_per_watt": 2.80,
      "electricity_rate": 0.12,
      // ... other parameters
    },
    "custom": {
      "system_cost_per_watt": 2.65,
      "electricity_rate": 0.13,
      // ... other parameters
    }
  },
  "percent_changes": {
    "payback_period_years": -10.0,
    "roi_percent": 12.0,
    "npv": 25.0,
    "irr_percent": 8.8,
    "lcoe_per_kwh": -10.0,
    "lifetime_savings": 6.7
  }
}
```

## Usage Examples

### Basic Parameter Sensitivity Analysis

```python
# Create the sensitivity analyzer
analyzer = SensitivityAnalyzer(calculation_engine, financial_model)

# Define base parameters
base_params = {
    "latitude": 39.7392,
    "longitude": -104.9903,
    "system_capacity": 10,
    "module_type": 1,
    "array_type": 2,
    "losses": 14,
    "tilt": 20,
    "azimuth": 180,
    "system_cost_per_watt": 2.80,
    "incentive_percent": 30,
    "loan_percent": 70,
    "loan_term": 20,
    "loan_rate": 5.5,
    "discount_rate": 4.0,
    "electricity_inflation": 2.5,
    "analysis_years": 25,
    "maintenance_cost": 20,
    "annual_production_kwh": 15000,
    "electricity_rate": 0.12
}

# Analyze sensitivity for system cost
cost_sensitivity = analyzer.analyze_parameter_sensitivity(
    base_params, "system_cost_per_watt"
)
print("System Cost Sensitivity:", cost_sensitivity)
```

### Generating Tornado Chart Data

```python
# Generate tornado chart data for multiple parameters
tornado_data = analyzer.analyze_multiple_parameters(base_params)
print("Tornado Chart Data:", tornado_data)
```

### Scenario Comparison

```python
# Define scenarios
scenarios = {
    "optimistic": {
        "system_cost_per_watt": 2.50,
        "electricity_rate": 0.13,
        "electricity_inflation": 3.0,
        "annual_production_kwh": 16500  # 10% higher
    },
    "pessimistic": {
        "system_cost_per_watt": 3.10,
        "electricity_rate": 0.11,
        "electricity_inflation": 2.0,
        "annual_production_kwh": 13500  # 10% lower
    }
}

# Compare scenarios
scenario_comparison = analyzer.compare_scenarios(base_params, scenarios)
print("Scenario Comparison:", scenario_comparison)
```

### Custom Scenario Analysis

```python
# Create custom scenario with user inputs
custom_scenario = analyzer.create_custom_scenario(
    base_params,
    {"system_cost_per_watt": 2.65, "loan_rate": 4.5, "analysis_years": 30}
)
print("Custom Scenario:", custom_scenario)
```

## API Integration

The sensitivity analyzer integrates with the backend API via the following endpoint:

```
POST /api/sensitivity-analysis
```

This endpoint accepts a JSON payload with the following structure:

```json
{
  "base_params": {
    // Base parameters for the calculation
  },
  "analysis_type": "tornado", // "tornado", "scenario", or "custom"
  "scenarios": {
    // For scenario analysis
  },
  "custom_params": {
    // For custom scenario analysis
  }
}
```

The response structure varies based on the analysis type, as described in the data models section.

## Frontend Integration

The sensitivity analyzer is integrated with the frontend via the `SensitivityAnalysisVisualization` component, which:

1. Displays tornado charts for parameter impact analysis
2. Shows scenario comparisons
3. Provides interactive sliders for custom scenario creation
4. Updates results in real-time as parameters change

## Performance Considerations

1. **Calculation intensity**: The analyzer performs multiple calculations for each parameter variation, which can be computationally intensive.
2. **Caching**: Consider caching results for common parameter sets to improve performance.
3. **Asynchronous processing**: For large parameter sets, consider implementing asynchronous processing.

## Best Practices

1. **Parameter selection**: Focus on parameters with the greatest impact on financial outcomes.
2. **Variation ranges**: Use appropriate ranges that reflect realistic parameter variations.
3. **Metric selection**: Choose metrics that align with the user's investment goals.
4. **Context for interpretation**: Provide clear explanations of how to interpret sensitivity results.

## Future Enhancements

1. **Monte Carlo simulation**: Implement probabilistic analysis using random parameter distributions.
2. **Correlation modeling**: Account for correlations between parameters (e.g., higher electricity rates may correlate with higher inflation).
3. **Optimization**: Add functionality to find optimal parameter combinations for specific goals.
4. **Additional metrics**: Expand the analysis to include environmental metrics (carbon reduction, etc.).
5. **Machine learning integration**: Use ML to predict parameter sensitivities based on historical data.