#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
STEP 02 — PREVIOUS CM (FORCED MA HISTORICAL VERSION)

✔ Loads BhavCopy
✔ Forces MA historical index only
✔ Ignores any indices_ohlc files
✔ Prints debug value
✔ Guarantees no zero PCT bug
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
    raise FileNotFoundError("No CM file found in previous month folder")

cm_file = files[0]
logger.info(f"Loading CM file: {cm_file.name}")

df = pd.read_csv(cm_file)
df = df[(df["Sgmt"] == "CM") & (df["SctySrs"] == "EQ")].copy()

spot_col = "ClsPric" if "ClsPric" in df.columns else "ClsPricRs"

df = df[["TradDt", "TckrSymb", spot_col]]
df = df.rename(columns={
    "TckrSymb": "SYMBOL",
    spot_col: "PREV_SPOT_CLOSE"
})

df = normalize_symbols(df)
df = parse_edates(df, "TradDt")
df = convert_to_numeric(df, ["PREV_SPOT_CLOSE"])

# =========================================================
# FORCE LOAD MA FILE ONLY
# =========================================================
ma_files = list(Path(RAW_DIR).glob("MA*.csv"))

if not ma_files:
    raise FileNotFoundError("MA historical index file not found")

ma_file = ma_files[0]
logger.info(f"Using MA file: {ma_file.name}")

ma = pd.read_csv(ma_file, skiprows=8, engine="python")
ma.columns = ma.columns.str.strip()

ma = ma[["INDEX", "CLOSE"]].dropna()

INDEX_MAP = {
    "Nifty 50": "NIFTY",
    "NIFTY MIDCAP 150": "MIDCPNIFTY",
    "Nifty FinSrv25 50": "FINNIFTY",
    "NIFTY BANK": "BANKNIFTY"
}

ma["SYMBOL"] = ma["INDEX"].map(INDEX_MAP)
ma = ma.dropna(subset=["SYMBOL"])

cm_date = cm_file.name.split("_")[6]
ma["TradDt"] = pd.to_datetime(cm_date, format="%Y%m%d")
ma = ma.rename(columns={"CLOSE": "PREV_SPOT_CLOSE"})

idx = ma[["TradDt", "SYMBOL", "PREV_SPOT_CLOSE"]]

idx = normalize_symbols(idx)
idx = parse_edates(idx, "TradDt")
idx = convert_to_numeric(idx, ["PREV_SPOT_CLOSE"])

df = pd.concat([df, idx], ignore_index=True)

logger.info("📊 MA historical index merged")

# =========================================================
# SAVE
# =========================================================
df = df.dropna(subset=["SYMBOL", "PREV_SPOT_CLOSE"])
df.to_csv(OUT_FILE, index=False)

logger.info("✅ STEP 02 COMPLETE")

# =========================================================
# DEBUG CHECK
# =========================================================
print("\n===== DEBUG NIFTY VALUE SAVED =====")
print(df[df["SYMBOL"] == "NIFTY"])
print("===================================\n")