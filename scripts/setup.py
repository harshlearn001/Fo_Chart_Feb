#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
PIPELINE INITIALIZATION HELPER
Sets up all necessary directories for the pipeline.

Run with: python setup.py
"""

from pathlib import Path
from config import RAW_PATHS, PROCESSED_PATHS

def setup_directories():
    """Create all required directories."""
    all_paths = {**RAW_PATHS, **PROCESSED_PATHS}
    
    print("🔧 Setting up directories...")
    
    created = 0
    for name, path in all_paths.items():
        path.mkdir(parents=True, exist_ok=True)
        print(f"   ✓ {name}: {path}")
        created += 1
    
    print(f"\n✅ Created {created} directories")

if __name__ == "__main__":
    setup_directories()
