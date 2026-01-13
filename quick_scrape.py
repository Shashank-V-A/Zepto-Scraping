"""
Quick scraper that runs immediately without waiting for user input.
Use this if you've already set location and navigated to the category page.
"""

from scraper import (
    setup_driver,
    scroll_and_load_products,
    extract_product_data,
    save_to_csv,
    save_to_json,
    human_like_delay,
    OUTPUT_CSV,
    OUTPUT_JSON,
    HEADLESS_MODE,
    FRUITS_VEGETABLES_URL
)

def main():
    """Quick scrape - assumes you're already on the category page."""
    driver = None
    
    try:
        print("=" * 60)
        print("QUICK SCRAPE - Fruits & Vegetables")
        print("=" * 60)
        print("\nThis script will:")
        print("1. Open browser (or use existing)")
        print("2. Navigate to Fruits & Vegetables")
        print("3. Scroll to load products")
        print("4. Extract all product data")
        print("5. Save to CSV/JSON")
        print("\n" + "=" * 60)
        
        # Setup driver
        print("\n[1/4] Setting up Chrome driver...")
        driver = setup_driver(headless=HEADLESS_MODE)
        print("[OK] Driver initialized")
        
        # Navigate to category
        print("\n[2/4] Navigating to Fruits & Vegetables category...")
        print(f"URL: {FRUITS_VEGETABLES_URL}")
        driver.get(FRUITS_VEGETABLES_URL)
        human_like_delay(5, 7)  # Wait longer for page to load
        print("[OK] Category page loaded")
        print(f"Current URL: {driver.current_url}")
        
        # Scroll to load products
        print("\n[3/4] Scrolling to load all products...")
        print("(This may take a minute...)")
        scroll_and_load_products(driver, max_scrolls=15)  # More scrolls
        print("[OK] Scrolling complete")
        
        # Extract products
        print("\n[4/4] Extracting product data...")
        products = extract_product_data(driver)
        
        if products:
            print("\n" + "=" * 60)
            print("SAVING DATA...")
            print("=" * 60)
            save_to_csv(products, OUTPUT_CSV)
            save_to_json(products, OUTPUT_JSON)
            print(f"\n[SUCCESS] Successfully scraped {len(products)} products!")
            print(f"\nOutput files:")
            print(f"  - {OUTPUT_CSV}")
            print(f"  - {OUTPUT_JSON}")
        else:
            print("\n" + "=" * 60)
            print("[WARNING] NO PRODUCTS FOUND!")
            print("=" * 60)
            print("\nPossible reasons:")
            print("1. Location not set correctly (should be Whitefield - 560067)")
            print("2. Products haven't loaded (try waiting longer)")
            print("3. Selectors need updating (Zepto may have changed HTML)")
            print("4. Page structure is different than expected")
            print("\nTroubleshooting:")
            print("- Check browser window - are products visible?")
            print("- Try scrolling manually in the browser")
            print("- Check if location is set correctly")
        
        print("\n" + "=" * 60)
        print("Scraping completed!")
        print("=" * 60)
        
        if not HEADLESS_MODE:
            print("\nBrowser will stay open for 30 seconds for you to verify...")
            import time
            time.sleep(30)
    
    except Exception as e:
        print(f"\n[ERROR] Error during scraping: {str(e)}")
        import traceback
        traceback.print_exc()
    
    finally:
        if driver:
            driver.quit()
            print("Browser closed.")

if __name__ == "__main__":
    main()
