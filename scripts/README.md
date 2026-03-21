# FO & Chart Futures Rollover Pipeline - Refactored & Reorganized

## 📂 Project Structure

```
Fo_Chart_Dece/
├── .gitignore                  # Git ignore patterns
├── requirements.txt            # Python dependencies
├── README.md                   # Project documentation (this file)
│
└── scripts/
    ├── __init__.py            # Package initialization
    ├── config.py              # Central configuration
    ├── utils.py               # Reusable utility functions
    ├── run_pipeline.py        # Main pipeline orchestrator
    ├── setup.py               # Directory setup utility
    ├── README.md              # Pipeline documentation
    │
    └── steps/                 # Individual pipeline steps
        ├── __init__.py
        ├── step_01_sixmonth_rollover_analysis.py
        ├── step_02_cleanup_previous_cm.py
        ├── step_03_latest_rollover_analysis.py
        ├── step_04_cleanup_latest_cm.py
        ├── step_05_merge_all_data.py
        ├── step_06_build_sector_layout.py
        ├── step_07_build_sector_master.py
        └── step_08_place_into_sectors.py

data/
├── raw/                       # Raw input data (CSV files)
│   ├── fo_latest_month/
│   ├── fo_last_sixmonth/
│   ├── cm_latest_month/
│   └── cm_previous_month/
│
└── processed/                 # Processed output data
    ├── latest_month_avg/
    ├── last_sixmonth_avg/
    ├── latest_month_cm/
    ├── previous_month_cm/
    ├── merged/
    └── Sector/
```

## 🎯 Overview

This pipeline analyzes NSE Futures & Options (FO) rollover patterns and cash market (CM) equity spot prices. It processes raw data through 8 organized steps to produce analysis-ready datasets with sector classification.

## 🔄 Improvements Made (Version 2.0)

### ✨ Better Organization
- **Separated Concerns**: Core modules (config.py, utils.py) at root level
- **Pipeline Steps**: All 8 processing steps organized in `steps/` subdirectory
- **Clear Naming**: Descriptive names for each step (`step_01_sixmonth_rollover_analysis.py`, etc.)
- **Package Structure**: Added `__init__.py` files for proper Python package management

### 📦 New Files Added
- `requirements.txt` - Python dependencies
- `.gitignore` - Git ignore patterns
- `scripts/__init__.py` - Package initialization with exposed APIs
- `scripts/steps/__init__.py` - Pipeline steps module

### 🏗️ Smart Import Handling
Each step script automatically adds parent directory to Python path:
```python
sys.path.insert(0, str(Path(__file__).parent.parent))
```
This allows seamless imports from config/utils regardless of execution location.

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Setup Directories
```bash
cd scripts
python setup.py
```

### 3. Run Pipeline
```bash
python run_pipeline.py
```

## 📊 Pipeline Steps

| Step | Name | Input | Output |
|------|------|-------|--------|
| 01 | 6-Month Rollover Analysis | FO (6M) | 6M rollover metrics |
| 02 | Cleanup Previous CM | CM (prev) | Previous spot prices |
| 03 | Latest Rollover Analysis | FO (latest) | Monthly rollover metrics |
| 04 | Cleanup Latest CM | CM (latest) | Latest spot prices |
| 05 | Merge All Data | All outputs | Combined FO+CM dataset |
| 06 | Build Sector Layout | Merged data | Sector layout CSV |
| 07 | Build Sector Master | Config | Sector master Excel |
| 08 | Place into Sectors | Merged + Sectors | Final analysis dataset |

## 📋 Core Components

### `config.py` - Centralized Configuration
```python
# Data paths
RAW_PATHS = {...}
PROCESSED_PATHS = {...}
OUTPUT_FILES = {...}

# Sector mapping (single source of truth)
FULL_SECTORIAL_MAP = {
    "CORE": {"PRIVATE_BANK": {...}, ...},
    "CYCLICAL": {...},
    "HIGH_BETA": {...},
    "REFERENCE": {...}
}

# Symbol mappings
SYMBOL_RENAME_MAP = {...}
SYMBOL_TO_SECTOR_MAP = {...}
```

### `utils.py` - Shared Utilities
```
normalize_columns()        # Standardize column names
normalize_symbols()        # Uppercase & strip symbols
detect_column()           # Smart column detection
calculate_rollover_oi()   # OI percentage calculation
calculate_rollover_cost() # Cost percentage calculation
ensure_paths()            # Directory creation
parse_edates()            # Date parsing
convert_to_numeric()      # Type conversion
+ 11 more functions
```

### `run_pipeline.py` - Orchestrator
- Runs all 8 steps sequentially
- Comprehensive error handling
- Progress tracking & summary statistics
- Stops on first failure with diagnostics

## 🔧 Configuration

All settings are in `scripts/config.py`:

### Output File Paths
```python
OUTPUT_FILES = {
    "six_month_avg": ".../six_month_Avg_rollover_and_rollovercost.csv",
    "latest_month_avg": ".../monthly_rollover_and_rollcost.csv",
    "latest_cm_clean": ".../eq_spot_standard.csv",
    "previous_cm_clean": ".../eq_spot_previous_standard.csv",
    "merged_fo_cm": ".../final_fo_oi_rollover_standard.csv",
    "sector_layout": ".../final_fo_sector_excel_layout.csv",
    "sector_master": ".../Sector_Master.xlsx",
    "final_with_sector": ".../final_fo_with_sector_placed.csv",
}
```

### Sector Master Mapping
Edit `FULL_SECTORIAL_MAP` in `config.py` to manage:
- 4 Macro buckets: CORE, CYCLICAL, HIGH_BETA, REFERENCE
- 30+ Sectors per macro bucket
- 271+ Stocks mapping

### Column Detection
```python
SPOT_CLOSE_CANDIDATES = ["SPOT_CLOSE", "CLOSE", "ClsPric", ...]
PREV_SPOT_CLOSE_CANDIDATES = ["PREV_SPOT_CLOSE", "PrvsClsgPric", ...]
```

## 🧪 Running Individual Steps

```bash
cd scripts

# Run a specific step
python steps/step_01_sixmonth_rollover_analysis.py
python steps/step_02_cleanup_previous_cm.py
# ... etc

# Or run all at once
python run_pipeline.py
```

## 📈 Output Files

| File | Rows | Columns | Purpose |
|------|------|---------|---------|
| `six_month_Avg_rollover_and_rollovercost.csv` | 211 | 3 | 6-month average OI & cost |
| `monthly_rollover_and_rollcost.csv` | 211 | 4 | Latest month metrics |
| `eq_spot_standard.csv` | 4000+ | 3 | Latest spot prices |
| `eq_spot_previous_standard.csv` | 4000+ | 3 | Previous spot prices |
| `final_fo_oi_rollover_standard.csv` | 211 | 8 | Merged FO + CM |
| `final_fo_sector_excel_layout.csv` | 235+ | 9 | Sector layout (with blanks) |
| `Sector_Master.xlsx` | 271 | 3 | Sector master mapping |
| `final_fo_with_sector_placed.csv` | 211 | 10 | **Final output** |

## 🔍 Logging Output

```
2026-02-23 13:55:51 - PIPELINE - INFO - 🚀 STARTING FUTURES & OPTIONS ROLLOVER PIPELINE
2026-02-23 13:55:51 - __main__ - INFO - Found 6 FO files (6M)
2026-02-23 13:55:55 - __main__ - INFO - ✅ 6-MONTH FUTURES ROLLOVER GENERATED
...
2026-02-23 13:56:00 - PIPELINE - INFO - 🎉 PIPELINE COMPLETED SUCCESSFULLY!
✅ Successful: 8/8
❌ Failed: 0/8
```

## 📝 Key Features

✅ **Centralized Configuration** - Single source of truth  
✅ **Reusable Utilities** - DRY principle throughout  
✅ **Smart Column Detection** - Handles different CSV formats  
✅ **Type Hints & Docstrings** - IDE support & documentation  
✅ **Comprehensive Logging** - Timestamps & module names  
✅ **Error Handling** - Stops on failure with diagnostics  
✅ **No Hardcoded Paths** - Fully relative path structure  
✅ **Production Ready** - Tested & validated  

## 🚀 Advanced Usage

### Custom Configuration
```python
from config import OUTPUT_FILES, FULL_SECTORIAL_MAP
from utils import normalize_symbols

# Access configuration
print(OUTPUT_FILES["merged_fo_cm"])
print(FULL_SECTORIAL_MAP["CORE"])
```

### Importing in Other Scripts
```python
# In your own script
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "scripts"))

from config import OUTPUT_FILES, FULL_SECTORIAL_MAP
from utils import normalize_columns, detect_column
```

## 🐛 Troubleshooting

**ModuleNotFoundError: No module named 'pandas'**
```bash
pip install -r requirements.txt
```

**FileNotFoundError: No CM bhavcopy found**
- Ensure raw CM CSV files are in correct directories
- Run `python setup.py` to create directory structure

**Column not found error**
- Check column naming in source CSV files
- Update `SPOT_CLOSE_CANDIDATES` in config.py

## 📞 Support

For issues or questions:
1. Check the logs generated during pipeline run
2. Verify source data files exist and are properly formatted
3. Ensure Python dependencies are installed: `pip install -r requirements.txt`
4. Review config.py for path and mapping configurations

## 📄 License

Internal use only - Data Analytics Team

---

**Pipeline Version**: 2.0  
**Last Updated**: February 23, 2026  
**Status**: Production Ready ✅

