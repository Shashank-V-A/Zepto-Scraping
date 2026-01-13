"""
Quick script to scrape Fruits & Vegetables category from Zepto.
This is a simplified version that focuses on the Fruits & Vegetables category.
"""

from scraper import (
    setup_driver, 
    set_location_whitefield, 
    scroll_and_load_products, 
    extract_product_data,
    save_to_csv,
    save_to_json,
    human_like_delay,
    navigate_to_fruits_vegetables_category,
    check_for_404,
    FRUITS_VEGETABLES_URL,
    ZEPTO_URL,
    OUTPUT_CSV,
    OUTPUT_JSON,
    HEADLESS_MODE
)

def main():
    """Scrape Fruits & Vegetables category."""
    driver = None
    
    try:
        print("=" * 60)
        print("Zepto Scraper - Fruits & Vegetables (Whitefield, 560067)")
        print("=" * 60)
        
        # Setup driver
        print("\n[1/4] Setting up Chrome driver...")
        driver = setup_driver(headless=HEADLESS_MODE)
        print("[OK] Driver initialized")
        
        # Navigate to homepage first to set location
        print("\n[2/5] Opening Zepto homepage...")
        driver.get(ZEPTO_URL)
        human_like_delay(3, 5)
        print("[OK] Homepage loaded")
        
        # Set location first (before navigating to category)
        print("\n[3/5] Setting delivery location to Whitefield (560067)...")
        location_set = set_location_whitefield(driver)
        
        if not location_set:
            print("\n" + "=" * 60)
            print("[IMPORTANT] Location was not set automatically!")
            print("=" * 60)
            print("\nPlease set the location manually:")
            print("1. Look for location button/display in the header")
            print("2. Click on it to open location modal")
            print("3. Enter PIN code: 560067")
            print("4. Click Apply/Confirm")
            print("\nAfter setting location, press Enter here to continue...")
            input("Press Enter after location is set to Whitefield (560067)...")
            print("\n[OK] Continuing with scraping...")
        else:
            print("\n[OK] Location set successfully! Continuing...")
        
        # Wait for page to reload after location change
        human_like_delay(3, 5)
        
        # Navigate to Fruits & Vegetables category using direct URL
        print("\n[4/5] Navigating to Fruits & Vegetables category...")
        print(f"URL: {FRUITS_VEGETABLES_URL}")
        category_navigated = navigate_to_fruits_vegetables_category(driver, use_direct_url=True)
        
        if not category_navigated:
            print("\n[WARNING] Could not navigate automatically.")
            print("Please navigate to Fruits & Vegetables category manually in the browser.")
            input("Press Enter after you've navigated to the category page...")
        else:
            print("[OK] Navigated to Fruits & Vegetables category")
        
        # Double-check for 404 page
        if check_for_404(driver):
            print("\n[ERROR] Page is showing 404 error!")
            print("Trying to navigate using direct URL...")
            driver.get(FRUITS_VEGETABLES_URL)
            human_like_delay(3, 5)
            
            if check_for_404(driver):
                print("[ERROR] Direct URL also returned 404!")
                print("Please navigate to Fruits & Vegetables category manually.")
                input("Press Enter after you've navigated to the category page...")
            else:
                print("[OK] Successfully navigated using direct URL")
        
        # Scroll to load all products
        print("\n[5/5] Scrolling to load all products...")
        scroll_and_load_products(driver, max_scrolls=10)
        
        # Extract products
        print("\nExtracting product data...")
        products = extract_product_data(driver)
        
        if products:
            print("\nSaving data...")
            save_to_csv(products, OUTPUT_CSV)
            save_to_json(products, OUTPUT_JSON)
            print(f"\n[SUCCESS] Successfully scraped {len(products)} products!")
            print(f"\nOutput files:")
            print(f"  - {OUTPUT_CSV}")
            print(f"  - {OUTPUT_JSON}")
        else:
            print("\n[WARNING] No products found.")
            print("This could be because:")
            print("  - Location is not set correctly")
            print("  - No products available for this location")
            print("  - Selectors need to be updated")
        
        print("\n" + "=" * 60)
        print("Scraping completed!")
        print("=" * 60)
        
        if not HEADLESS_MODE:
            print("\nBrowser will close in 10 seconds...")
            import time
            time.sleep(10)
    
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
