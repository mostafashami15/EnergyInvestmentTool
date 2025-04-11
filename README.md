# Energy Investment Decision Support System

## Project Overview
An interactive web application that helps users make informed decisions about renewable energy investments based on location-specific data, financial parameters, and technological options.

## Features
- Solar energy production calculation using multiple data sources (NREL, NASA)
- Location-based solar resource assessment
- Utility rate information for financial analysis
- Interactive mapping interface (planned)
- Financial ROI and payback period calculations (planned)
- System optimization recommendations (planned)

## Technology Stack
- **Backend**: Python/Flask
- **APIs**: NREL, NASA POWER
- **Frontend**: React.js, Leaflet (planned)
- **Data Visualization**: D3.js, Chart.js (planned)
- **LLM Integration**: OpenAI/Anthropic (planned)

## Current Status
Initial research phase completed with successful API integrations:

- ✅ NREL APIs (PVWatts, Solar Resource, Utility Rates)
- ✅ NASA POWER APIs (Hourly, Daily, Monthly, Climatology)
- ✅ Comparative analysis of data sources
- ✅ Initial mapping prototypes

## Project Structure
```
EnergyInvestmentTool/
├── client/                # React frontend
│   ├── public/
│   └── src/
│       └── research/      # Frontend research (map tests)
├── server/                # Python/Flask backend
│   └── src/
│       ├── config.py      # Configuration settings
│       ├── data_sources/  # API interface modules
│       │   ├── __init__.py
│       │   ├── nasa.py    # NASA POWER API interface
│       │   └── nrel.py    # NREL API interface
│       └── research/      # Research and testing
│           ├── nasa_test.py
│           └── nrel_test.py
├── docs/                  # Documentation
│   ├── api_research/      # API findings
│   ├── system_design/     # Architecture docs
│   └── roadmap.md         # Project timeline
└── README.md              # Project overview
```

## Key Findings

### Solar Production Comparison
- NREL PVWatts (Denver, 10kW): 16,133 kWh/year
- NASA Calculation (Denver, 10kW): 10,917 kWh/year
- PVWatts estimates are ~48% higher than NASA calculations

### Regional Variations
- Phoenix has 67% more solar resource than Seattle
- Utility rates vary from 7.8¢-12.0¢/kWh depending on location
- Optimal tilt angle can increase production by 22%

## Installation and Setup
1. Clone the repository
2. Create Python environment: `python -m venv env`
3. Activate environment: `source env/bin/activate` (Unix) or `env\Scripts\activate` (Windows)
4. Install dependencies: `pip install -r requirements.txt`
5. Configure API keys in `.env` file (see `.env.example`)
6. Run tests: `python -m server.src.research.nrel_test`

## Getting Started
The project is currently in the research and development phase. See the documentation folder for implementation details and roadmap.

## Next Steps
1. Create unified calculation engine for solar energy production
2. Implement financial modeling with utility rate data
3. Develop initial mapping interface with solar potential visualization
4. Build backend API endpoints for frontend integration
5. Implement data caching for better performance

## Documentation
See the `docs/` directory for detailed documentation:
- `roadmap.md`: Project development timeline
- `api_research/`: API capabilities and integration notes
- `system_design/`: Architecture and data pipeline documentation

## License
MIT License