#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
from pathlib import Path

RAW_DIR = Path(r"H:\Fo_Chart_Feb\data\raw\cm_previous_month")
OUT_FILE = Path(r"H:\Fo_Chart_Feb\data\processed\cm\previous_index_from_ma.csv")

OUT_FILE.parent.mkdir(parents=True, exist_ok=True)

# Find MA file
ma_files = list(RAW_DIR.glob("MA*.csv"))

if not ma_files:
    raise FileNotFoundError("MA file not found")

ma_file = ma_files[0]
print(f"Using MA file: {ma_file.name}")

# Read MA
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

date_part = ma_file.stem.replace("MA", "")
trade_date = pd.to_datetime(date_part, format="%d%m%y")

ma["TradDt"] = trade_date
ma = ma.rename(columns={"CLOSE": "PREV_SPOT_CLOSE"})

final = ma[["TradDt", "SYMBOL", "PREV_SPOT_CLOSE"]]
final.to_csv(OUT_FILE, index=False)

print("✅ MA index extracted & saved")
print(final)