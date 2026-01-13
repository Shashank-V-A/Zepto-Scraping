"""
Zepto Web Scraper - Whitefield, Bangalore (PIN: 560067)
========================================================

This scraper extracts product data from Zepto for Whitefield, Bangalore location.
It handles JavaScript rendering, lazy loading, and location selection.

Author: Educational/MVP Purpose
"""

import time
import csv
import json
import os
import shutil
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager


# Configuration
ZEPTO_URL = "https://www.zepto.com"
WHITEFIELD_PIN = "560067"
OUTPUT_CSV = "output/zepto_whitefield_products.csv"
OUTPUT_JSON = "output/zepto_whitefield_products.json"
HEADLESS_MODE = False  # Set to True to run in background

# Category URLs (updated with working URLs)
FRUITS_VEGETABLES_URL = "https://www.zepto.com/cn/fruits-vegetables/fruits-vegetables/cid/64374cfe-d06f-4a01-898e-c07c46462c36/scid/e78a8422-5f20-4e4b-9a9f-22a0e53962e3"


def clear_webdriver_cache():
    """
    Clears the webdriver-manager cache to force re-download of ChromeDriver.
    This helps fix corrupted or incompatible ChromeDriver issues.
    """
    try:
        # Get the cache directory for webdriver-manager
        cache_path = os.path.join(os.path.expanduser("~"), ".wdm")
        if os.path.exists(cache_path):
            print("Clearing webdriver-manager cache...")
            shutil.rmtree(cache_path)
            print("Cache cleared successfully!")
            return True
    except Exception as e:
        print(f"Warning: Could not clear cache: {e}")
    return False


def setup_driver(headless=False, retry_count=2):
    """
    Sets up and returns a Chrome WebDriver instance with optimized settings.
    Includes error handling for ChromeDriver compatibility issues.
    
    Args:
        headless (bool): Whether to run browser in headless mode
        retry_count (int): Number of retry attempts if driver setup fails
        
    Returns:
        webdriver.Chrome: Configured Chrome driver instance
        
    Raises:
        Exception: If driver setup fails after all retries
    """
    chrome_options = Options()
    
    # Basic bot-safe settings
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    # Realistic User-Agent
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    # Window size for better rendering
    chrome_options.add_argument("--window-size=1920,1080")
    
    # Additional stability options
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    
    if headless:
        chrome_options.add_argument("--headless")
    
    # Try to setup driver with retry mechanism
    for attempt in range(retry_count + 1):
        try:
            if attempt > 0:
                print(f"Retry attempt {attempt}/{retry_count}...")
                # Clear cache on retry
                clear_webdriver_cache()
                time.sleep(2)  # Wait a bit before retrying
            
            # Initialize driver using webdriver-manager
            # Use cache_valid_range to force fresh download if needed
            driver_manager = ChromeDriverManager()
            if attempt > 0:
                # Force fresh download on retry
                driver_path = driver_manager.install()
            else:
                driver_path = driver_manager.install()
            
            print(f"ChromeDriver path: {driver_path}")
            
            # Verify the driver file exists and is valid
            if not os.path.exists(driver_path):
                raise FileNotFoundError(f"ChromeDriver not found at: {driver_path}")
            
            # Create service with the driver path
            service = Service(driver_path)
            
            # Try to create the driver
            print("Initializing Chrome browser...")
            driver = webdriver.Chrome(service=service, options=chrome_options)
            
            # Execute script to remove webdriver property
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            print("Chrome driver initialized successfully!")
            return driver
            
        except OSError as e:
            error_msg = str(e)
            if "WinError 193" in error_msg or "not a valid Win32 application" in error_msg:
                print(f"ChromeDriver compatibility error (attempt {attempt + 1}/{retry_count + 1}):")
                print("  This usually means ChromeDriver is corrupted or incompatible.")
                if attempt < retry_count:
                    print("  Clearing cache and retrying...")
                    continue
                else:
                    print("\n" + "="*60)
                    print("ERROR: Could not initialize ChromeDriver after retries.")
                    print("="*60)
                    print("\nPossible solutions:")
                    print("1. Update Google Chrome to the latest version")
                    print("2. Manually download ChromeDriver from:")
                    print("   https://chromedriver.chromium.org/downloads")
                    print("3. Check if you have the correct architecture (32-bit vs 64-bit)")
                    print("4. Try running: pip install --upgrade webdriver-manager")
                    raise Exception("ChromeDriver initialization failed. See error messages above.")
            else:
                # Other OSError - re-raise
                raise
        except Exception as e:
            if attempt < retry_count:
                print(f"Error setting up driver (attempt {attempt + 1}): {e}")
                print("Retrying...")
                continue
            else:
                raise


def human_like_delay(min_seconds=1, max_seconds=3):
    """
    Adds a random human-like delay between actions.
    This helps avoid detection and mimics natural browsing behavior.
    
    Args:
        min_seconds (float): Minimum delay in seconds
        max_seconds (float): Maximum delay in seconds
    """
    import random
    delay = random.uniform(min_seconds, max_seconds)
    time.sleep(delay)


def set_location_whitefield(driver, pin_code=WHITEFIELD_PIN):
    """
    Sets the delivery location to Whitefield, Bangalore using PIN code.
    
    This function handles the location modal that appears when visiting Zepto.
    It looks for common location input patterns and submits the PIN code.
    
    Args:
        driver: Selenium WebDriver instance
        pin_code (str): PIN code to set (default: 560067 for Whitefield)
        
    Returns:
        bool: True if location was set successfully, False otherwise
    """
    try:
        print("=" * 60)
        print(f"SETTING LOCATION: Whitefield, Bangalore (PIN: {pin_code})")
        print("=" * 60)
        
        # Wait for page to load initially
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        human_like_delay(3, 4)
        
        # Strategy 1: Check if location is already set correctly
        print("\n[Strategy 1] Checking if location is already set...")
        page_text = driver.page_source.lower()
        current_url = driver.current_url.lower()
        
        # Check for Whitefield or PIN in page
        if "whitefield" in page_text or pin_code in page_text or "560067" in current_url:
            print(f"  [OK] Location appears to be already set to Whitefield ({pin_code})")
            # Double-check by looking for location display
            try:
                location_display = driver.find_elements(By.XPATH, "//*[contains(text(), 'Whitefield') or contains(text(), '560067')]")
                if location_display:
                    print("  [OK] Verified: Whitefield location found on page")
                    return True
            except:
                pass
        
        # Strategy 2: Look for location display/button in header and click it
        print("\n[Strategy 2] Looking for location button/display to click...")
        location_clicked = False
        
        # Try multiple ways to find and click location element
        location_find_strategies = [
            # XPath strategies (more flexible)
            ("//*[contains(@class, 'location') or contains(@class, 'Location')]", By.XPATH),
            ("//*[contains(text(), 'Road') or contains(text(), 'Cross')]", By.XPATH),
            ("//button[contains(@aria-label, 'location') or contains(@aria-label, 'Location')]", By.XPATH),
            ("//*[@role='button' and contains(., 'Road')]", By.XPATH),
            # CSS selector strategies
            ("[class*='location']", By.CSS_SELECTOR),
            ("[class*='Location']", By.CSS_SELECTOR),
            ("button[aria-label*='location']", By.CSS_SELECTOR),
            ("div[class*='location']", By.CSS_SELECTOR),
            ("span[class*='location']", By.CSS_SELECTOR),
        ]
        
        for selector, by_type in location_find_strategies:
            try:
                elements = driver.find_elements(by_type, selector)
                for elem in elements:
                    try:
                        if elem.is_displayed() and elem.is_enabled():
                            elem_text = elem.text.lower()
                            # Skip if it's clearly not a location button
                            if any(skip in elem_text for skip in ['login', 'cart', 'search']):
                                continue
                            print(f"  [FOUND] Location element: {elem.text[:50] if elem.text else 'No text'}")
                            # Scroll element into view
                            driver.execute_script("arguments[0].scrollIntoView(true);", elem)
                            human_like_delay(0.5, 1)
                            elem.click()
                            print("  [OK] Clicked location element")
                            location_clicked = True
                            human_like_delay(2, 3)
                            break
                    except Exception as e:
                        continue
                if location_clicked:
                    break
            except Exception as e:
                continue
        
        # Strategy 3: Look for location modal/popup with PIN input
        print("\n[Strategy 3] Looking for PIN code input field...")
        pin_input = None
        
        # Wait a bit for modal to appear if we clicked location
        if location_clicked:
            human_like_delay(2, 3)
        
        # Common selectors for location input
        location_input_selectors = [
            "input[placeholder*='PIN']",
            "input[placeholder*='Pin']",
            "input[placeholder*='pincode']",
            "input[placeholder*='Pincode']",
            "input[placeholder*='Enter PIN']",
            "input[placeholder*='Enter pin']",
            "input[type='text'][placeholder*='code']",
            "input[type='text'][placeholder*='PIN']",
            "input[name*='pin']",
            "input[name*='pincode']",
            "input[id*='pin']",
            "input[id*='pincode']",
            "input[class*='pin']",
            "input[class*='pincode']",
            # More generic
            "input[type='text']",
            "input[type='number']",
        ]
        
        for selector in location_input_selectors:
            try:
                # Try with longer wait if we clicked location
                wait_time = 8 if location_clicked else 5
                pin_input = WebDriverWait(driver, wait_time).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                )
                if pin_input and pin_input.is_displayed():
                    # Verify it's likely a PIN input (check placeholder or nearby text)
                    placeholder = pin_input.get_attribute("placeholder") or ""
                    if any(term in placeholder.lower() for term in ['pin', 'code', 'pincode']) or not placeholder:
                        print(f"  [OK] Found PIN input using: {selector}")
                        break
                    else:
                        pin_input = None
            except TimeoutException:
                continue
            except Exception as e:
                continue
        
        # Strategy 4: Try to find input by searching for text near it
        if pin_input is None:
            print("\n[Strategy 4] Searching for input near location-related text...")
            try:
                # Look for elements containing "PIN" or "pincode" text
                pin_text_elements = driver.find_elements(By.XPATH, "//*[contains(text(), 'PIN') or contains(text(), 'pincode') or contains(text(), 'Pincode')]")
                for text_elem in pin_text_elements:
                    try:
                        # Find nearby input
                        nearby_input = text_elem.find_element(By.XPATH, "./following::input[1] | ./preceding::input[1] | ./ancestor::*//input[1]")
                        if nearby_input and nearby_input.is_displayed():
                            print("  [OK] Found input near PIN text")
                            pin_input = nearby_input
                            break
                    except:
                        continue
            except Exception as e:
                pass
        
        # If we found the input, enter PIN and submit
        if pin_input:
            print(f"\n[ACTION] Entering PIN code: {pin_code}")
            try:
                # Clear and enter PIN
                pin_input.clear()
                human_like_delay(0.5, 1)
                pin_input.click()  # Focus the input
                human_like_delay(0.5, 1)
                pin_input.send_keys(pin_code)
                print(f"  [OK] Entered PIN: {pin_code}")
                human_like_delay(1, 2)
                
                # Look for submit/confirm button
                print("\n[ACTION] Looking for submit button...")
                submit_selectors = [
                    "button[type='submit']",
                    "button:contains('Apply')",
                    "button:contains('Confirm')",
                    "button:contains('Set')",
                    "button:contains('Go')",
                    "button:contains('Continue')",
                    "[class*='apply']",
                    "[class*='submit']",
                    "[class*='confirm']",
                ]
                
                submit_clicked = False
                for selector in submit_selectors:
                    try:
                        if ":contains" in selector:
                            # Use XPath for text contains
                            text = selector.split("'")[1]
                            submit_btn = driver.find_element(By.XPATH, f"//button[contains(text(), '{text}')]")
                        else:
                            submit_btn = driver.find_element(By.CSS_SELECTOR, selector)
                        
                        if submit_btn and submit_btn.is_displayed():
                            print(f"  [OK] Found submit button: {submit_btn.text[:30] if submit_btn.text else selector}")
                            submit_btn.click()
                            submit_clicked = True
                            human_like_delay(3, 4)
                            print("  [OK] Clicked submit button")
                            break
                    except (NoSuchElementException, TimeoutException):
                        continue
                
                # Try pressing Enter if button not found
                if not submit_clicked:
                    print("  [INFO] Submit button not found, trying Enter key...")
                    from selenium.webdriver.common.keys import Keys
                    pin_input.send_keys(Keys.RETURN)
                    human_like_delay(3, 4)
                    print("  [OK] Pressed Enter key")
                
                # Verify location was set
                print("\n[VERIFY] Checking if location was set successfully...")
                human_like_delay(2, 3)
                page_text_after = driver.page_source.lower()
                current_url_after = driver.current_url.lower()
                
                if pin_code in page_text_after or "whitefield" in page_text_after or pin_code in current_url_after:
                    print(f"  [SUCCESS] Location set to Whitefield ({pin_code})!")
                    return True
                else:
                    print("  [WARNING] Location may not have been set. Checking page...")
                    # Check for location display
                    try:
                        location_display = driver.find_elements(By.XPATH, f"//*[contains(text(), '{pin_code}') or contains(text(), 'Whitefield')]")
                        if location_display:
                            print("  [OK] Found location indicator on page")
                            return True
                    except:
                        pass
                    print("  [WARNING] Could not verify location was set")
                    return False
                    
            except Exception as e:
                print(f"  [ERROR] Error entering PIN: {str(e)}")
                return False
        else:
            print("\n[WARNING] Could not find PIN input field")
            print("  This might mean:")
            print("  - Location modal didn't open")
            print("  - Input field has different structure")
            print("  - Location is already set")
            return False
        
    except Exception as e:
        print(f"\n[ERROR] Error setting location: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def scroll_and_load_products(driver, max_scrolls=10, scroll_pause=2):
    """
    Scrolls the page to trigger lazy loading of products.
    
    Many e-commerce sites use infinite scroll or lazy loading. This function
    scrolls down the page incrementally to load more products.
    
    Args:
        driver: Selenium WebDriver instance
        max_scrolls (int): Maximum number of scroll actions to perform
        scroll_pause (float): Seconds to wait after each scroll
    """
    print("Scrolling to load products...")
    
    # Get initial page height
    last_height = driver.execute_script("return document.body.scrollHeight")
    
    for i in range(max_scrolls):
        # Scroll down to bottom
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        human_like_delay(scroll_pause, scroll_pause + 1)
        
        # Calculate new scroll height and compare with last scroll height
        new_height = driver.execute_script("return document.body.scrollHeight")
        
        if new_height == last_height:
            # No new content loaded, might have reached the end
            print(f"Reached end of page after {i+1} scrolls")
            break
        
        last_height = new_height
        print(f"Scroll {i+1}/{max_scrolls} - Page height: {new_height}px")
    
    # Scroll back to top for better visibility
    driver.execute_script("window.scrollTo(0, 0);")
    human_like_delay(1, 2)


def extract_product_data(driver):
    """
    Extracts product information from the current page.
    
    This function looks for product cards/containers and extracts:
    - Product Name
    - Price
    - Discount (if available)
    - Quantity/Size
    - Product Image URL
    - Product Page URL
    
    Args:
        driver: Selenium WebDriver instance
        
    Returns:
        list: List of dictionaries containing product data
    """
    products = []
    
    print("=" * 60)
    print("EXTRACTING PRODUCT DATA")
    print("=" * 60)
    print(f"Current URL: {driver.current_url}")
    
    # Wait for products to load
    try:
        print("Waiting for page to load...")
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        print("[OK] Page loaded")
    except TimeoutException:
        print("[ERROR] Page did not load properly")
        return products
    
    # Wait a bit more for dynamic content
    human_like_delay(2, 3)
    
    # Zepto-specific selectors - try multiple strategies
    print("\nSearching for product elements...")
    product_elements = []
    
    # Strategy 1: Look for product links (most reliable)
    print("Strategy 1: Looking for product links...")
    try:
        all_links = driver.find_elements(By.TAG_NAME, "a")
        print(f"  [INFO] Total links on page: {len(all_links)}")
        product_links = []
        banner_links = []
        
        for link in all_links:
            try:
                href = link.get_attribute("href") or ""
                text = link.text.lower()
                
                # Check if it's a product link - be more flexible
                is_product_link = False
                if href:
                    # Zepto product URLs might have different patterns
                    if any(pattern in href.lower() for pattern in ['/product', '/p/', '/item', 'product']):
                        is_product_link = True
                    # Also check if link contains product-like structure
                    elif 'zepto.com' in href.lower() and len(href) > 30:  # Product URLs are usually longer
                        # Check if it's not a category or homepage link
                        if not any(skip in href.lower() for skip in ['/category/', '/home', '/search', '/cn/']):
                            is_product_link = True
                
                if is_product_link:
                    # Check if it's a banner/promo (less strict filtering)
                    text_lower = text
                    if any(skip in text_lower for skip in ['explore', 'explore now', 'banner']):
                        banner_links.append(link)
                        continue
                    product_links.append(link)
            except Exception as e:
                continue
        
        print(f"  [INFO] Found {len(product_links)} potential product links")
        print(f"  [INFO] Found {len(banner_links)} banner/promo links (skipped)")
        
        if product_links:
            print(f"  [OK] Using {len(product_links)} product links")
            product_elements = product_links
        else:
            print("  [INFO] No product links found with '/product' pattern")
            # Try to find any clickable product-like elements
            print("  [INFO] Trying to find product containers by structure...")
    except Exception as e:
        print(f"  [ERROR] Error finding links: {e}")
    
    # Strategy 2: Look for product cards by class and structure
    if not product_elements:
        print("\nStrategy 2: Looking for product cards by class...")
        product_container_selectors = [
            "[class*='ProductCard']",
            "[class*='product-card']",
            "[class*='ProductCard__']",
            "[data-testid*='product']",
            "[data-testid*='ProductCard']",
            "article[class*='product']",
            "div[class*='Product']",
            "[class*='product-item']",
            "[data-product-id]",
            # More generic patterns
            "a[href*='zepto.com'][href*='/']",  # Any Zepto link that's not homepage
        ]
        
        for selector in product_container_selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    # Filter out banners and non-product elements
                    filtered = []
                    for elem in elements:
                        try:
                            text = (elem.text or "").lower()
                            href = (elem.get_attribute("href") or "").lower()
                            # Skip obvious banners
                            if any(skip in text for skip in ['explore', 'explore now', 'banner', 'up to 30% off']):
                                continue
                            # Skip category links
                            if '/category/' in href or '/cn/' in href:
                                continue
                            filtered.append(elem)
                        except:
                            continue
                    
                    if filtered:
                        print(f"  [OK] Found {len(filtered)} product elements using: {selector}")
                        product_elements = filtered
                        break
            except Exception as e:
                continue
    
    # Strategy 3: Look for product containers via images and structure
    if not product_elements:
        print("\nStrategy 3: Looking for product containers via images...")
        try:
            all_images = driver.find_elements(By.TAG_NAME, "img")
            print(f"  [INFO] Total images on page: {len(all_images)}")
            product_containers = []
            seen_hrefs = set()
            
            for img in all_images:
                try:
                    src = img.get_attribute("src") or ""
                    alt = (img.get_attribute("alt") or "").lower()
                    
                    # Try to find parent link/container
                    try:
                        # Look for parent <a> tag
                        parent = img.find_element(By.XPATH, "./ancestor::a[1]")
                        if parent:
                            href = parent.get_attribute("href") or ""
                            # Skip if we've seen this href before
                            if href and href in seen_hrefs:
                                continue
                            
                            # Check if it looks like a product (has price, name, etc.)
                            parent_text = (parent.text or "").lower()
                            
                            # Skip banners
                            if any(skip in parent_text for skip in ['explore', 'banner', 'up to 30%']):
                                continue
                            
                            # Check if image src suggests it's a product image
                            if any(pattern in src.lower() for pattern in ['product', 'item', 'cdn', 'image']) or '₹' in parent_text:
                                product_containers.append(parent)
                                if href:
                                    seen_hrefs.add(href)
                    except:
                        # If no parent <a>, try to find any clickable parent
                        try:
                            parent = img.find_element(By.XPATH, "./ancestor::*[@onclick or @href][1]")
                            if parent:
                                product_containers.append(parent)
                        except:
                            continue
                except:
                    continue
            
            if product_containers:
                print(f"  [OK] Found {len(product_containers)} product containers via images")
                product_elements = product_containers
            else:
                print("  [INFO] No product containers found via images")
        except Exception as e:
            print(f"  [ERROR] Error: {e}")
    
    # Strategy 4: Look for elements containing price (₹) - most reliable indicator
    if not product_elements:
        print("\nStrategy 4: Looking for elements containing price (₹)...")
        try:
            # Find all elements containing ₹ symbol
            price_elements = driver.find_elements(By.XPATH, "//*[contains(text(), '₹')]")
            print(f"  [INFO] Found {len(price_elements)} elements with ₹ symbol")
            
            product_containers = []
            for price_elem in price_elements:
                try:
                    # Get the parent container (likely the product card)
                    # Try to find the closest <a> tag or product container
                    container = price_elem.find_element(By.XPATH, "./ancestor::a[1] | ./ancestor::div[contains(@class, 'card') or contains(@class, 'item')][1]")
                    
                    if container:
                        container_text = (container.text or "").lower()
                        # Skip if it's a banner
                        if any(skip in container_text for skip in ['explore', 'banner', 'up to 30% off']):
                            continue
                        # Must have some product-like text (name, price, etc.)
                        if len(container_text) > 10:  # Has some content
                            product_containers.append(container)
                except:
                    continue
            
            # Remove duplicates
            seen = set()
            unique_containers = []
            for container in product_containers:
                try:
                    container_id = id(container)  # Use object id to avoid duplicates
                    if container_id not in seen:
                        seen.add(container_id)
                        unique_containers.append(container)
                except:
                    continue
            
            if unique_containers:
                print(f"  [OK] Found {len(unique_containers)} product containers via price elements")
                product_elements = unique_containers
            else:
                print("  [INFO] No product containers found via price")
        except Exception as e:
            print(f"  [ERROR] Error: {e}")
    
    # Strategy 5: Look for grid items as last resort
    if not product_elements:
        print("\nStrategy 5: Looking for grid items...")
        try:
            # Common grid patterns
            grid_selectors = [
                "[class*='grid'] [class*='item']",
                "[class*='Grid'] [class*='Item']",
                "div[class*='card']",
            ]
            for selector in grid_selectors:
                try:
                    elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements and len(elements) > 3:  # Likely products if many found
                        print(f"  [OK] Found {len(elements)} grid items")
                        product_elements = elements
                        break
                except:
                    continue
        except Exception as e:
            print(f"  [ERROR] Error: {e}")
    
    print(f"\n{'='*60}")
    print(f"Total product elements found: {len(product_elements)}")
    print(f"{'='*60}\n")
    
    if not product_elements:
        print("[WARNING] No product elements found!")
        print("This could mean:")
        print("  - Products haven't loaded yet (try scrolling)")
        print("  - Selectors need to be updated")
        print("  - Page structure has changed")
        print("\nTrying to get page source info...")
        try:
            page_text = driver.page_source[:1000]
            print(f"Page source preview: {page_text[:200]}...")
        except:
            pass
        return products
    
    # Extract all products (remove limit to get everything)
    for idx, product_element in enumerate(product_elements):
        try:
            product_data = {}
            
            # Extract product name
            name_selectors = [
                "h1", "h2", "h3", "h4",
                "[class*='title']",
                "[class*='name']",
                "[data-testid*='name']",
                "[data-testid*='title']",
            ]
            
            product_name = None
            for selector in name_selectors:
                try:
                    name_elem = product_element.find_element(By.CSS_SELECTOR, selector)
                    product_name = name_elem.text.strip()
                    if product_name:
                        break
                except:
                    continue
            
            if not product_name:
                # Try getting text from the product element itself
                element_text = product_element.text or ""
                if element_text:
                    # Get first meaningful line (skip empty lines)
                    lines = [line.strip() for line in element_text.split('\n') if line.strip()]
                    for line in lines:
                        # Skip price lines, discount lines, etc.
                        if not any(skip in line.lower() for skip in ['₹', 'off', '%', 'mins', 'pack', 'g', 'kg', 'pc']):
                            if len(line) > 3:  # Must be meaningful
                                product_name = line
                                break
                    # If still no name, use first line
                    if not product_name and lines:
                        product_name = lines[0]
            
            # Clean up product name
            if product_name:
                # Remove common suffixes that might be in the name
                product_name = product_name.strip()
                # Remove extra whitespace
                product_name = ' '.join(product_name.split())
            
            product_data['name'] = product_name if product_name else "Unknown"
            
            # Extract price - try multiple methods
            price = None
            import re
            
            # Method 1: Look for price in specific elements
            price_selectors = [
                "[class*='price']",
                "[class*='Price']",
                "[data-testid*='price']",
                "span",
                "div",
            ]
            
            for selector in price_selectors:
                try:
                    price_elems = product_element.find_elements(By.CSS_SELECTOR, selector)
                    for price_elem in price_elems:
                        price_text = price_elem.text.strip()
                        # Look for price pattern (₹ followed by numbers)
                        price_match = re.search(r'₹\s*(\d+(?:[.,]\d+)?)', price_text)
                        if price_match:
                            price = price_match.group(1).replace(',', '').replace('.', '')
                            # Make sure it's a reasonable price (not too large, likely a product price)
                            if price and 1 <= int(price) <= 100000:
                                break
                    if price:
                        break
                except:
                    continue
            
            # Method 2: Search in all text of the element
            if not price:
                try:
                    all_text = product_element.text or ""
                    # Find first price in text
                    price_match = re.search(r'₹\s*(\d+(?:[.,]\d+)?)', all_text)
                    if price_match:
                        price = price_match.group(1).replace(',', '').replace('.', '')
                        if price and 1 <= int(price) <= 100000:
                            pass  # Use this price
                        else:
                            price = None
                except:
                    pass
            
            product_data['price'] = price if price else "N/A"
            
            # Extract original price (struck-through price)
            original_price = None
            original_price_selectors = [
                "[class*='original']",
                "[class*='strike']",
                "s",
                "del",
                "[style*='line-through']",
            ]
            
            for selector in original_price_selectors:
                try:
                    orig_elem = product_element.find_element(By.CSS_SELECTOR, selector)
                    orig_text = orig_elem.text.strip()
                    import re
                    orig_match = re.search(r'₹?\s*(\d+[.,]?\d*)', orig_text)
                    if orig_match:
                        original_price = orig_match.group(1).replace(',', '')
                        break
                except:
                    continue
            
            product_data['original_price'] = original_price if original_price else "N/A"
            
            # Extract discount amount (e.g., "₹45 OFF")
            discount_amount = None
            discount_amount_selectors = [
                "[class*='discount']",
                "[class*='off']",
                "[class*='save']",
            ]
            
            for selector in discount_amount_selectors:
                try:
                    disc_elem = product_element.find_element(By.CSS_SELECTOR, selector)
                    disc_text = disc_elem.text.strip()
                    import re
                    # Look for "₹XX OFF" or "XX OFF"
                    disc_match = re.search(r'₹?\s*(\d+)\s*OFF', disc_text, re.IGNORECASE)
                    if disc_match:
                        discount_amount = f"₹{disc_match.group(1)}"
                        break
                except:
                    continue
            
            # Extract discount percentage
            discount_percent = None
            discount_selectors = [
                "[class*='discount']",
                "[class*='Discount']",
                "[class*='off']",
                "span:contains('%')",
            ]
            
            for selector in discount_selectors:
                try:
                    discount_elem = product_element.find_element(By.CSS_SELECTOR, selector)
                    discount_text = discount_elem.text.strip()
                    import re
                    discount_match = re.search(r'(\d+)%', discount_text)
                    if discount_match:
                        discount_percent = discount_match.group(1)
                        break
                except:
                    continue
            
            product_data['discount_amount'] = discount_amount if discount_amount else "N/A"
            product_data['discount_percent'] = f"{discount_percent}%" if discount_percent else "N/A"
            
            # Extract quantity/size
            quantity_selectors = [
                "[class*='quantity']",
                "[class*='size']",
                "[class*='weight']",
                "[class*='unit']",
            ]
            
            quantity = None
            for selector in quantity_selectors:
                try:
                    qty_elem = product_element.find_element(By.CSS_SELECTOR, selector)
                    quantity = qty_elem.text.strip()
                    if quantity:
                        break
                except:
                    continue
            
            product_data['quantity'] = quantity if quantity else "N/A"
            
            # Extract product image URL
            try:
                img_elem = product_element.find_element(By.TAG_NAME, "img")
                product_data['image_url'] = img_elem.get_attribute("src") or img_elem.get_attribute("data-src") or "N/A"
            except:
                product_data['image_url'] = "N/A"
            
            # Extract product page URL
            try:
                link_elem = product_element.find_element(By.TAG_NAME, "a")
                href = link_elem.get_attribute("href")
                if href:
                    if href.startswith("/"):
                        product_data['product_url'] = ZEPTO_URL + href
                    else:
                        product_data['product_url'] = href
                else:
                    product_data['product_url'] = "N/A"
            except:
                product_data['product_url'] = "N/A"
            
            # Only add product if it has at least a name (price can be N/A for some products)
            if product_data.get('name') and product_data['name'] != "Unknown" and len(product_data['name']) > 2:
                product_data['scraped_at'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                products.append(product_data)
                price_display = f"₹{product_data['price']}" if product_data.get('price') != "N/A" else "N/A"
                print(f"  [{idx+1}] [OK] {product_data['name'][:40]:<40} | {price_display}")
            else:
                # Debug: show what we found
                name_debug = product_data.get('name', 'None')[:30]
                price_debug = product_data.get('price', 'None')
                print(f"  [{idx+1}] [SKIP] Name: '{name_debug}' | Price: {price_debug}")
        
        except Exception as e:
            print(f"  [{idx+1}] [ERROR] {str(e)[:50]}")
            continue
    
    print(f"\n{'='*60}")
    print(f"EXTRACTION COMPLETE: {len(products)} products extracted!")
    print(f"{'='*60}\n")
    return products


def save_to_csv(products, filename=OUTPUT_CSV):
    """
    Saves product data to a CSV file.
    
    Args:
        products (list): List of product dictionaries
        filename (str): Output CSV file path
    """
    if not products:
        print("No products to save.")
        return
    
    import os
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    
    # Get all unique keys from products
    fieldnames = ['name', 'price', 'original_price', 'discount_amount', 'discount_percent', 'quantity', 'image_url', 'product_url', 'scraped_at']
    
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(products)
    
    print(f"Data saved to {filename}")


def save_to_json(products, filename=OUTPUT_JSON):
    """
    Saves product data to a JSON file (optional).
    
    Args:
        products (list): List of product dictionaries
        filename (str): Output JSON file path
    """
    if not products:
        print("No products to save.")
        return
    
    import os
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    
    with open(filename, 'w', encoding='utf-8') as jsonfile:
        json.dump(products, jsonfile, indent=2, ensure_ascii=False)
    
    print(f"Data saved to {filename}")


def check_for_404(driver):
    """
    Checks if the current page is a 404 error page.
    
    Args:
        driver: Selenium WebDriver instance
        
    Returns:
        bool: True if page is a 404 error, False otherwise
    """
    try:
        # Check for common 404 indicators
        page_text = driver.page_source.lower()
        if "404" in page_text or "page not found" in page_text or "egg-sit" in page_text:
            return True
        
        # Check URL
        current_url = driver.current_url.lower()
        if "404" in current_url:
            return True
        
        # Check page title
        page_title = driver.title.lower()
        if "404" in page_title or "not found" in page_title:
            return True
        
        return False
    except:
        return False


def navigate_to_fruits_vegetables_category(driver, use_direct_url=True):
    """
    Navigates to Fruits & Vegetables category.
    
    Args:
        driver: Selenium WebDriver instance
        use_direct_url (bool): If True, uses direct URL. If False, tries to find and click link.
        
    Returns:
        bool: True if navigation was successful, False otherwise
    """
    try:
        if use_direct_url:
            # Use the known working URL directly
            print(f"Navigating directly to Fruits & Vegetables category...")
            driver.get(FRUITS_VEGETABLES_URL)
            human_like_delay(3, 5)
            
            # Verify we're not on a 404 page
            if check_for_404(driver):
                print("[ERROR] Direct URL returned 404. Trying to find category link from homepage...")
                driver.get(ZEPTO_URL)
                human_like_delay(3, 5)
                return navigate_to_fruits_vegetables_category(driver, use_direct_url=False)
            
            # Check if page loaded successfully (look for product elements or category indicators)
            try:
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )
                print("[OK] Successfully navigated to Fruits & Vegetables category")
                return True
            except TimeoutException:
                print("[WARNING] Page may not have loaded completely")
                return True  # Still return True, let the scraper continue
        else:
            # Fallback: Try to find and click the category link
            print("Looking for Fruits & Vegetables category link...")
            
            # Wait for page to load
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            human_like_delay(2, 3)
            
            # Strategy 1: Look for category links with text containing "Fruits" or "Vegetables"
            category_link_texts = [
                "Fruits & Vegetables",
                "Fruits and Vegetables",
                "Fruits",
                "Vegetables",
                "fruits-vegetables",
                "Fruits & Veg",
            ]
            
            # Try finding links by text content
            for link_text in category_link_texts:
                try:
                    # Try XPath to find links containing the text
                    xpath = f"//a[contains(text(), '{link_text}') or contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{link_text.lower()}')]"
                    category_link = driver.find_element(By.XPATH, xpath)
                    if category_link and category_link.is_displayed():
                        print(f"Found category link: {link_text}")
                        category_link.click()
                        human_like_delay(3, 5)
                        
                        # Verify we're not on a 404 page
                        if check_for_404(driver):
                            print("[ERROR] Clicked link led to 404 page. Trying alternative method...")
                            continue
                        
                        print("[OK] Successfully navigated to Fruits & Vegetables category")
                        return True
                except (NoSuchElementException, TimeoutException):
                    continue
            
            print("[WARNING] Could not find Fruits & Vegetables category link automatically.")
            return False
        
    except Exception as e:
        print(f"[ERROR] Error navigating to category: {str(e)}")
        return False


def navigate_to_category_or_search(driver, search_term=None, category_url=None):
    """
    Navigates to a category page or performs a search.
    
    Args:
        driver: Selenium WebDriver instance
        search_term (str): Optional search term to search for
        category_url (str): Optional direct category URL (use with caution - may be 404)
    """
    if category_url:
        print(f"Navigating to category URL: {category_url}")
        driver.get(category_url)
        human_like_delay(3, 5)
        
        # Check if we got a 404
        if check_for_404(driver):
            print("[ERROR] Category URL returned 404 error!")
            print("Trying to find category link from homepage instead...")
            driver.get(ZEPTO_URL)
            human_like_delay(3, 5)
            navigate_to_fruits_vegetables_category(driver)
    elif search_term:
        print(f"Searching for: {search_term}")
        # Look for search input
        search_selectors = [
            "input[type='search']",
            "input[placeholder*='Search']",
            "input[name*='search']",
            "input[id*='search']",
        ]
        
        search_input = None
        for selector in search_selectors:
            try:
                search_input = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                )
                break
            except TimeoutException:
                continue
        
        if search_input:
            search_input.clear()
            search_input.send_keys(search_term)
            human_like_delay(1, 2)
            from selenium.webdriver.common.keys import Keys
            search_input.send_keys(Keys.RETURN)
            human_like_delay(3, 5)
        else:
            print("Search input not found. Please search manually.")
    else:
        # Just stay on homepage or navigate to a common category
        print("Staying on homepage. You can navigate manually if needed.")
        human_like_delay(2, 3)


def main():
    """
    Main function that orchestrates the scraping process.
    """
    driver = None
    
    try:
        print("=" * 60)
        print("Zepto Scraper - Whitefield, Bangalore (PIN: 560067)")
        print("=" * 60)
        
        # Step 1: Setup driver
        print("\n[1/5] Setting up Chrome driver...")
        driver = setup_driver(headless=HEADLESS_MODE)
        print("[OK] Driver initialized")
        
        # Step 2: Open Zepto homepage
        print("\n[2/5] Opening Zepto homepage...")
        driver.get(ZEPTO_URL)
        human_like_delay(3, 5)
        print("[OK] Homepage loaded")
        
        # Step 3: Set location to Whitefield
        print("\n[3/5] Setting delivery location...")
        location_set = set_location_whitefield(driver)
        if not location_set:
            print("\n" + "=" * 60)
            print("[IMPORTANT] Location was not set automatically!")
            print("=" * 60)
            print("\nPlease set the location manually:")
            print("1. Look for location button/display in the header (top of page)")
            print("2. Click on it to open location modal")
            print("3. Enter PIN code: 560067")
            print("4. Click Apply/Confirm/Go")
            print("\nAfter setting location, press Enter here to continue...")
            input("Press Enter after location is set to Whitefield (560067)...")
            print("\n[OK] Continuing with scraping...")
        else:
            print("\n[OK] Location set successfully! Continuing...")
        
        # Step 4: Navigate to Fruits & Vegetables category
        print("\n[4/5] Navigating to Fruits & Vegetables category...")
        print(f"URL: {FRUITS_VEGETABLES_URL}")
        category_navigated = navigate_to_fruits_vegetables_category(driver, use_direct_url=True)
        if not category_navigated:
            print("\n[WARNING] Could not navigate automatically.")
            print("Please navigate to Fruits & Vegetables category manually in the browser.")
            input("Press Enter after you've navigated to the category page...")
        else:
            print("[OK] Navigated to Fruits & Vegetables category")
        
        # Verify we're not on a 404 page
        if check_for_404(driver):
            print("\n[ERROR] Page is showing 404 error!")
            print("Trying direct URL again...")
            driver.get(FRUITS_VEGETABLES_URL)
            human_like_delay(3, 5)
            if check_for_404(driver):
                print("[ERROR] Still getting 404. Please navigate manually.")
                input("Press Enter after you've navigated to the category page...")
        
        # Wait for products to load
        human_like_delay(3, 5)
        
        # Step 5: Scroll to load all products
        print("\n[5/5] Scrolling to load all products...")
        scroll_and_load_products(driver, max_scrolls=10)  # Increased to get all products
        
        # Step 6: Extract product data
        print("\nExtracting product data...")
        products = extract_product_data(driver)
        
        if products:
            # Step 7: Save to files
            print("\nSaving data...")
            save_to_csv(products)
            save_to_json(products)
            print(f"\n[SUCCESS] Successfully scraped {len(products)} products!")
        else:
            print("\n[WARNING] No products found. This could be because:")
            print("  - Location is not set correctly")
            print("  - No products available for this location")
            print("  - Selectors need to be updated (Zepto may have changed their HTML)")
            print("  - You need to navigate to a category/search page manually")
        
        print("\n" + "=" * 60)
        print("Scraping completed!")
        print("=" * 60)
        
        # Keep browser open for a few seconds to verify
        if not HEADLESS_MODE:
            print("\nBrowser will close in 10 seconds...")
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
