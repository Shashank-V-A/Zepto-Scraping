"""
Quick test to verify ChromeDriver setup works correctly.
This tests only the driver initialization without running the full scraper.
"""

import sys
from scraper import setup_driver

def test_driver_setup():
    """Test if ChromeDriver can be initialized."""
    print("="*60)
    print("Testing ChromeDriver Setup")
    print("="*60)
    print()
    
    driver = None
    try:
        print("Attempting to initialize Chrome driver...")
        print("(This may take a moment on first run as ChromeDriver downloads)")
        print()
        
        driver = setup_driver(headless=False)
        
        print()
        print("="*60)
        print("[SUCCESS] ChromeDriver initialized successfully!")
        print("="*60)
        print()
        print("The driver is ready. You can now run the full scraper:")
        print("  python scraper.py")
        print()
        print("Closing test browser in 3 seconds...")
        
        import time
        time.sleep(3)
        
        return True
        
    except Exception as e:
        print()
        print("="*60)
        print("[ERROR] ChromeDriver initialization failed!")
        print("="*60)
        print()
        print(f"Error: {str(e)}")
        print()
        print("Troubleshooting steps:")
        print("1. Run: python fix_chromedriver.py")
        print("2. Update Chrome browser to latest version")
        print("3. Check if Chrome is installed correctly")
        print("4. Try: pip install --upgrade webdriver-manager selenium")
        return False
        
    finally:
        if driver:
            try:
                driver.quit()
                print("Browser closed.")
            except:
                pass

if __name__ == "__main__":
    success = test_driver_setup()
    sys.exit(0 if success else 1)
