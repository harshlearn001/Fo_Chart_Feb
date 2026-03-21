"""
FO Chart Futures & Options Rollover Analysis Pipeline

A production-ready data pipeline for analyzing NSE Futures & Options rollover patterns
and cash market equity spot prices with sector classification.

Main Entry Points:
    - python run_pipeline.py : Run complete pipeline
    - python setup.py        : Create necessary directories
"""

__version__ = "2.0"
__author__ = "Data Analytics Team"

# Import core modules for easy access
from config import (
    BASE_DIR, RAW_PATHS, PROCESSED_PATHS, OUTPUT_FILES,
    FULL_SECTORIAL_MAP, SYMBOL_TO_SECTOR_MAP
)
from utils import (
    normalize_columns, normalize_symbols, detect_column,
    calculate_rollover_oi, calculate_rollover_cost
)

__all__ = [
    "BASE_DIR",
    "RAW_PATHS",
    "PROCESSED_PATHS",
    "OUTPUT_FILES",
    "FULL_SECTORIAL_MAP",
    "SYMBOL_TO_SECTOR_MAP",
    "normalize_columns",
    "normalize_symbols",
    "detect_column",
    "calculate_rollover_oi",
    "calculate_rollover_cost",
]
