#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
STEP 03 | LATEST MONTH FUTURES ROLLOVER ANALYSIS

✔ Processes latest month FO data
✔ Calculates monthly rollover metrics
✔ Aggregates across all dates in month
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

import pandas as pd
import numpy as np

from config import (
    RAW_PATHS, OUTPUT_FILES, setup_logging
)
from utils import (
    normalize_columns, normalize_symbols, extract_trade_date,
    calculate_rollover_oi, calculate_rollover_cost,
    rename_expiry_column, convert_to_numeric, parse_edates,
    handle_missing_files, ensure_paths
)

logger = setup_logging(__name__)

RAW_DIR = RAW_PATHS["fo_latest_month"]
OUT_DIR = OUTPUT_FILES["latest_month_avg"].parent
OUT_FILE = OUTPUT_FILES["latest_month_avg"]

ensure_paths(OUT_DIR)


# =================================================
# DISCOVER AND PROCESS FILES
# =================================================
files = handle_missing_files(RAW_DIR, "fo*.csv")
files = [f for f in files if f.stem[2:].isdigit()]
logger.info(f"Found {len(files)} FO files (latest month)")

rows = []

# =================================================
# PROCESS EACH FILE
# =================================================
for csv_file in files:
    logger.info(f"Processing {csv_file.name}")

    df = pd.read_csv(csv_file)
    df = normalize_columns(df)
    df = rename_expiry_column(df)

    required = {"SYMBOL", "EXP_DATE", "OPEN_INT", "CLOSE_PRICE"}
    if not required.issubset(df.columns):
        logger.warning(f"Skipping {csv_file.name}: missing required columns")
        continue

    df = normalize_symbols(df)
    df = parse_edates(df)
    df = convert_to_numeric(df, ["OPEN_INT", "CLOSE_PRICE"])

    # =================================================
    # PER SYMBOL → EXPIRY AGGREGATION
    # =================================================
    for sym, g in df.groupby("SYMBOL"):

        exp = (
            g.groupby("EXP_DATE", as_index=False)
             .agg(
                 OI=("OPEN_INT", "sum"),
                 PRICE=("CLOSE_PRICE", "mean")
             )
             .sort_values("EXP_DATE")
        )

        if len(exp) < 3:
            continue

        # Prices
        CP1 = exp["PRICE"].iloc[0]   # current / near
        CP2 = exp["PRICE"].iloc[1]   # next / mid

        # OI
        OI1, OI2, OI3 = exp["OI"].iloc[:3]

        roll_oi = calculate_rollover_oi(np.array([OI1, OI2, OI3]))
        roll_cost = calculate_rollover_cost(CP1, CP2)

        rows.append({
            "SYMBOL": sym,
            "FUT_NEXT_PRICE": CP2,
            "ROLL_COST_PCT_M": roll_cost,
            "ROLL_OI_PCT_M": roll_oi
        })


# =================================================
# CALCULATE MONTHLY AVERAGES
# =================================================
dfm = pd.DataFrame(rows)

monthly = (
    dfm
    .groupby("SYMBOL", as_index=False)
    .mean(numeric_only=True)
    .round(4)
)

monthly.to_csv(OUT_FILE, index=False)

logger.info("✅ MONTHLY FUTURES ROLLOVER GENERATED (FAR PRICE REMOVED)")
logger.info(f"📁 Output: {OUT_FILE}")
logger.info(monthly.head())
