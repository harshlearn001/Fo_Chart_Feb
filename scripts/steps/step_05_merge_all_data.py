#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
STEP 05 — MERGE ALL DATA (FINAL)

✔ Merge:
    - Previous CM
    - Latest CM
    - 6M rollover
    - Latest rollover
✔ Create final dataset
✔ Save final_fo_oi_rollover_standard.csv
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pandas as pd
from config import OUTPUT_FILES, setup_logging

logger = setup_logging(__name__)

def main():

    logger.info("📊 STEP 05 - MERGING ALL DATA")

    # ============================================
    # LOAD FILES
    # ============================================

    prev_cm = pd.read_csv(OUTPUT_FILES["previous_cm_clean"])
    latest_cm = pd.read_csv(OUTPUT_FILES["latest_cm_clean"])

    sixm = pd.read_csv(OUTPUT_FILES["six_month_avg"])
    latest = pd.read_csv(OUTPUT_FILES["latest_month_avg"])

    # ============================================
    # RENAME COLUMNS
    # ============================================

    latest = latest.rename(columns={
        "FUT_NEXT_PRICE": "FUTURE_PRICE",
        "ROLL_COST_PCT_M": "ROLLOVER_COST_LATEST",
        "ROLL_OI_PCT_M": "ROLLOVER_OI_LATEST"
    })

    sixm = sixm.rename(columns={
        "ROLL_COST_PCT_6M": "ROLLOVER_COST_6M_AVG",
        "ROLL_OI_PCT_6M": "ROLLOVER_OI_6M_AVG"
    })

    # ============================================
    # MERGE DATA
    # ============================================

    df = latest.merge(prev_cm, on="SYMBOL", how="left")
    df = df.merge(latest_cm, on="SYMBOL", how="left")
    df = df.merge(sixm, on="SYMBOL", how="left")

    # ============================================
    # CALCULATIONS
    # ============================================

    df["SPOT_CLOSE"] = df["SPOT_CLOSE"]
    df["PCT_CHANGE"] = ((df["SPOT_CLOSE"] - df["PREV_SPOT_CLOSE"]) / df["PREV_SPOT_CLOSE"]) * 100

    df["BASIS"] = df["FUTURE_PRICE"] - df["SPOT_CLOSE"]

    df["DIFF"] = df["ROLLOVER_OI_LATEST"] - df["ROLLOVER_OI_6M_AVG"]

    # ============================================
    # CLEAN
    # ============================================

    df = df.fillna(0)

    # ============================================
    # SAVE FINAL
    # ============================================

    out_file = OUTPUT_FILES["merged_fo_cm"]

    df.to_csv(out_file, index=False)

    logger.info("🔥 FINAL MERGED FILE READY")
    logger.info(f"📁 Saved → {out_file}")
    logger.info(df.head())


if __name__ == "__main__":
    main()