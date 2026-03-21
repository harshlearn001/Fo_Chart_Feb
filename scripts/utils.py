#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
UTILITY FUNCTIONS
- Data normalization
- Column detection
- Path management
- Common operations
"""

from pathlib import Path
from typing import List, Dict, Set
import pandas as pd
import numpy as np


def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Normalize column names: strip, uppercase, remove asterisks.
    
    Args:
        df: DataFrame with raw column names
        
    Returns:
        DataFrame with normalized column names
    """
    df.columns = (
        df.columns
        .str.strip()
        .str.upper()
        .str.replace("*", "", regex=False)
    )
    return df


def normalize_symbols(df: pd.DataFrame, col: str = "SYMBOL") -> pd.DataFrame:
    """Normalize symbol column: uppercase, strip whitespace.
    
    Args:
        df: DataFrame containing symbol column
        col: Name of symbol column
        
    Returns:
        DataFrame with normalized symbols
    """
    df[col] = df[col].astype(str).str.strip().str.upper()
    return df


def detect_column(
    df: pd.DataFrame, 
    candidates: List[str], 
    label: str
) -> str:
    """Smart column detection from list of candidates.
    
    Args:
        df: DataFrame to search in
        candidates: List of possible column names
        label: Description for error messages
        
    Returns:
        The column name if found
        
    Raises:
        KeyError: If no candidate column found
    """
    for col in candidates:
        if col in df.columns:
            return col
    raise KeyError(
        f"{label} not found among {candidates}. "
        f"Available: {list(df.columns)}"
    )


def ensure_paths(*paths: Path) -> None:
    """Ensure all paths exist as directories.
    
    Args:
        *paths: Variable number of Path objects
    """
    for path in paths:
        path.mkdir(parents=True, exist_ok=True)


def validate_required_columns(
    df: pd.DataFrame,
    required: Set[str],
    file_path: str = ""
) -> None:
    """Validate that DataFrame has all required columns.
    
    Args:
        df: DataFrame to check
        required: Set of required column names
        file_path: Optional file path for error context
        
    Raises:
        ValueError: If required columns missing
    """
    missing = required - set(df.columns)
    if missing:
        raise ValueError(
            f"Missing columns in {file_path}: {missing}. "
            f"Available: {set(df.columns)}"
        )


def handle_missing_files(
    pattern_path: Path,
    glob_pattern: str = "*.csv"
) -> List[Path]:
    """Find files matching pattern, raise if none found.
    
    Args:
        pattern_path: Directory to search in
        glob_pattern: File pattern to match
        
    Returns:
        List of matching file paths
        
    Raises:
        FileNotFoundError: If no files found
    """
    files = list(pattern_path.glob(glob_pattern))
    if not files:
        raise FileNotFoundError(
            f"No files matching '{glob_pattern}' found in {pattern_path}"
        )
    return sorted(files)


def extract_trade_date(filename: str, date_format: str = "%d%m%Y") -> pd.Timestamp:
    """Extract trade date from filename.
    
    Args:
        filename: Filename with date (e.g., "fo27012026.csv")
        date_format: Expected date format
        
    Returns:
        Parsed date as pandas Timestamp
    """
    file_stem = Path(filename).stem
    # Remove prefix (fo/BhavCopy_NSE_CM_etc)
    date_str = file_stem.replace("fo", "").replace("BhavCopy_NSE_CM_0_0_0_", "").split("_")[0]
    return pd.to_datetime(date_str, format=date_format, errors="coerce")


def calculate_rollover_oi(oi_values: np.ndarray) -> float:
    """Calculate rollover OI percentage from 3 expiry OI values.
    
    Args:
        oi_values: Array of 3 OI values [OI1, OI2, OI3]
        
    Returns:
        Rollover OI percentage or NaN
    """
    if len(oi_values) < 3:
        return np.nan
    
    OI1, OI2, OI3 = oi_values[:3]
    
    if pd.isna(OI1) or pd.isna(OI2) or pd.isna(OI3):
        return np.nan
    
    total = OI1 + OI2 + OI3
    if total == 0:
        return np.nan
    
    return ((OI2 + OI3) / total) * 100


def calculate_rollover_cost(cp1: float, cp2: float) -> float:
    """Calculate rollover cost percentage from 2 prices.
    
    Args:
        cp1: Current month close price
        cp2: Next month close price
        
    Returns:
        Rollover cost percentage or NaN
    """
    if pd.isna(cp1) or pd.isna(cp2) or cp1 == 0:
        return np.nan
    
    return ((cp2 - cp1) / cp1) * 100


def rename_expiry_column(df: pd.DataFrame) -> pd.DataFrame:
    """Standardize expiry date column name.
    
    Args:
        df: DataFrame with expiry date column
        
    Returns:
        DataFrame with standardized 'EXP_DATE' column
    """
    df = df.rename(columns={
        "EXPIRY_DT": "EXP_DATE",
        "EXPIRY_DATE": "EXP_DATE"
    })
    return df


def convert_to_numeric(
    df: pd.DataFrame,
    columns: List[str],
    errors: str = "coerce"
) -> pd.DataFrame:
    """Convert multiple columns to numeric.
    
    Args:
        df: DataFrame to convert
        columns: List of column names to convert
        errors: How to handle errors {'coerce', 'raise', 'ignore'}
        
    Returns:
        DataFrame with converted columns
    """
    for col in columns:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors=errors)
    return df


def parse_edates(df: pd.DataFrame, col: str = "EXP_DATE") -> pd.DataFrame:
    """Parse expiry date column to datetime.
    
    Args:
        df: DataFrame with date column
        col: Column name to parse
        
    Returns:
        DataFrame with parsed dates
    """
    if col in df.columns:
        df[col] = pd.to_datetime(df[col], dayfirst=True, errors="coerce")
    return df
