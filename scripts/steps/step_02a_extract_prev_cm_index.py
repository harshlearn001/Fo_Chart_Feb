#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
from pathlib import Path
import re

# ============================================
# PATHS
# ============================================
RAW_DIR = Path(r"H:\Fo_Chart_Feb\data\raw\cm_previous_month_indices")
OUT_FILE = Path(r"H:\Fo_Chart_Feb\data\processed\cm\previous_cm_index.csv")

OUT_FILE.parent.mkdir(parents=True, exist_ok=True)

# ============================================
# AUTO FIND PD FILE
# ============================================
pd_files = list(RAW_DIR.glob("pd*.csv"))

if not pd_files:
    raise FileNotFoundError("❌ No pd file found in folder")

FILE = pd_files[0]
print(f"📄 Using PD file: {FILE.name}")

# ============================================
# READ FILE
# ============================================
df = pd.read_csv(FILE)
df.columns = df.columns.str.strip().str.upper()

# ============================================
# CLEAN SECURITY COLUMN
# ============================================
df["SECURITY"] = df["SECURITY"].astype(str).str.upper().str.strip()

# ============================================
# INDEX MAPPING (STRICT)
# ============================================
def map_index(name):
    if name == "NIFTY 50":
        return "NIFTY"
    elif name == "NIFTY BANK":
        return "BANKNIFTY"
    elif name == "NIFTY FIN SERVICE":
        return "FINNIFTY"
    elif name in ["NIFTY MIDCAP SELECT", "NIFTY MIDCAP 150"]:
        return "MIDCPNIFTY"
    elif name == "NIFTY NEXT 50":
        return "NIFTYNXT50"
    else:
        return None

df["SYMBOL"] = df["SECURITY"].apply(map_index)

# keep only valid indices
df = df.dropna(subset=["SYMBOL"])

# ============================================
# EXTRACT DATE FROM FILE NAME
# ============================================
match = re.search(r"pd(\d{2})(\d{2})(\d{4})", FILE.name.lower())

if not match:
    raise ValueError("❌ Date not found in filename")

day, month, year = match.groups()
trade_date = pd.to_datetime(f"{year}-{month}-{day}")

# ============================================
# BUILD FINAL DATA
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

# ============================================
# DATA TYPE FIX (IMPORTANT)
# ============================================

# numeric conversion
for col in ["OPEN", "HIGH", "LOW", "CLOSE"]:
    final[col] = pd.to_numeric(final[col], errors="coerce")

final["VOLUME"] = pd.to_numeric(final["VOLUME"], errors="coerce").fillna(0).astype("int64")

# date as datetime
final["DATE"] = pd.to_datetime(trade_date)

# reorder
final = final[["DATE", "SYMBOL", "OPEN", "HIGH", "LOW", "CLOSE", "VOLUME"]]

# ============================================
# SORT + CLEAN
# ============================================
final = final.sort_values("SYMBOL").reset_index(drop=True)

# ============================================
# SAVE
# ============================================
final.to_csv(OUT_FILE, index=False)

print("\n✅ FINAL CLEAN INDEX DATA READY")
print(final)
print("\n📁 Saved →", OUT_FILE)