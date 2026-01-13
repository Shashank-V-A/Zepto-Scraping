"""
Quick test script to verify all imports work correctly.
Run this before running the main scraper.
"""

try:
    import selenium
    print("[OK] Selenium imported successfully")
    
    from selenium import webdriver
    print("[OK] Selenium webdriver imported successfully")
    
    from webdriver_manager.chrome import ChromeDriverManager
    print("[OK] WebDriver Manager imported successfully")
    
    import csv
    import json
    import time
    from datetime import datetime
    print("[OK] Standard library modules imported successfully")
    
    print("\n" + "="*50)
    print("All imports successful! You're ready to run scraper.py")
    print("="*50)
    
except ImportError as e:
    print(f"[ERROR] Import error: {e}")
    print("Please run: pip install -r requirements.txt")
