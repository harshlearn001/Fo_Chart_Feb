#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
STEP 08 FINAL PRO
Place Stocks into Sectors + Final Excel Output

✔ Adds SPOT_CLOSE
✔ Adds PREV_SPOT_CLOSE
✔ Shows correct PCT change
✔ Final trading ready sheet
"""

import sys
from pathlib import Path
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent.parent))

from config import OUTPUT_FILES, setup_logging

logger = setup_logging(__name__)


def main():

    logger.info("📊 STEP 08 - FINAL SECTOR OUTPUT")

    # ======================================================
    # LOAD FILES
    # ======================================================
    fo = pd.read_csv(OUTPUT_FILES["merged_fo_cm"])
    sector = pd.read_excel(OUTPUT_FILES["sector_master"])

    logger.info(f"Loaded {len(fo)} rows from FO file")
    logger.info(f"Loaded {len(sector)} sector mappings")

    # ======================================================
    # MERGE SECTOR MAP
    # ======================================================
    final = fo.merge(sector, on="SYMBOL", how="left")

    # ======================================================
    # RANK INSIDE SECTOR
    # ======================================================
    final["RANK"] = (
        final.sort_values("DIFF", ascending=False)
        .groupby("SECTOR")
        .cumcount() + 1
    )

    # ======================================================
    # FINAL COLUMN ORDER (ULTRA FINAL)
    # ======================================================
    final = final[[
        "MACRO_BUCKET",
        "SECTOR",
        "SYMBOL",

        # NEW ADDED
        "SPOT_CLOSE",
        "PREV_SPOT_CLOSE",

        "PCT_CHANGE",
        "FUTURE_PRICE",
        "BASIS",

        "ROLLOVER_OI_LATEST",
        "ROLLOVER_OI_6M_AVG",
        "ROLLOVER_COST_LATEST",
        "ROLLOVER_COST_6M_AVG",

        "RANK",
        "DIFF"
    ]]

    final = final.sort_values(["MACRO_BUCKET", "SECTOR", "RANK"])

    # ======================================================
    # SAVE FINAL
    # ======================================================
    final.to_csv(OUTPUT_FILES["final_with_sector"], index=False)

    excel_path = OUTPUT_FILES["final_with_sector"].with_suffix(".xlsx")
    final.to_excel(excel_path, index=False)

    logger.info("🎉 FINAL SECTOR FILE GENERATED")
    logger.info(f"📁 CSV: {OUTPUT_FILES['final_with_sector']}")
    logger.info(f"📁 Excel: {excel_path}")
    logger.info(final.head())


if __name__ == "__main__":
    main()