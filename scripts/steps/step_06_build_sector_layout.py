#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
STEP 06
Build Final Excel Layout (Production Safe)
"""

import sys
from pathlib import Path
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent.parent))

from config import OUTPUT_FILES, SYMBOL_TO_SECTOR_MAP, setup_logging

logger = setup_logging(__name__)


def main():

    logger.info("📊 STEP 06 - BUILDING SECTOR LAYOUT")

    input_file = OUTPUT_FILES["merged_fo_cm"]

    # ======================================================
    # CHECK INPUT FILE
    # ======================================================

    if not Path(input_file).exists():
        raise FileNotFoundError(f"❌ Missing merged file: {input_file}")

    df = pd.read_csv(input_file)

    if df.empty:
        raise ValueError("❌ Input dataframe is empty")

    # ======================================================
    # CLEAN SYMBOL
    # ======================================================

    df["SYMBOL"] = df["SYMBOL"].astype(str).str.upper().str.strip()

    # ======================================================
    # ADD SECTOR + MACRO
    # ======================================================

    def map_sector(symbol):
        return SYMBOL_TO_SECTOR_MAP.get(symbol, ("UNKNOWN", "UNKNOWN"))

    df[["MACRO", "SECTOR"]] = df["SYMBOL"].apply(
        lambda x: pd.Series(map_sector(x))
    )

    # ======================================================
    # ENSURE REQUIRED COLUMNS
    # ======================================================

    required_cols = [
        "SPOT_CLOSE",
        "PCT_CHANGE",
        "FUTURE_PRICE",
        "BASIS",
        "ROLLOVER_OI_LATEST",
        "ROLLOVER_OI_6M_AVG",
        "ROLLOVER_COST_LATEST",
        "ROLLOVER_COST_6M_AVG",
        "DIFF",
    ]

    for col in required_cols:
        if col not in df.columns:
            logger.warning(f"⚠ Missing column: {col}")
            df[col] = 0

    # ======================================================
    # TYPE FIX (IMPORTANT)
    # ======================================================

    for col in required_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    # ======================================================
    # RANK WITHIN SECTOR
    # ======================================================

    df = df.sort_values("DIFF", ascending=False)

    df["RANK"] = df.groupby("SECTOR").cumcount() + 1

    # ======================================================
    # SELECT COLUMNS
    # ======================================================

    final_cols = [
        "MACRO",
        "SECTOR",
        "SYMBOL",
        "SPOT_CLOSE",
        "PCT_CHANGE",
        "FUTURE_PRICE",
        "BASIS",
        "ROLLOVER_OI_LATEST",
        "ROLLOVER_OI_6M_AVG",
        "ROLLOVER_COST_LATEST",
        "ROLLOVER_COST_6M_AVG",
        "RANK",
        "DIFF",
    ]

    df_final = df[final_cols].sort_values(
        ["MACRO", "SECTOR", "RANK"]
    ).reset_index(drop=True)

    # ======================================================
    # SAVE CSV
    # ======================================================

    df_final.to_csv(OUTPUT_FILES["sector_layout"], index=False)

    # ======================================================
    # SAVE EXCEL
    # ======================================================

    excel_path = OUTPUT_FILES["sector_layout"].with_suffix(".xlsx")
    df_final.to_excel(excel_path, index=False)

    logger.info("✅ STEP 06 COMPLETED")
    logger.info(f"📁 Saved CSV → {OUTPUT_FILES['sector_layout']}")
    logger.info(f"📁 Saved Excel → {excel_path}")


if __name__ == "__main__":
    main()