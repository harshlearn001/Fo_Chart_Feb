#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
STEP 07 | BUILD SECTOR MASTER EXCEL (FINAL)

✔ Single source of truth from config
✔ FULL_SECTORIAL_MAP with macro + sector mapping
✔ Duplicate-symbol guard
✔ Excel-ready output
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

import pandas as pd

from config import (
    OUTPUT_FILES, FULL_SECTORIAL_MAP, setup_logging
)
from utils import (
    ensure_paths
)

logger = setup_logging(__name__)

# =================================================
# FLATTEN SECTOR MAP WITH DUPLICATE GUARD
# =================================================
rows = []
seen = set()

for macro, sectors in FULL_SECTORIAL_MAP.items():
    for sector, symbols in sectors.items():
        for symbol in symbols:
            if symbol in seen:
                raise ValueError(f"Duplicate symbol detected: {symbol}")
            seen.add(symbol)
            rows.append({
                "SYMBOL": symbol,
                "MACRO_BUCKET": macro,
                "SECTOR": sector
            })

df = (
    pd.DataFrame(rows)
      .sort_values(["MACRO_BUCKET","SECTOR","SYMBOL"])
      .reset_index(drop=True)
)

# =================================================
# WRITE EXCEL
# =================================================
ensure_paths(OUTPUT_FILES["sector_master"].parent)

with pd.ExcelWriter(OUTPUT_FILES["sector_master"], engine="xlsxwriter") as writer:
    df.to_excel(writer, sheet_name="Sector_Master", index=False)
    writer.sheets["Sector_Master"].freeze_panes(1, 0)

logger.info("✅ SECTOR MASTER EXCEL GENERATED")
logger.info(f"📊 Symbols : {len(df)}")
logger.info(f"📁 File    : {OUTPUT_FILES['sector_master']}")
logger.info(df.head())
