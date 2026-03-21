#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
STEP 01 | 6-MONTH FUTURES ROLLOVER ANALYSIS

✔ Aggregates 6 months of FO data
✔ Calculates rollover OI and rollover cost percentages
✔ Outputs monthly averages for 6-month period
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

RAW_DIR = RAW_PATHS["fo_last_sixmonth"]
OUT_DIR = OUTPUT_FILES["six_month_avg"].parent
OUT_FILE = OUTPUT_FILES["six_month_avg"]

ensure_paths(OUT_DIR)


# =================================================
# DISCOVER AND PROCESS FILES
# =================================================
files = handle_missing_files(RAW_DIR, "fo*.csv")
files = [f for f in files if f.stem[2:].isdigit()]
logger.info(f"Found {len(files)} FO files (6M)")

rows = []

for f in files:
    trade_dt = extract_trade_date(f.name)
    ym = trade_dt.to_period("M").to_timestamp()

    df = pd.read_csv(f)
    df = normalize_columns(df)
    df = rename_expiry_column(df)

    req = {"SYMBOL", "EXP_DATE", "OPEN_INT", "CLOSE_PRICE"}
    if not req.issubset(df.columns):
        logger.warning(f"Skipping {f.name}: missing required columns")
        continue

    df = normalize_symbols(df)
    df = parse_edates(df)
    df = convert_to_numeric(df, ["OPEN_INT", "CLOSE_PRICE"])

    for sym, g in df.groupby("SYMBOL"):
        exp = (
            g.groupby("EXP_DATE", as_index=False)
             .agg(OI=("OPEN_INT", "sum"), PRICE=("CLOSE_PRICE", "mean"))
             .sort_values("EXP_DATE")
        )

        if len(exp) < 3:
            continue

        OI1, OI2, OI3 = exp["OI"].iloc[:3]
        CP1, CP2 = exp["PRICE"].iloc[:2]

        roll_oi = calculate_rollover_oi(np.array([OI1, OI2, OI3]))
        roll_cost = calculate_rollover_cost(CP1, CP2)

        rows.append({
            "YEAR_MONTH": ym,
            "SYMBOL": sym,
            "ROLL_OI": roll_oi,
            "ROLL_COST": roll_cost
        })


# =================================================
# CALCULATE 6-MONTH AVERAGES
# =================================================
dfd = pd.DataFrame(rows)
latest = dfd["YEAR_MONTH"].max()
cutoff = latest - pd.DateOffset(months=6)

sixm = dfd[dfd["YEAR_MONTH"] >= cutoff]

six_avg = (
    sixm.groupby("SYMBOL", as_index=False)
        .agg(
            ROLL_OI_PCT_6M=("ROLL_OI", "mean"),
            ROLL_COST_PCT_6M=("ROLL_COST", "mean")
        )
        .round(4)
)

six_avg.to_csv(OUT_FILE, index=False)

logger.info("✅ 6-MONTH FUTURES ROLLOVER GENERATED")
logger.info(f"📁 Output: {OUT_FILE}")
logger.info(six_avg.head())
