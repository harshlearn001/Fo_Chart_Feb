#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
STEP 02 | PREVIOUS MONTH CM + INDEX (FINAL MASTER FIX)

✔ Loads previous CM
✔ Loads matching index file (same date)
✔ Fixes zero PCT problem
✔ Production safe
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import pandas as pd
from config import RAW_PATHS, OUTPUT_FILES, setup_logging
from utils import (
    normalize_symbols,
    parse_edates,
    convert_to_numeric,
    handle_missing_files,
    ensure_paths
)

logger = setup_logging(__name__)

RAW_DIR = RAW_PATHS["cm_previous_month"]
OUT_DIR = OUTPUT_FILES["previous_cm_clean"].parent
OUT_FILE = OUTPUT_FILES["previous_cm_clean"]

ensure_paths(OUT_DIR)

# =========================================================
# LOAD PREVIOUS CM
# =========================================================

files = handle_missing_files(RAW_DIR, "BhavCopy_NSE_CM_*.csv")

if not files:
    raise FileNotFoundError("No previous CM file found")

logger.info(f"Loading CM file: {files[0].name}")

df = pd.read_csv(files[0])
df = df[(df["Sgmt"] == "CM") & (df["SctySrs"] == "EQ")].copy()

# Detect close column
if "ClsPric" in df.columns:
    spot_col = "ClsPric"
elif "ClsPricRs" in df.columns:
    spot_col = "ClsPricRs"
else:
    raise ValueError("Closing price column not found")

df = df[["TradDt", "TckrSymb", spot_col]]
df = df.rename(columns={
    "TckrSymb": "SYMBOL",
    spot_col: "PREV_SPOT_CLOSE"
})

df = normalize_symbols(df)
df = parse_edates(df, "TradDt")
df = convert_to_numeric(df, ["PREV_SPOT_CLOSE"])

# =========================================================
# LOAD MATCHING INDEX FILE (STRICT DATE MATCH)
# =========================================================

cm_filename = files[0].name
parts = cm_filename.split("_")

# Example:
# BhavCopy_NSE_CM_0_0_0_20260127_F_0000.csv
cm_date = parts[6]

logger.info(f"Detected CM date: {cm_date}")

index_file = Path(RAW_DIR) / f"indices_ohlc_eod_{cm_date}.csv"

if index_file.exists():

    logger.info(f"Loading index file: {index_file.name}")
    idx = pd.read_csv(index_file)

    INDEX_MAP = {
        "NIFTY 50": "NIFTY",
        "NIFTY BANK": "BANKNIFTY",
        "NIFTY NEXT 50": "NIFTYNXT50",
        "NIFTY FINANCIAL SERVICES": "FINNIFTY",
        "NIFTY MIDCAP SELECT": "MIDCPNIFTY",
        "INDIA VIX": "INDIAVIX"
    }

    idx["SYMBOL"] = idx["INDEX_NAME"].map(INDEX_MAP)
    idx = idx.dropna(subset=["SYMBOL"])

    idx = idx.rename(columns={
        "CLOSE": "PREV_SPOT_CLOSE",
        "TRADE_DATE": "TradDt"
    })

    idx = idx[["TradDt", "SYMBOL", "PREV_SPOT_CLOSE"]]
    idx = normalize_symbols(idx)
    idx = parse_edates(idx, "TradDt")
    idx = convert_to_numeric(idx, ["PREV_SPOT_CLOSE"])

    df = pd.concat([df, idx], ignore_index=True)
    logger.info("📊 Index merged SUCCESS")

else:
    logger.error(f"❌ INDEX FILE NOT FOUND: {index_file}")

# =========================================================
# SAVE FINAL
# =========================================================

df = df.dropna(subset=["SYMBOL", "PREV_SPOT_CLOSE"])
df.to_csv(OUT_FILE, index=False)

logger.info("✅ PREVIOUS CM READY")
logger.info(df.head())