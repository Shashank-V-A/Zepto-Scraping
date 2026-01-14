"""
Zepto Scraper - Meat, Fish & Eggs Category
Extracts all products from the Meat, Fish & Eggs category with accurate values.
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
# TODO: Replace with the actual Meat, Fish & Eggs category URL
# You can find this by navigating to the category in your browser and copying the URL
MEAT_FISH_EGGS_URL = "https://www.zepto.com/cn/meats-fish-eggs/meats-fish-eggs/cid/4654bd8a-fb30-4ee1-ab30-4bf581b6c6e3/scid/95157c69-f03e-48e5-ae2f-d947af34397f"  # Update this
OUTPUT_CSV = "output/zepto_meat_fish_eggs.csv"
OUTPUT_JSON = "output/zepto_meat_fish_eggs.json"

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

def is_valid_product(product):
    """
    Check if product belongs to Meat, Fish & Eggs categories.
    Returns True if valid, False otherwise.
    """
    name = (product.get('name') or '').lower()
    url = (product.get('product_url') or '').lower()
    combined_text = f"{name} {url}".lower()
    
    # Keywords that indicate invalid products (should be excluded)
    invalid_keywords = [
        'bread', 'biryani', 'kit', 'incl. of all taxes', 'buy ', 'online',
        'marinade', 'snack', 'sauce', 'spice', 'masala', 'marination'
    ]
    
    # Check for invalid keywords first
    for invalid_kw in invalid_keywords:
        if invalid_kw in combined_text:
            # Exception: "marinade" in combo products might be okay if it's part of a meat combo
            if invalid_kw == 'marinade' and any(kw in combined_text for kw in ['chicken', 'fish', 'mutton', 'meat']):
                continue
            if invalid_kw in ['bread', 'biryani', 'kit']:
                return False
            if invalid_kw in ['incl. of all taxes', 'buy ', 'online']:
                return False
    
    # Keywords that indicate valid products
    valid_keywords = [
        # Meat
        'chicken', 'mutton', 'lamb', 'goat', 'beef', 'pork', 'meat',
        # Fish & Seafood
        'fish', 'prawn', 'shrimp', 'crab', 'lobster', 'squid', 'octopus',
        'seafood', 'salmon', 'tuna', 'rohu', 'katla', 'pomfret', 'bangda',
        # Eggs
        'egg', 'eggs',
        # Cold Cuts
        'sausage', 'salami', 'ham', 'bacon', 'cold cut', 'cold cuts',
        # Frozen Meat
        'frozen meat', 'frozen chicken', 'frozen fish'
    ]
    
    # Check if product name or URL contains valid keywords
    for valid_kw in valid_keywords:
        if valid_kw in combined_text:
            return True
    
    # If no valid keywords found, exclude it
    return False

def find_subcategories(driver):
    """Find subcategory links (Chicken, Fish, Mutton, Eggs, Cold Cuts, etc.) on the category page."""
    subcategory_urls = []
    subcategory_names = []
    
    print("\n  Looking for subcategories (Chicken, Fish, Mutton, Eggs, Cold Cuts, etc.)...")
    
    # Common subcategory keywords - ONLY for Meat, Fish & Eggs
    subcategory_keywords = [
        "chicken", "fish", "mutton", "egg", "eggs", "seafood", "prawn", "shrimp",
        "cold cut", "cold cuts", "sausage", "salami", "frozen meat", "lamb", "goat"
    ]
    
    # Exclude these subcategories
    excluded_keywords = [
        "marinade", "snack", "sauce", "spice", "masala", "bread", "biryani"
    ]
    
    try:
        # Strategy 1: Look for links that might be subcategories
        all_links = driver.find_elements(By.TAG_NAME, "a")
        
        for link in all_links:
            try:
                href = link.get_attribute("href") or ""
                text = (link.text or "").strip().lower()
                
                # Check if it's a subcategory link
                if href and "zepto.com" in href:
                    # Check if URL contains category indicators
                    url_lower = href.lower()
                    if any(keyword in url_lower for keyword in subcategory_keywords):
                        # Check if text matches subcategory keywords OR if URL clearly indicates a subcategory
                        is_subcategory = False
                        
                        # First check: exclude if it contains excluded keywords
                        if any(excluded_kw in text or excluded_kw in url_lower for excluded_kw in excluded_keywords):
                            continue
                        
                        if any(keyword in text for keyword in subcategory_keywords):
                            is_subcategory = True
                        elif "/cn/" in href and "/pn/" not in href:
                            # If it's a category URL (not product), it might be a subcategory
                            # Check if it's different from the main category URL
                            if "meats-fish-eggs" not in url_lower or len([k for k in ["chicken", "fish", "mutton", "egg"] if k in url_lower]) == 1:
                                # Make sure it doesn't contain excluded keywords
                                if not any(excluded_kw in url_lower for excluded_kw in excluded_keywords):
                                    is_subcategory = True
                        
                        if is_subcategory and href not in subcategory_urls:
                            subcategory_urls.append(href)
                            subcategory_names.append(link.text.strip() or href.split("/")[-1])
                            print(f"    Found subcategory: {link.text.strip()[:50] if link.text.strip() else href[:50]}")
            except:
                continue
        
        # Strategy 2: Look for subcategory sections by text patterns (only valid categories)
        try:
            for keyword in ["Chicken", "Fish", "Mutton", "Egg", "Eggs", "Seafood", "Prawn", "Cold Cut", "Sausage"]:
                # Skip if keyword is in excluded list
                if keyword.lower() in [kw.lower() for kw in excluded_keywords]:
                    continue
                try:
                    # Find elements with the keyword and get their parent links
                    xpath = f"//a[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{keyword.lower()}')]"
                    elements = driver.find_elements(By.XPATH, xpath)
                    for elem in elements:
                        try:
                            href = elem.get_attribute("href") or ""
                            if href and "zepto.com" in href and "/cn/" in href and "/pn/" not in href:
                                if href not in subcategory_urls:
                                    subcategory_urls.append(href)
                                    subcategory_names.append(elem.text.strip() or keyword)
                                    print(f"    Found subcategory via text search: {elem.text.strip()[:50] if elem.text.strip() else keyword}")
                        except:
                            continue
                except:
                    continue
        except:
            pass
        
        # Strategy 3: If we found the main category page, try to construct subcategory URLs
        current_url = driver.current_url
        if "meats-fish-eggs" in current_url.lower() or "meat" in current_url.lower():
            # Try common subcategory URL patterns (only valid ones)
            base_url = current_url.split("/cn/")[0] + "/cn/"
            potential_subcategories = [
                ("chicken", "chicken"),
                ("fish", "fish"),
                ("seafood", "seafood"),
                ("mutton", "mutton"),
                ("lamb", "lamb"),
                ("goat", "goat"),
                ("egg", "egg"),
                ("eggs", "eggs"),
                ("cold-cut", "cold cuts"),
                ("cold-cuts", "cold cuts"),
                ("sausage", "sausage"),
                ("frozen-meat", "frozen meat"),
            ]
            
            for sub_path, sub_name in potential_subcategories:
                try:
                    # Try to find if this subcategory exists by looking for links
                    test_url = base_url + sub_path
                    # Don't add if we already have it
                    if not any(test_url in url for url in subcategory_urls):
                        # Check if there's a link to this subcategory on the page
                        test_links = driver.find_elements(By.XPATH, f"//a[contains(@href, '{sub_path}')]")
                        if test_links:
                            for link in test_links:
                                href = link.get_attribute("href") or ""
                                if href and "/cn/" in href and "/pn/" not in href and href not in subcategory_urls:
                                    subcategory_urls.append(href)
                                    subcategory_names.append(sub_name.capitalize())
                                    print(f"    Found subcategory via URL pattern: {sub_name.capitalize()}")
                                    break
                except:
                    continue
        
    except Exception as e:
        print(f"    [WARNING] Error finding subcategories: {str(e)}")
    
    # Remove duplicates
    seen = set()
    unique_urls = []
    unique_names = []
    for url, name in zip(subcategory_urls, subcategory_names):
        if url not in seen:
            seen.add(url)
            unique_urls.append(url)
            unique_names.append(name)
    
    return unique_urls, unique_names

def scroll_page(driver, times=25):
    """Scroll page to load products - stops when no new products found."""
    print("Scrolling to load products...")
    last_count = 0
    no_change_count = 0
    max_no_change = 3  # Stop if no new products for 3 consecutive scrolls
    
    for i in range(times):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2.5)  # Slightly longer wait for lazy loading
        
        # Check how many products are visible now
        try:
            current_count = len(driver.find_elements(By.XPATH, "//*[contains(text(), '₹')]"))
            if current_count > last_count:
                print(f"  Scroll {i+1}/{times} - Found {current_count} price elements (+{current_count - last_count} new)")
                last_count = current_count
                no_change_count = 0  # Reset counter
            else:
                no_change_count += 1
                print(f"  Scroll {i+1}/{times} - No new products ({current_count} total)")
                
                # If no new products for several scrolls, we might be done
                if no_change_count >= max_no_change:
                    print(f"  No new products for {max_no_change} scrolls. Assuming all products loaded.")
                    break
        except:
            print(f"  Scroll {i+1}/{times}")
            no_change_count += 1
    
    print(f"\n  Final count: {last_count} price elements found")
    
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
    
    if "meat" not in current_url.lower() and "fish" not in current_url.lower() and "egg" not in current_url.lower():
        print("  [WARNING] Might not be on Meat, Fish & Eggs page!")
    
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
                
                # Get product URL for unique identification
                href = None
                try:
                    href = container.get_attribute("href")
                    if not href:
                        try:
                            a_tag = container.find_element(By.XPATH, ".//a[@href]")
                            href = a_tag.get_attribute("href") or ""
                        except:
                            pass
                except:
                    pass
                
                # Use container's text as key to avoid duplicates
                container_text = (container.text or "").strip()[:100]  # First 100 chars as key
                
                if container_text and len(container_text) > 10:  # Must have some content
                    # Skip banners and promotional content
                    text_lower = container_text.lower()
                    if "explore" not in text_lower and "banner" not in text_lower and "up to 30%" not in text_lower:
                        # Use URL as primary key (most unique), fallback to text+price
                        if href and "/pn/" in href:
                            # Extract product ID from URL for unique key
                            try:
                                url_parts = href.split("/pvid/")
                                if len(url_parts) > 1:
                                    product_id = url_parts[1].split("/")[0].split("?")[0]
                                    key = product_id  # Most unique identifier
                                else:
                                    # Fallback to URL slug
                                    url_slug = href.split("/pn/")[1].split("/")[0] if "/pn/" in href else ""
                                    price_match = re.search(r'₹\s*(\d+)', container_text)
                                    key = f"{url_slug}|{price_match.group(1) if price_match else 'no_price'}"
                            except:
                                price_match = re.search(r'₹\s*(\d+)', container_text)
                                key = f"{container_text.split('\n')[0][:30]}|{price_match.group(1) if price_match else 'no_price'}"
                        else:
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
                            # e.g., "chicken-breast-boneless" -> "Chicken Breast Boneless"
                            name_parts = product_slug.split("-")
                            # Capitalize first letter of each word
                            product_name = " ".join(word.capitalize() for word in name_parts)
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
                        if "price list" in line_clean.lower() or ("meat" in line_clean.lower() and "fish" in line_clean.lower()):
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
                        # Filter: Only include Meat, Fish & Eggs products
                        if is_valid_product(product):
                            product['scraped_at'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            products.append(product)
                            price_display = f"₹{product['price']}" if product['price'] != "N/A" else "N/A"
                            print(f"  [{len(products)}] {product['name'][:50]:<50} | {price_display}")
                        # else: silently skip invalid products
            
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
        print("Zepto Scraper - Meat, Fish & Eggs Category")
        print("=" * 60)
        
        # Check if URL is set
        if "..." in MEAT_FISH_EGGS_URL:
            print("\n[IMPORTANT] Category URL not configured!")
            print("Please update MEAT_FISH_EGGS_URL in the script with the actual category URL.")
            print("\nTo find the URL:")
            print("  1. Open Zepto in your browser")
            print("  2. Navigate to 'Meat, Fish & Eggs' category")
            print("  3. Copy the full URL from the address bar")
            print("  4. Update MEAT_FISH_EGGS_URL in this script")
            print("\nOr you can provide it now:")
            user_url = input("Enter the Meat, Fish & Eggs category URL (or press Enter to exit): ").strip()
            if not user_url:
                print("Exiting...")
                return
            category_url = user_url
        else:
            category_url = MEAT_FISH_EGGS_URL
        
        # Setup
        print("\n[1/5] Setting up browser...")
        driver = setup_driver()
        print("  [OK] Browser ready")
        
        # Navigate to homepage
        print("\n[2/5] Opening Zepto homepage...")
        driver.get("https://www.zepto.com")
        time.sleep(3)
        print("  [OK] Homepage loaded")
        
        # Wait for user to set location
        print("\n" + "=" * 60)
        print("IMPORTANT: Set location to Whitefield (560067) in the browser")
        print("=" * 60)
        input("Press Enter after you've set the location...")
        
        # Navigate to main category page
        print("\n[3/5] Navigating to Meat, Fish & Eggs category...")
        driver.get(category_url)
        print("  Waiting for page to load...")
        time.sleep(8)
        
        # Find subcategories
        print("\n[4/5] Finding subcategories...")
        subcategory_urls, subcategory_names = find_subcategories(driver)
        
        all_products = []
        all_product_urls = set()  # To track unique products across subcategories
        
        # Extract from main category page first
        print("\n  Extracting from main category page...")
        try:
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.XPATH, "//*[contains(text(), '₹')]"))
            )
            scroll_page(driver, times=25)
            main_products = extract_products(driver)
            for product in main_products:
                if product.get('product_url') and product['product_url'] not in all_product_urls:
                    all_products.append(product)
                    all_product_urls.add(product['product_url'])
            print(f"  Extracted {len(main_products)} products from main page")
        except:
            print("  [WARNING] Could not extract from main page, continuing with subcategories...")
        
        # Extract from each subcategory
        if subcategory_urls:
            print(f"\n  Found {len(subcategory_urls)} subcategories. Extracting from each...")
            for idx, (sub_url, sub_name) in enumerate(zip(subcategory_urls, subcategory_names), 1):
                try:
                    print(f"\n  [{idx}/{len(subcategory_urls)}] Extracting from: {sub_name[:50]}")
                    driver.get(sub_url)
                    time.sleep(5)
                    
                    # Wait for products
                    try:
                        WebDriverWait(driver, 15).until(
                            EC.presence_of_element_located((By.XPATH, "//*[contains(text(), '₹')]"))
                        )
                    except:
                        print("    [WARNING] No products found, skipping...")
                        continue
                    
                    # Scroll to load all products
                    scroll_page(driver, times=25)
                    
                    # Extract products
                    sub_products = extract_products(driver)
                    
                    # Add unique products
                    added_count = 0
                    for product in sub_products:
                        if product.get('product_url') and product['product_url'] not in all_product_urls:
                            all_products.append(product)
                            all_product_urls.add(product['product_url'])
                            added_count += 1
                    
                    print(f"    Extracted {added_count} new products (total: {len(all_products)})")
                    
                except Exception as e:
                    print(f"    [ERROR] Failed to extract from {sub_name}: {str(e)}")
                    continue
        else:
            print("  [INFO] No subcategories found. Extracting from main page only...")
            # If no subcategories found, just extract from main page
            if not all_products:
                scroll_page(driver, times=25)
                all_products = extract_products(driver)
        
        # Save all products
        print("\n[5/5] Saving all products...")
        if all_products:
            save_data(all_products)
            print(f"\n" + "=" * 60)
            print(f"[SUCCESS] Extracted {len(all_products)} total products!")
            print("=" * 60)
            
            # Check for duplicates
            unique_names = len(set(p['name'] for p in all_products))
            if len(all_products) > unique_names:
                print(f"Note: {len(all_products) - unique_names} duplicate(s) found (same name, different variants)")
            
            # Show breakdown by type (all products are already filtered)
            print("\nProduct breakdown (filtered - only Meat, Fish & Eggs):")
            name_lower = lambda p: (p.get('name', '') or '').lower()
            url_lower = lambda p: (p.get('product_url', '') or '').lower()
            
            chicken_count = sum(1 for p in all_products if 'chicken' in name_lower(p) or 'chicken' in url_lower(p))
            fish_count = sum(1 for p in all_products if any(kw in name_lower(p) or kw in url_lower(p) 
                for kw in ['fish', 'prawn', 'shrimp', 'crab', 'seafood', 'salmon', 'tuna', 'rohu', 'katla', 'pomfret', 'bangda']))
            mutton_count = sum(1 for p in all_products if any(kw in name_lower(p) or kw in url_lower(p) 
                for kw in ['mutton', 'lamb', 'goat']))
            egg_count = sum(1 for p in all_products if 'egg' in name_lower(p) or 'egg' in url_lower(p))
            cold_cuts_count = sum(1 for p in all_products if any(kw in name_lower(p) or kw in url_lower(p) 
                for kw in ['sausage', 'salami', 'ham', 'bacon', 'cold cut', 'cold cuts']))
            
            print(f"  - Chicken: {chicken_count}")
            print(f"  - Fish & Seafood: {fish_count}")
            print(f"  - Mutton/Lamb/Goat: {mutton_count}")
            print(f"  - Eggs: {egg_count}")
            print(f"  - Cold Cuts: {cold_cuts_count}")
            
            # Calculate others (products that might match multiple categories)
            others = len(all_products) - chicken_count - fish_count - mutton_count - egg_count - cold_cuts_count
            if others > 0:
                print(f"  - Others (may overlap with above): {others}")
            else:
                print(f"  - Total: {len(all_products)} products")
            
            print(f"\nTo verify if all products were extracted:")
            print(f"  1. Check the browser - manually count products visible")
            print(f"  2. Compare with the CSV file: {OUTPUT_CSV}")
            print(f"  3. If you see more products in browser, try running again")
        else:
            print("\n[ERROR] No products found!")
            print("Make sure:")
            print("  1. Location is set correctly (560067)")
            print("  2. You're on the Meat, Fish & Eggs page")
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
