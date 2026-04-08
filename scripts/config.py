#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
CENTRAL CONFIGURATION
- Sector mapping (single source of truth)
- Data paths
- Logging setup
- Constants
"""

from pathlib import Path
import logging

# =================================================
# BASE PATH
# =================================================
BASE_DIR = Path(__file__).resolve().parents[1]

# =================================================
# DATA PATHS
# =================================================
RAW_PATHS = {
    "fo_latest_month": BASE_DIR / "data/raw/fo_latest_month",
    "fo_last_sixmonth": BASE_DIR / "data/raw/fo_last_sixmonth",
    "cm_latest_month": BASE_DIR / "data/raw/cm_latest_month",
    "cm_previous_month": BASE_DIR / "data/raw/cm_previous_month",
    # Raw indices files (market watch / indices CSVs)
    "indices": BASE_DIR / "data/raw/indices",
}

PROCESSED_PATHS = {
    "latest_month_avg": BASE_DIR / "data/processed/latest_month_avg",
    "last_sixmonth_avg": BASE_DIR / "data/processed/last_sixmonth_avg",
    "latest_month_cm": BASE_DIR / "data/processed/latest_month_cm",
    "previous_month_cm": BASE_DIR / "data/processed/previous_month_cm",
    "merged": BASE_DIR / "data/processed/merged",
    "sector": BASE_DIR / "data/Sector",
}

OUTPUT_FILES = {
    "six_month_avg": PROCESSED_PATHS["last_sixmonth_avg"] / "six_month_Avg_rollover_and_rollovercost.csv",
    "latest_month_avg": PROCESSED_PATHS["latest_month_avg"] / "monthly_rollover_and_rollcost.csv",
    "latest_cm_clean": PROCESSED_PATHS["latest_month_cm"] / "eq_spot_standard.csv",
    "previous_cm_clean": PROCESSED_PATHS["previous_month_cm"] / "eq_spot_previous_standard.csv",
    "merged_fo_cm": PROCESSED_PATHS["merged"] / "final_fo_oi_rollover_standard.csv",
    "sector_layout": PROCESSED_PATHS["merged"] / "final_fo_sector_excel_layout.csv",
    "sector_master": PROCESSED_PATHS["sector"] / "Sector_Master.xlsx",
    "final_with_sector": PROCESSED_PATHS["merged"] / "final_fo_with_sector_placed.csv",
}

# =================================================
# LOGGING SETUP
# =================================================
def setup_logging(name: str) -> logging.Logger:
    """Setup logging for a script."""
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger

# =================================================
# FULL SECTORIAL MAP (AUTHORITATIVE - SINGLE SOURCE OF TRUTH)
# =================================================
FULL_SECTORIAL_MAP = {

    # ================= CORE =================
    "CORE": {

        "PRIVATE_BANK": {
            "HDFCBANK","ICICIBANK","AXISBANK","KOTAKBANK","INDUSINDBK",
            "IDFCFIRSTB","FEDERALBNK","RBLBANK","YESBANK","BANDHANBNK","AUBANK"
        },

        "PSU_BANK": {
            "SBIN","BANKBARODA","PNB","CANBK","UNIONBANK","BANKINDIA",
            "INDIANB","IOB","UCOBANK","CENTRALBK","MAHABANK"
        },

        "FIN_SERV_INSURANCE": {
            "SBILIFE","HDFCLIFE","ICICIPRULI","ICICIGI","LICI"
        },

        "FIN_SERV_AMC_WEALTH": {
            "HDFCAMC","360ONE","KFINTECH","CAMS","ANGELONE","MFSL","NUVAMA"
        },

        "FIN_SERV_HOLDING": {
            "BAJAJHLDNG"
        },

        "TELECOM": {
            "BHARTIARTL","INDUSTOWER"
        },

        "CONSUMER_JEWELLERY": {
            "TITAN"
        },

        "IT": {
            "TCS","INFY","HCLTECH","WIPRO","TECHM","LTIM","MPHASIS","COFORGE",
            "PERSISTENT","OFSS","KPITTECH","CYIENT","ZENSARTECH",
            "TATAELXSI","TATATECH","SONATSOFTW","BSOFT","LTTS","INTELLECT",
            "NAUKRI"
        },

        "FMCG": {
            "ITC","HINDUNILVR","NESTLEIND","BRITANNIA","TATACONSUM",
            "DABUR","GODREJCP","MARICO","VBL","EMAMILTD",
            "RADICO","UBL","UNITDSPR","COLPAL",
            "PAGEIND","JUBLFOOD"
        },

        "PHARMA": {
            "SUNPHARMA","DRREDDY","CIPLA","DIVISLAB","ZYDUSLIFE",
            "TORNTPHARM","ALKEM","LUPIN","AUROPHARMA","BIOCON",
            "GLENMARK","IPCALAB","MANKIND","LAURUSLABS","PPLPHARMA",
            "ABBOTINDIA","SYNGENE","PFIZER","GLAXO",
            "AJANTPHARM","JBCHEPHARM","NEULANDLAB","NATCOPHARM",
            "GRANULES","WOCKPHARMA","ERIS","CAPLIPOINT","EMCURE",
            "CONCORDBIO","ASTRAZEN"
        },
    },

    # ================= CYCLICAL =================
    "CYCLICAL": {

        "FIN_SERV_NBFC": {
            "BAJFINANCE","BAJAJFINSV","SHRIRAMFIN","CHOLAFIN","LICHSGFIN",
            "MUTHOOTFIN","MANAPPURAM","PNBHOUSING","ABCAPITAL","LTF",
            "IIFL","SAMMAANCAP"
        },

        "FIN_SERV_PSU_FIN": {
            "PFC","RECLTD","IRFC","IREDA","HUDCO"
        },

        "METALS": {
            "TATASTEEL","JSWSTEEL","JINDALSTEL","SAIL","NMDC",
            "HINDALCO","NATIONALUM","APLAPOLLO","HINDZINC",
            "VEDL","WELCORP",
            "AMBUJACEM","DALBHARAT","GRASIM","SHREECEM","ULTRACEMCO",
            "COALINDIA"
        },

        "ENERGY": {
            "RELIANCE","ONGC","BPCL","IOC","HINDPETRO","OIL",
            "GAIL","PETRONET","IGL","MGL","GUJGASLTD","GSPL",
            "NTPC","POWERGRID","NHPC","TATAPOWER","ADANIPOWER",
            "ADANIGREEN","JSWENERGY","SJVN","NLCINDIA","IEX",
            "ADANIENSOL","INOXWIND","SUZLON","TORNTPOWER"
        },

        "CHEMICALS": {
            "PIDILITIND","SRF","SOLARINDS","UPL","PIIND","AARTIIND",
            "FLUOROCHEM","NAVINFLUOR","TATACHEM","COROMANDEL",
            "DEEPAKNTR","DEEPAKFERT","CHAMBLFERT","BAYERCROP",
            "PCBL","LINDEINDIA","SUMICHEM","SWANENERGY","ASIANPAINT"
        },

        "AUTO": {
            "MARUTI","TATAMOTORS","M&M","BAJAJ-AUTO","HEROMOTOCO","EICHERMOT",
            "TVSMOTOR","ASHOKLEY","SONACOMS","MOTHERSON","UNOMINDA",
            "ENDURANCE","BOSCHLTD","EXIDEIND","BALKRISIND",
            "MRF","CEAT","JKTYRE","BHARATFORG","TIINDIA"
        },

        "INDUSTRIALS": {
            "ABB","CGPOWER","CUMMINSIND","KAYNES","KEI",
            "SIEMENS","SUPREMEIND"
        },

        "ELECTRICAL": {
            "CROMPTON","HAVELLS","POLYCAB"
        },

        "ELECTRICAL_INFRA": {
            "PGEL"
        },

        "CAPITAL_GOODS": {
            "POWERINDIA"
        },

        "EMS_MANUFACTURING": {
            "DIXON"
        },

        "AUTO_EV": {
            "PREMIERENE","TMPV"
        },

        "INFRA_PIPES": {
            "ASTRAL"
        },

        "RENEWABLE_ENERGY": {
            "WAAREEENER"
        },

        "TELECOM": {
            "IDEA"
        },

        "INFRA": {
            "LT","ADANIPORTS","BHEL","KEC","KNRCON","IRCON",
            "RVNL","NBCC","RITES","ENGINERSIN","PNCINFRA",
            "ASHOKA","GMRINFRA","HGINFRA","CONCOR","ADANIENT","GMRAIRPORT"
        },
    },

    # ================= HIGH BETA =================
    "HIGH_BETA": {

        "FIN_SERV_PLATFORM": {
            "PAYTM","POLICYBZR","JIOFIN"
        },

        "FIN_SERV_CONSUMER_CREDIT": {
            "SBICARD"
        },

        "REALTY": {
            "DLF","LODHA","GODREJPROP","OBEROIRLTY","PRESTIGE",
            "PHOENIXLTD","SOBHA","BRIGADE","ANANTRAJ","SIGNATURE"
        },

        "DEFENCE": {
            "HAL","BEL","BDL","MAZDOCK"
        },

        "MEDIA": {
            "ZEEL","SUNTV","PVRINOX","SAREGAMA","TIPSMUSIC",
            "NETWORK18","HATHWAY","DBCORP","NAZARA","PFOCUS"
        },

        "RETAIL": {
            "DMART","TRENT","KALYANKJIL","NYKAA","ETERNAL",
            "INDHOTEL","INDIGO"
        },

        "LOGISTICS": {
            "IRCTC","DELHIVERY","ALLCARGO","GATI","TCIEXP","VRLLOG"
        },
    },

    # ================= DEFENSIVE =================
    "DEFENSIVE": {
        
        "HEALTHCARE": {
            "APOLLOHOSP","FORTIS","MAXHEALTH"
        },
        
        "FMCG": {
            "PATANJALI"
        },
    },

    # ================= NEWAGE =================
    "NEWAGE": {
        
        "CONSUMER_TECH": {
            "SWIGGY"
        },
    },

    # ================= CONSUMER =================
    "CONSUMER": {
        
        "CONSUMER_DURABLES": {
            "AMBER","BLUESTARCO","VOLTAS"
        },
    },

    # ================= REFERENCE =================
    "REFERENCE": {
        "MARKET_INFRA": {
            "BSE","MCX","CDSL"
        },
        "INDEX": {
            "NIFTY","BANKNIFTY","FINNIFTY","MIDCPNIFTY","NIFTYNXT50"
        }
    }
}

# Build flat symbol-to-sector mapping for quick lookups
SYMBOL_TO_SECTOR_MAP = {}
for macro, sectors in FULL_SECTORIAL_MAP.items():
    for sector, symbols in sectors.items():
        for symbol in symbols:
            if symbol in SYMBOL_TO_SECTOR_MAP:
                raise ValueError(f"Duplicate symbol detected: {symbol}")
            SYMBOL_TO_SECTOR_MAP[symbol] = (macro, sector)

# =================================================
# SYMBOL RENAME MAP (NSEMAPPING CORRECTIONS)
# =================================================
SYMBOL_RENAME_MAP = {
    "PHOENIXL": "PHOENIXLTD",
    "UNO MINDA": "UNOMINDA",
    "LTI": "LTIM",
    "LTM": "LTIM",   # ✅ FINAL FIX
    "MCDOWELL": "MCDOWELL-N",
}
# =================================================
# COLUMN DETECTION CANDIDATES
# =================================================
SPOT_CLOSE_CANDIDATES = [
    "SPOT_CLOSE", "CLOSE", "CLOSE_PRICE", "LAST", "ClsPric", "LastPric"
]

PREV_SPOT_CLOSE_CANDIDATES = [
    "PREV_SPOT_CLOSE", "PRE_SPOT_CLOSE", "SPOT_CLOSE", "CLOSE", "PrvsClsgPric", "ClsPric"
]
