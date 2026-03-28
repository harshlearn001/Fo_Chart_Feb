#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
MAIN PIPELINE RUNNER
Orchestrates all steps: 01-08

Run with: python run_pipeline.py
"""

import sys
import subprocess
from pathlib import Path
import logging

from config import setup_logging

logger = setup_logging("PIPELINE")

SCRIPT_DIR = Path(__file__).resolve().parent
STEPS_DIR = SCRIPT_DIR / "steps"

STEPS = [
    ("step_01_sixmonth_rollover_analysis.py", "6-Month Rollover Analysis"),
    ("step_02_cleanup_previous_cm.py", "Clean Previous Month CM Data"),
    ("step_03_latest_rollover_analysis.py", "Latest Month Rollover Analysis"),
    ("step_04a_extract_latest_cm_index.py", "Extract Latest Month Index"),
    ("step_04_cleanup_latest_cm.py", "Clean Latest Month CM Data"),
    ("step_05_merge_all_data.py", "Merge All FO & CM Data"),
    ("step_06_build_sector_layout.py", "Build Sector Layout"),
    ("step_07_build_sector_master.py", "Build Sector Master Excel"),
    ("step_08_place_into_sectors.py", "Place Stocks into Sectors"),
]


def run_script(script_name: str, description: str) -> bool:
    """Run a single script.
    
    Args:
        script_name: Name of the script file
        description: Human-readable description
        
    Returns:
        True if successful, False otherwise
    """
    script_path = STEPS_DIR / script_name
    
    if not script_path.exists():
        logger.error(f"❌ Script not found: {script_path}")
        return False
    
    logger.info(f"\n{'='*60}")
    logger.info(f"▶ STEP: {description}")
    logger.info(f"📄 Running: {script_name}")
    logger.info(f"{'='*60}")
    
    try:
        result = subprocess.run(
            [sys.executable, str(script_path)],
            cwd=SCRIPT_DIR,
            check=True,
            capture_output=False
        )
        logger.info(f"✅ COMPLETED: {description}\n")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ FAILED: {description}")
        logger.error(f"Error code: {e.returncode}")
        return False
    except Exception as e:
        logger.error(f"❌ ERROR in {description}: {str(e)}")
        return False


def main():
    """Run the complete pipeline."""
    logger.info("\n" + "="*60)
    logger.info("🚀 STARTING FUTURES & OPTIONS ROLLOVER PIPELINE")
    logger.info("="*60)
    
    successful = 0
    failed = 0
    
    for script_name, description in STEPS:
        if run_script(script_name, description):
            successful += 1
        else:
            failed += 1
            logger.warning(f"⚠️  Stopping pipeline due to failure in: {description}")
            break
    
    # Final summary
    logger.info("\n" + "="*60)
    logger.info("📊 PIPELINE SUMMARY")
    logger.info("="*60)
    logger.info(f"✅ Successful: {successful}/{len(STEPS)}")
    if failed == 0:
        logger.info("🎯 No failures detected")
    else:
        logger.error(f"❌ Failed: {failed}/{len(STEPS)}")
    
    if failed == 0:
        logger.info("\n🎉 PIPELINE COMPLETED SUCCESSFULLY!")
        return 0
    else:
        logger.error(f"\n❌ PIPELINE FAILED at step {successful + 1}")
        return 1


if __name__ == "__main__":
    sys.exit(main())

