#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
STEP 02 — PREVIOUS CM + INDEX (FINAL STABLE VERSION)

✔ Loads BhavCopy
✔ Uses processed PD index file
✔ No MA dependency
✔ No zero PCT bug
✔ Pipeline-safe
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
# LOAD CM BHAVCOPY
# =========================================================
files = handle_missing_files(RAW_DIR, "BhavCopy_NSE_CM_*.csv")

if not files:
    raise FileNotFoundError("❌ No CM file found")

cm_file = files[0]
logger.info(f"📄 Loading CM file: {cm_file.name}")

df = pd.read_csv(cm_file)
df = df[(df["Sgmt"] == "CM") & (df["SctySrs"] == "EQ")].copy()

# detect close column
if "ClsPric" in df.columns:
    spot_col = "ClsPric"
elif "ClsPricRs" in df.columns:
    spot_col = "ClsPricRs"
else:
    raise ValueError("❌ Closing price column not found")

df = df[["TradDt", "TckrSymb", spot_col]]

df = df.rename(columns={
    "TckrSymb": "SYMBOL",
    spot_col: "PREV_SPOT_CLOSE"
})

df = normalize_symbols(df)
df = parse_edates(df, "TradDt")
df = convert_to_numeric(df, ["PREV_SPOT_CLOSE"])

# =========================================================
# LOAD INDEX FROM PD PIPELINE (FINAL FIX)
# =========================================================

index_file = Path(r"H:\Fo_Chart_Feb\data\processed\cm\previous_cm_index.csv")

if not index_file.exists():
    raise FileNotFoundError(f"❌ Processed index file not found: {index_file}")

logger.info(f"📊 Loading index file: {index_file.name}")

idx = pd.read_csv(index_file)
idx.columns = idx.columns.str.strip().str.upper()

# rename to match CM structure
idx = idx.rename(columns={
    "DATE": "TradDt",
    "CLOSE": "PREV_SPOT_CLOSE"
})

idx = idx[["TradDt", "SYMBOL", "PREV_SPOT_CLOSE"]]

idx = normalize_symbols(idx)
idx = parse_edates(idx, "TradDt")
idx = convert_to_numeric(idx, ["PREV_SPOT_CLOSE"])

df = pd.concat([df, idx], ignore_index=True)

logger.info("✅ INDEX MERGED (PD SYSTEM)")

# =========================================================
# SAVE FINAL
# =========================================================

df = df.dropna(subset=["SYMBOL", "PREV_SPOT_CLOSE"])
df = df.sort_values(["TradDt", "SYMBOL"]).reset_index(drop=True)

df.to_csv(OUT_FILE, index=False)

logger.info("🔥 STEP 02 COMPLETE")
logger.info(df.head())

# =========================================================
# DEBUG CHECK
# =========================================================
print("\n===== DEBUG NIFTY VALUE =====")
print(df[df["SYMBOL"] == "NIFTY"])
print("=============================\n")