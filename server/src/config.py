"""
Configuration settings for the Energy Investment Decision Support System.
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file if present
load_dotenv()

# API Keys
NREL_API_KEY = os.getenv("NREL_API_KEY", "Zr6gLeUtWfgvxP1cVBZJBTWczSwbdAFxKiyDMaUQ")
NASA_POWER_API_URL = "https://power.larc.nasa.gov/api/temporal/daily/point"

# Default parameters
DEFAULT_SYSTEM_CAPACITY = 4  # kW
DEFAULT_LOSSES = 14  # %
DEFAULT_TILT = 20  # degrees
DEFAULT_AZIMUTH = 180  # degrees (south-facing)
DEFAULT_MODULE_TYPE = 1  # Standard module type
DEFAULT_ARRAY_TYPE = 1  # Fixed open rack