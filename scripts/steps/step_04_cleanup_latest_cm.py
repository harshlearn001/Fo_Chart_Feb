#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
STEP 04 | CLEANUP LATEST MONTH CM DATA + INDEX (FINAL VERSION)

✔ Loads latest CM BhavCopy
✔ Loads processed index (from Step 04a)
✔ Merges both
✔ Ensures SPOT_CLOSE is correct
✔ Production-ready
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

if not files:
    raise FileNotFoundError("❌ No CM file found")

cm_file = files[0]
logger.info(f"📄 Loading CM file: {cm_file.name}")

df = pd.read_csv(cm_file)

# filter only EQ
df = df[(df["Sgmt"] == "CM") & (df["SctySrs"] == "EQ")].copy()

# detect close column
if "ClsPric" in df.columns:
    spot_col = "ClsPric"
elif "ClsPricRs" in df.columns:
    spot_col = "ClsPricRs"
else:
    raise ValueError("❌ Closing price column not found")

# select columns
df = df[["TradDt", "TckrSymb", spot_col]]

# rename
df = df.rename(columns={
    "TckrSymb": "SYMBOL",
    spot_col: "SPOT_CLOSE"
})

# clean
df = normalize_symbols(df)
df = parse_edates(df, "TradDt")
df = convert_to_numeric(df, ["SPOT_CLOSE"])

# =================================================
# LOAD INDEX FROM STEP 04a (FINAL FIX)
# =================================================
index_file = Path(r"H:\Fo_Chart_Feb\data\processed\cm\latest_cm_index.csv")

if not index_file.exists():
    raise FileNotFoundError(f"❌ Latest index file not found: {index_file}")

logger.info(f"📊 Loading processed index: {index_file.name}")

idx = pd.read_csv(index_file)

# clean column names
idx.columns = idx.columns.str.strip().str.upper()

# rename to match CM structure
idx = idx.rename(columns={
    "DATE": "TradDt",
    "CLOSE": "SPOT_CLOSE"
})

# select needed columns
idx = idx[["TradDt", "SYMBOL", "SPOT_CLOSE"]]

# clean index data
idx = normalize_symbols(idx)
idx = parse_edates(idx, "TradDt")
idx = convert_to_numeric(idx, ["SPOT_CLOSE"])

# merge CM + INDEX
df = pd.concat([df, idx], ignore_index=True)

logger.info("📊 Index data merged (latest month)")

# =================================================
# FINAL CLEAN
# =================================================
df = df.dropna(subset=["SYMBOL", "SPOT_CLOSE"])
df = df.sort_values(["TradDt", "SYMBOL"]).reset_index(drop=True)

# =================================================
# SAVE
# =================================================
df.to_csv(OUT_FILE, index=False)

logger.info("🔥 STEP 04 COMPLETE — LATEST CM + INDEX READY")
logger.info(df.head())

# =================================================
# DEBUG CHECK
# =================================================
print("\n===== DEBUG INDEX CHECK =====")
print(df[df["SYMBOL"].isin(["NIFTY", "BANKNIFTY", "FINNIFTY"])])
print("============================\n")