"""
Simple Zepto Scraper - Fruits & Vegetables
Just navigate and extract. No complex logic.
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time
import csv
import json
from datetime import datetime
import os
import re

# Configuration
FRUITS_VEGETABLES_URL = "https://www.zepto.com/cn/fruits-vegetables/fruits-vegetables/cid/64374cfe-d06f-4a01-898e-c07c46462c36/scid/e78a8422-5f20-4e4b-9a9f-22a0e53962e3"
OUTPUT_CSV = "output/zepto_products.csv"
OUTPUT_JSON = "output/zepto_products.json"

def setup_driver():
    """Setup Chrome driver with error suppression."""
    chrome_options = Options()
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
    
    # Suppress console errors and warnings
    chrome_options.add_argument("--log-level=3")  # Only fatal errors
    chrome_options.add_argument("--disable-logging")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging"])
    
    # Additional stability options
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-extensions")
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
    return driver

def scroll_page(driver, times=15):
    """Scroll page to load products."""
    print("Scrolling to load products...")
    last_count = 0
    for i in range(times):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        
        # Check how many products are visible now
        try:
            current_count = len(driver.find_elements(By.XPATH, "//*[contains(text(), '₹')]"))
            if current_count > last_count:
                print(f"  Scroll {i+1}/{times} - Found {current_count} price elements")
                last_count = current_count
            else:
                print(f"  Scroll {i+1}/{times}")
        except:
            print(f"  Scroll {i+1}/{times}")
    
    # Scroll back to top
    driver.execute_script("window.scrollTo(0, 0);")
    time.sleep(2)

def extract_products(driver):
    """Extract products from current page - SIMPLE AND RELIABLE."""
    print("\nExtracting products...")
    products = []
    
    # Wait for page to fully load
    print("  Waiting for page to fully load...")
    time.sleep(5)
    
    # Verify we're on the right page
    current_url = driver.current_url
    print(f"  Current URL: {current_url[:80]}...")
    
    if "fruits-vegetables" not in current_url.lower():
        print("  [WARNING] Might not be on Fruits & Vegetables page!")
    
    # PRIMARY METHOD: Find all elements with price (₹) - most reliable
    print("  Finding products by looking for price (₹)...")
    try:
        # Wait for price elements to appear
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//*[contains(text(), '₹')]"))
            )
        except:
            print("  [WARNING] No price elements found yet, continuing anyway...")
        
        price_elements = driver.find_elements(By.XPATH, "//*[contains(text(), '₹')]")
        print(f"  Found {len(price_elements)} elements with ₹ symbol")
        
        if len(price_elements) == 0:
            print("  [ERROR] No price elements found!")
            print("  This means products might not be loaded.")
            print("  Trying to refresh and wait longer...")
            driver.refresh()
            time.sleep(8)
            price_elements = driver.find_elements(By.XPATH, "//*[contains(text(), '₹')]")
            print(f"  After refresh: Found {len(price_elements)} elements with ₹")
        
        if len(price_elements) == 0:
            print("\n[ERROR] No products found on page!")
            print("  Possible reasons:")
            print("    1. Location not set correctly")
            print("    2. Products haven't loaded yet")
            print("    3. Page structure is different")
            return products
        
        # Group by parent container to avoid duplicates
        product_containers = {}
        
        for price_elem in price_elements:
            try:
                # Get parent container (product card)
                try:
                    # Try to get <a> tag parent first (most common)
                    container = price_elem.find_element(By.XPATH, "./ancestor::a[1]")
                except:
                    # If no <a>, get closest div that likely contains the product
                    try:
                        container = price_elem.find_element(By.XPATH, "./ancestor::div[position()<=5][1]")
                    except:
                        # Last resort: use the element itself
                        container = price_elem
                
                # Use container's text as key to avoid duplicates
                container_text = (container.text or "").strip()[:100]  # First 100 chars as key
                
                if container_text and len(container_text) > 10:  # Must have some content
                    # Skip banners and promotional content
                    text_lower = container_text.lower()
                    if "explore" not in text_lower and "banner" not in text_lower and "up to 30%" not in text_lower:
                        # Use a more unique key (first line + price)
                        price_match = re.search(r'₹\s*(\d+)', container_text)
                        if price_match:
                            key = container_text.split('\n')[0] + "|" + price_match.group(1)
                        else:
                            key = container_text[:50]
                        
                        if key not in product_containers:
                            product_containers[key] = container
            except Exception as e:
                continue
        
        product_list = list(product_containers.values())
        print(f"  Found {len(product_list)} unique product containers")
        
        if len(product_list) == 0:
            print("\n[ERROR] Could not extract product containers!")
            return products
        
        # Extract data from each product
        print(f"\n  Extracting data from {len(product_list)} products...")
        for idx, container in enumerate(product_list):
            try:
                product = {}
                
                # Get all text from container
                container_text = (container.text or "").strip()
                lines = [l.strip() for l in container_text.split('\n') if l.strip()]
                
                # Get product URL first (most reliable for name extraction)
                href = None
                try:
                    href = container.get_attribute("href")
                    if not href:
                        try:
                            a_tag = container.find_element(By.TAG_NAME, "a")
                            href = a_tag.get_attribute("href") or ""
                        except:
                            # Try finding any link in container
                            try:
                                a_tag = container.find_element(By.XPATH, ".//a[@href]")
                                href = a_tag.get_attribute("href") or ""
                            except:
                                pass
                except:
                    pass
                
                # Extract product name - PRIORITIZE URL (most reliable)
                product_name = None
                
                # Strategy 1: Extract from product URL (MOST RELIABLE)
                if href and "/pn/" in href:
                    try:
                        # URL format: /pn/product-name-slug/pvid/...
                        url_parts = href.split("/pn/")
                        if len(url_parts) > 1:
                            product_slug = url_parts[1].split("/")[0]
                            # Convert slug to readable name
                            # e.g., "strawberry-mahabaleshwar" -> "Strawberry (Mahabaleshwar)"
                            name_parts = product_slug.split("-")
                            # Capitalize first letter of each word
                            product_name = " ".join(word.capitalize() for word in name_parts)
                            # Handle special cases like "(mahabaleshwar)" -> "(Mahabaleshwar)"
                            product_name = re.sub(r'\((\w+)', r'(\1', product_name)
                    except:
                        pass
                
                # Strategy 2: Look for product name in specific DOM elements
                if not product_name:
                    try:
                        name_selectors = [
                            "h1", "h2", "h3", "h4",
                            "span[class*='name']",
                            "span[class*='title']",
                            "div[class*='name']",
                            "div[class*='title']",
                            "p[class*='name']",
                            "div[class*='product']",
                        ]
                        for selector in name_selectors:
                            try:
                                name_elem = container.find_element(By.CSS_SELECTOR, selector)
                                name_text = (name_elem.text or "").strip()
                                # Must be meaningful and not a button
                                if name_text and len(name_text) > 3:
                                    name_upper = name_text.upper()
                                    if name_upper not in ["ADD", "NOTIFY", "EXPLORE", "EXPLORE NOW", "BUY NOW"]:
                                        if not re.match(r'^₹\s*\d+', name_text):  # Not a price
                                            product_name = name_text
                                            break
                            except:
                                continue
                    except:
                        pass
                
                # Strategy 3: Find name in text lines (skip buttons, prices, etc.)
                if not product_name:
                    for line in lines:
                        line_clean = line.strip()
                        # Skip buttons and common UI text
                        if line_clean.upper() in ["ADD", "NOTIFY", "EXPLORE", "EXPLORE NOW", "BUY NOW"]:
                            continue
                        # Skip if it's a price
                        if re.match(r'^₹\s*\d+', line_clean):
                            continue
                        # Skip if it's discount
                        if re.match(r'^₹\s*\d+\s*OFF', line_clean, re.IGNORECASE):
                            continue
                        # Skip if it's delivery time
                        if 'mins' in line_clean.lower() or 'min' in line_clean.lower():
                            continue
                        # Skip if it's just quantity (starts with number + unit)
                        if re.match(r'^\d+\s*(pack|g|kg|ml|l|pc|pcs|Approx)', line_clean, re.IGNORECASE):
                            continue
                        # Skip if it's a category header
                        if "price list" in line_clean.lower() or ("fruits" in line_clean.lower() and "vegetables" in line_clean.lower()):
                            continue
                        # Skip if it's just a number or weight
                        if re.match(r'^\d+[\s-]+\d+\s*(g|kg)', line_clean, re.IGNORECASE):
                            continue
                        # Must have meaningful text
                        if len(line_clean) > 3 and not line_clean.isdigit():
                            product_name = line_clean
                            break
                
                product['name'] = product_name if product_name else "Unknown"
                
                # Extract price
                price_match = re.search(r'₹\s*(\d+)', container_text)
                if price_match:
                    product['price'] = price_match.group(1)
                else:
                    product['price'] = "N/A"
                
                # Extract discount
                discount_match = re.search(r'₹\s*(\d+)\s*OFF', container_text, re.IGNORECASE)
                if discount_match:
                    product['discount'] = f"₹{discount_match.group(1)}"
                else:
                    product['discount'] = "N/A"
                
                # Extract quantity
                qty_match = re.search(r'(\d+\s*(?:pack|g|kg|pc|pcs|ml|l|Approx\.))', container_text, re.IGNORECASE)
                if qty_match:
                    product['quantity'] = qty_match.group(1)
                else:
                    product['quantity'] = "N/A"
                
                # Save product URL (already extracted above)
                product['product_url'] = href if href else "N/A"
                
                # Get image URL
                try:
                    img = container.find_element(By.TAG_NAME, "img")
                    product['image_url'] = img.get_attribute("src") or img.get_attribute("data-src") or "N/A"
                except:
                    product['image_url'] = "N/A"
                
                # Only add if we have a valid name (not "Unknown" or button text)
                if product.get('name') and product['name'] != "Unknown" and len(product['name']) > 2:
                    # Double-check: skip if name is still a button
                    name_upper = product['name'].upper()
                    if name_upper not in ["ADD", "NOTIFY", "EXPLORE", "BUY NOW"]:
                        product['scraped_at'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        products.append(product)
                        price_display = f"₹{product['price']}" if product['price'] != "N/A" else "N/A"
                        print(f"  [{len(products)}] {product['name'][:50]:<50} | {price_display}")
            
            except Exception as e:
                continue
        
    except Exception as e:
        print(f"  [ERROR] {str(e)}")
        import traceback
        traceback.print_exc()
    
    return products

def save_data(products):
    """Save products to CSV and JSON."""
    if not products:
        print("No products to save!")
        return
    
    os.makedirs(os.path.dirname(OUTPUT_CSV), exist_ok=True)
    
    # Save CSV
    with open(OUTPUT_CSV, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['name', 'price', 'discount', 'quantity', 'image_url', 'product_url', 'scraped_at'])
        writer.writeheader()
        writer.writerows(products)
    
    # Save JSON
    with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
        json.dump(products, f, indent=2, ensure_ascii=False)
    
    print(f"\nSaved {len(products)} products to:")
    print(f"  - {OUTPUT_CSV}")
    print(f"  - {OUTPUT_JSON}")

def main():
    """Main function."""
    driver = None
    
    try:
        print("=" * 60)
        print("Simple Zepto Scraper - Fruits & Vegetables")
        print("=" * 60)
        
        # Setup
        print("\n[1/4] Setting up browser...")
        driver = setup_driver()
        print("  [OK] Browser ready")
        
        # Navigate to homepage
        print("\n[2/4] Opening Zepto homepage...")
        driver.get("https://www.zepto.com")
        time.sleep(3)
        print("  [OK] Homepage loaded")
        
        # Wait for user to set location
        print("\n" + "=" * 60)
        print("IMPORTANT: Set location to Whitefield (560067) in the browser")
        print("=" * 60)
        input("Press Enter after you've set the location...")
        
        # Navigate to Fruits & Vegetables
        print("\n[3/4] Navigating to Fruits & Vegetables category...")
        driver.get(FRUITS_VEGETABLES_URL)
        print("  Waiting for page to load...")
        time.sleep(8)
        
        # Wait for products to appear
        try:
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.XPATH, "//*[contains(text(), '₹')]"))
            )
            print("  [OK] Products detected on page")
        except:
            print("  [WARNING] Waiting a bit more...")
            time.sleep(5)
        
        print("  [OK] Category page loaded")
        
        # Scroll to load products (more scrolls to get all products)
        scroll_page(driver, times=15)
        
        # Extract products
        print("\n[4/4] Extracting products...")
        products = extract_products(driver)
        
        if products:
            save_data(products)
            print(f"\n[SUCCESS] Extracted {len(products)} products!")
        else:
            print("\n[ERROR] No products found!")
            print("Make sure:")
            print("  1. Location is set correctly (560067)")
            print("  2. You're on the Fruits & Vegetables page")
            print("  3. Products are visible in the browser")
            print(f"  4. Current URL: {driver.current_url}")
        
        print("\n" + "=" * 60)
        print("Done! Browser will close in 10 seconds...")
        time.sleep(10)
    
    except Exception as e:
        print(f"\n[ERROR] {str(e)}")
        import traceback
        traceback.print_exc()
    
    finally:
        if driver:
            driver.quit()
            print("Browser closed.")

if __name__ == "__main__":
    main()
