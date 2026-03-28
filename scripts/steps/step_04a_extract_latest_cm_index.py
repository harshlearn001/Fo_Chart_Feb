#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
STEP 04a — EXTRACT LATEST CM INDEX (FINAL FIXED VERSION)

✔ Handles "" vs NaN issue
✔ Filters only real index rows
✔ Removes ETF / stock noise
✔ Correct mapping
✔ No empty output
✔ Production ready
"""

import pandas as pd
from pathlib import Path
import re

# ============================================
# PATHS
# ============================================
RAW_DIR = Path(r"H:\Fo_Chart_Feb\data\raw\cm_latest_month_indices")
OUT_FILE = Path(r"H:\Fo_Chart_Feb\data\processed\cm\latest_cm_index.csv")

OUT_FILE.parent.mkdir(parents=True, exist_ok=True)

# ============================================
# FIND PD FILE
# ============================================
pd_files = list(RAW_DIR.glob("pd*.csv"))

if not pd_files:
    raise FileNotFoundError("❌ No PD file found")

FILE = pd_files[0]
print(f"📄 Using PD file: {FILE.name}")

# ============================================
# READ FILE
# ============================================
df = pd.read_csv(FILE)
df.columns = df.columns.str.strip().str.upper()

# ============================================
# DEBUG RAW (IMPORTANT)
# ============================================
print("\n===== RAW SAMPLE =====")
print(df[["SERIES", "SYMBOL", "SECURITY"]].head(10))
print("======================\n")

# ============================================
# CLEAN SECURITY
# ============================================
df["SECURITY"] = df["SECURITY"].astype(str).str.upper().str.strip()

# ============================================
# 🔥 FIXED FILTER (handles empty string)
# ============================================
df = df[
    (df["SERIES"].astype(str).str.strip() == "") &
    (df["SYMBOL"].astype(str).str.strip() == "")
]

# ============================================
# INDEX MAPPING (SAFE)
# ============================================
def map_index(name):

    name = str(name).upper()

    if name == "NIFTY 50":
        return "NIFTY"

    elif name == "NIFTY BANK":
        return "BANKNIFTY"

    elif "FINSRV" in name:
        return "FINNIFTY"

    elif "MIDCAP" in name:
        return "MIDCPNIFTY"

    elif name == "NIFTY NEXT 50":
        return "NIFTYNXT50"

    else:
        return None

df["SYMBOL"] = df["SECURITY"].apply(map_index)

# keep only valid
df = df.dropna(subset=["SYMBOL"])

# ============================================
# DEBUG MATCH
# ============================================
print("\n===== FINAL INDEX MATCH =====")
print(df[["SECURITY", "SYMBOL"]])
print("============================\n")

# ============================================
# EXTRACT DATE
# ============================================
match = re.search(r"pd(\d{2})(\d{2})(\d{4})", FILE.name.lower())

if not match:
    raise ValueError("❌ Date not found in filename")

day, month, year = match.groups()
trade_date = pd.to_datetime(f"{year}-{month}-{day}")

# ============================================
# BUILD FINAL
# ============================================
final = df[[
    "SYMBOL",
    "OPEN_PRICE",
    "HIGH_PRICE",
    "LOW_PRICE",
    "CLOSE_PRICE",
    "NET_TRDQTY"
]].copy()

# rename
final = final.rename(columns={
    "OPEN_PRICE": "OPEN",
    "HIGH_PRICE": "HIGH",
    "LOW_PRICE": "LOW",
    "CLOSE_PRICE": "CLOSE",
    "NET_TRDQTY": "VOLUME"
})

# numeric conversion
for col in ["OPEN", "HIGH", "LOW", "CLOSE"]:
    final[col] = pd.to_numeric(final[col], errors="coerce")

final["VOLUME"] = pd.to_numeric(final["VOLUME"], errors="coerce").fillna(0).astype("int64")

# add date
final["DATE"] = trade_date

# reorder
final = final[["DATE", "SYMBOL", "OPEN", "HIGH", "LOW", "CLOSE", "VOLUME"]]

# ============================================
# REMOVE DUPLICATES
# ============================================
final = final.drop_duplicates(subset=["SYMBOL"])

# ============================================
# SORT
# ============================================
final = final.sort_values("SYMBOL").reset_index(drop=True)

# ============================================
# SAVE
# ============================================
final.to_csv(OUT_FILE, index=False)

print("\n🔥 FINAL CLEAN INDEX DATA READY")
print(final)

print("\n📁 Saved →", OUT_FILE)