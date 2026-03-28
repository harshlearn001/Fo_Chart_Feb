#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
from pathlib import Path

RAW_DIR = Path(r"H:\Fo_Chart_Feb\data\raw\cm_previous_month")
index_file = Path(r"H:\Fo_Chart_Feb\data\processed\cm\previous_cm_index.csv")
OUT_FILE = Path(r"H:\Fo_Chart_Feb\data\processed\cm\previous_cm_clean.csv")

OUT_FILE.parent.mkdir(parents=True, exist_ok=True)

cm_files = list(RAW_DIR.glob("BhavCopy_NSE_CM_*.csv"))

if not cm_files:
    raise FileNotFoundError("CM bhavcopy not found")

cm_file = cm_files[0]
print(f"Using CM file: {cm_file.name}")

df = pd.read_csv(cm_file)
df = df[(df["Sgmt"] == "CM") & (df["SctySrs"] == "EQ")].copy()

spot_col = "ClsPric" if "ClsPric" in df.columns else "ClsPricRs"

df = df[["TradDt", "TckrSymb", spot_col]]
df = df.rename(columns={
    "TckrSymb": "SYMBOL",
    spot_col: "PREV_SPOT_CLOSE"
})

# ✅ FIXED HERE
if not index_file.exists():
    raise FileNotFoundError("Run step_02a_extract_prev_cm_index.py first")

idx = pd.read_csv(index_file)

df = pd.concat([df, idx], ignore_index=True)
df.to_csv(OUT_FILE, index=False)

print("✅ CM + INDEX merged")
print(df[df["SYMBOL"] == "NIFTY"])