#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
STEP 04 | CLEANUP LATEST MONTH CM DATA + INDEX SUPPORT (STRICT DATE FIXED)
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

RAW_DIR = RAW_PATHS["cm_latest_month"]
OUT_DIR = OUTPUT_FILES["latest_cm_clean"].parent
OUT_FILE = OUTPUT_FILES["latest_cm_clean"]

ensure_paths(OUT_DIR)

# =================================================
# LOAD EQUITY CM
# =================================================
files = handle_missing_files(RAW_DIR, "BhavCopy_NSE_CM_*.csv")
logger.info(f"Loading CM file: {files[0].name}")

df = pd.read_csv(files[0])
df = df[(df["Sgmt"] == "CM") & (df["SctySrs"] == "EQ")].copy()

if "ClsPric" in df.columns:
    spot_col = "ClsPric"
elif "ClsPricRs" in df.columns:
    spot_col = "ClsPricRs"
else:
    raise ValueError("Closing price not found")

df = df[["TradDt", "TckrSymb", spot_col]]
df = df.rename(columns={
    "TckrSymb": "SYMBOL",
    spot_col: "SPOT_CLOSE"
})

df = normalize_symbols(df)
df = parse_edates(df, "TradDt")
df = convert_to_numeric(df, ["SPOT_CLOSE"])

# =================================================
# STRICT DATE MATCH INDEX FILE
# =================================================

cm_filename = files[0].name
parts = cm_filename.split("_")
cm_date = parts[6]   # FIXED INDEX

expected_index_file = Path(RAW_DIR) / f"indices_ohlc_eod_{cm_date}.csv"

if expected_index_file.exists():

    logger.info(f"Loading index file: {expected_index_file.name}")
    idx = pd.read_csv(expected_index_file)

    INDEX_NAME_MAP = {
        "NIFTY 50": "NIFTY",
        "NIFTY BANK": "BANKNIFTY",
        "NIFTY NEXT 50": "NIFTYNXT50",
        "NIFTY FINANCIAL SERVICES": "FINNIFTY",
        "NIFTY MIDCAP SELECT": "MIDCPNIFTY",
        "INDIA VIX": "INDIAVIX"
    }

    idx["SYMBOL"] = idx["INDEX_NAME"].map(INDEX_NAME_MAP)
    idx = idx.dropna(subset=["SYMBOL"])

    idx = idx.rename(columns={
        "CLOSE": "SPOT_CLOSE",
        "TRADE_DATE": "TradDt"
    })

    idx = idx[["TradDt", "SYMBOL", "SPOT_CLOSE"]]
    idx = normalize_symbols(idx)
    idx = parse_edates(idx, "TradDt")
    idx = convert_to_numeric(idx, ["SPOT_CLOSE"])

    df = pd.concat([df, idx], ignore_index=True)
    logger.info("📊 Index data merged (latest month)")

else:
    logger.warning(f"⚠ Matching index file NOT FOUND for date {cm_date}")

# =================================================
# SAVE
# =================================================
df = df.dropna(subset=["SYMBOL", "SPOT_CLOSE"])
df.to_csv(OUT_FILE, index=False)

logger.info("✅ LATEST CM + INDEX READY")
logger.info(df.head())