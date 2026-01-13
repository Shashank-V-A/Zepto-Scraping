"""
Utility script to fix ChromeDriver issues.
Run this if you encounter WinError 193 or ChromeDriver compatibility errors.
"""

import os
import shutil
from pathlib import Path

def clear_webdriver_cache():
    """Clears webdriver-manager cache directory."""
    cache_paths = [
        os.path.join(os.path.expanduser("~"), ".wdm"),
        os.path.join(os.path.expanduser("~"), ".cache", "selenium"),
    ]
    
    cleared = False
    for cache_path in cache_paths:
        if os.path.exists(cache_path):
            try:
                print(f"Found cache at: {cache_path}")
                shutil.rmtree(cache_path)
                print(f"  [OK] Cleared successfully!")
                cleared = True
            except Exception as e:
                print(f"  [ERROR] Error clearing: {e}")
        else:
            print(f"Cache not found at: {cache_path}")
    
    return cleared

def main():
    print("="*60)
    print("ChromeDriver Cache Cleaner")
    print("="*60)
    print()
    
    if clear_webdriver_cache():
        print("\n" + "="*60)
        print("Cache cleared! Now try running scraper.py again.")
        print("="*60)
    else:
        print("\nNo cache found or already cleared.")
        print("If you still have issues, try:")
        print("1. Update Chrome: https://www.google.com/chrome/")
        print("2. Update webdriver-manager: pip install --upgrade webdriver-manager")
        print("3. Check Chrome version matches ChromeDriver")

if __name__ == "__main__":
    main()
