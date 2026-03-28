#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
STEP 08 FINAL PRO (UPGRADED)

✔ Sector validation
✔ Safe ranking
✔ Numeric cleanup
✔ Excel formatted
✔ Trading-ready output
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
    # CLEAN SYMBOL
    # ======================================================
    fo["SYMBOL"] = fo["SYMBOL"].astype(str).str.upper().str.strip()
    sector["SYMBOL"] = sector["SYMBOL"].astype(str).str.upper().str.strip()

    # ======================================================
    # MERGE SECTOR MAP
    # ======================================================
    final = fo.merge(sector, on="SYMBOL", how="left")

    # ======================================================
    # CHECK MISSING SECTORS (CRITICAL)
    # ======================================================
    missing = final[final["SECTOR"].isna()]

    if not missing.empty:
        logger.warning(f"⚠ Missing sector for {len(missing)} symbols")
        logger.warning(missing["SYMBOL"].unique()[:10])

        # Optional: mark instead of leaving NaN
        final["SECTOR"] = final["SECTOR"].fillna("UNKNOWN")
        final["MACRO_BUCKET"] = final["MACRO_BUCKET"].fillna("UNKNOWN")

    # ======================================================
    # NUMERIC CLEANUP
    # ======================================================
    num_cols = [
        "SPOT_CLOSE",
        "PREV_SPOT_CLOSE",
        "PCT_CHANGE",
        "FUTURE_PRICE",
        "BASIS",
        "ROLLOVER_OI_LATEST",
        "ROLLOVER_OI_6M_AVG",
        "ROLLOVER_COST_LATEST",
        "ROLLOVER_COST_6M_AVG",
        "DIFF"
    ]

    for col in num_cols:
        if col in final.columns:
            final[col] = pd.to_numeric(final[col], errors="coerce").fillna(0)

    # ======================================================
    # RANK INSIDE SECTOR (SAFE)
    # ======================================================
    final = final.sort_values(["SECTOR", "DIFF"], ascending=[True, False])
    final["RANK"] = final.groupby("SECTOR").cumcount() + 1

    # ======================================================
    # FINAL COLUMN ORDER
    # ======================================================
    final = final[[
        "MACRO_BUCKET",
        "SECTOR",
        "SYMBOL",
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

    final = final.sort_values(["MACRO_BUCKET", "SECTOR", "RANK"]).reset_index(drop=True)

    # ======================================================
    # SAVE CSV
    # ======================================================
    final.to_csv(OUTPUT_FILES["final_with_sector"], index=False)

    # ======================================================
    # SAVE EXCEL (FORMATTED)
    # ======================================================
    excel_path = OUTPUT_FILES["final_with_sector"].with_suffix(".xlsx")

    with pd.ExcelWriter(excel_path, engine="xlsxwriter") as writer:
        final.to_excel(writer, sheet_name="Final", index=False)

        ws = writer.sheets["Final"]

        # Freeze header
        ws.freeze_panes(1, 0)

        # Autofilter
        ws.autofilter(0, 0, len(final), len(final.columns) - 1)

        # Column width
        ws.set_column("A:B", 20)
        ws.set_column("C:C", 15)
        ws.set_column("D:N", 14)

    logger.info("🎉 FINAL SECTOR FILE GENERATED")
    logger.info(f"📁 CSV: {OUTPUT_FILES['final_with_sector']}")
    logger.info(f"📁 Excel: {excel_path}")
    logger.info(final.head())


if __name__ == "__main__":
    main()