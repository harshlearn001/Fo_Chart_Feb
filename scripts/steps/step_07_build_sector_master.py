#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
STEP 07 | BUILD SECTOR MASTER EXCEL (FINAL PRO VERSION)

✔ Clean symbol normalization
✔ Strong duplicate detection
✔ Empty sector validation
✔ Excel formatting (usable)
✔ Production safe
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import pandas as pd

from config import OUTPUT_FILES, FULL_SECTORIAL_MAP, setup_logging
from utils import ensure_paths

logger = setup_logging(__name__)

# =================================================
# FLATTEN SECTOR MAP (SAFE VERSION)
# =================================================
rows = []
seen = {}

for macro, sectors in FULL_SECTORIAL_MAP.items():

    if not sectors:
        raise ValueError(f"❌ Empty macro detected: {macro}")

    for sector, symbols in sectors.items():

        if not symbols:
            raise ValueError(f"❌ Empty sector: {macro} → {sector}")

        for symbol in symbols:

            symbol_clean = str(symbol).upper().strip()

            # duplicate detection (advanced)
            if symbol_clean in seen:
                raise ValueError(
                    f"❌ Duplicate symbol: {symbol_clean} | "
                    f"Existing: {seen[symbol_clean]} | "
                    f"New: {macro} → {sector}"
                )

            seen[symbol_clean] = f"{macro} → {sector}"

            rows.append({
                "SYMBOL": symbol_clean,
                "MACRO_BUCKET": macro,
                "SECTOR": sector
            })

df = (
    pd.DataFrame(rows)
      .sort_values(["MACRO_BUCKET", "SECTOR", "SYMBOL"])
      .reset_index(drop=True)
)

# =================================================
# SAVE EXCEL (FORMATTED)
# =================================================
ensure_paths(OUTPUT_FILES["sector_master"].parent)

excel_path = OUTPUT_FILES["sector_master"]

with pd.ExcelWriter(excel_path, engine="xlsxwriter") as writer:

    df.to_excel(writer, sheet_name="Sector_Master", index=False)

    ws = writer.sheets["Sector_Master"]

    # Freeze header
    ws.freeze_panes(1, 0)

    # Autofilter
    ws.autofilter(0, 0, len(df), len(df.columns) - 1)

    # Column widths
    ws.set_column("A:A", 15)
    ws.set_column("B:B", 20)
    ws.set_column("C:C", 25)

logger.info("✅ SECTOR MASTER EXCEL GENERATED")
logger.info(f"📊 Symbols : {len(df)}")
logger.info(f"📁 File    : {excel_path}")
logger.info(df.head())