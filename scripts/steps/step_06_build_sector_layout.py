#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
STEP 06
Build Final Excel Layout Like Screenshot
"""

import sys
from pathlib import Path
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent.parent))

from config import OUTPUT_FILES, SYMBOL_TO_SECTOR_MAP, setup_logging

logger = setup_logging(__name__)


def main():

    logger.info("📊 STEP 06 - BUILDING SECTOR LAYOUT")

    df = pd.read_csv(OUTPUT_FILES["merged_fo_cm"])

    # ======================================================
    # ADD SECTOR + MACRO
    # ======================================================

    def map_sector(symbol):
        return SYMBOL_TO_SECTOR_MAP.get(symbol, ("UNKNOWN", "UNKNOWN"))

    df[["MACRO", "SECTOR"]] = df["SYMBOL"].apply(
        lambda x: pd.Series(map_sector(x))
    )

    # ======================================================
    # RANK WITHIN SECTOR
    # ======================================================

    df["RANK"] = (
        df.sort_values("DIFF", ascending=False)
        .groupby("SECTOR")
        .cumcount() + 1
    )

    # ======================================================
    # SELECT COLUMNS (LIKE IMAGE)
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
    )

    # ======================================================
    # SAVE CSV
    # ======================================================

    df_final.to_csv(OUTPUT_FILES["sector_layout"], index=False)

    # ======================================================
    # ALSO SAVE EXCEL VERSION
    # ======================================================

    excel_path = OUTPUT_FILES["sector_layout"].with_suffix(".xlsx")
    df_final.to_excel(excel_path, index=False)

    logger.info("✅ STEP 06 COMPLETED")


if __name__ == "__main__":
    main()