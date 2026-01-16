"""
Zepto Scraper - Breakfast & Sauces Category
Extracts all products from the Breakfast & Sauces category with accurate values.
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
# TODO: Replace with the actual Breakfast & Sauces category URL
# You can find this by navigating to the category in your browser and copying the URL
BREAKFAST_SAUCES_URL = "https://www.zepto.com/cn/breakfast-sauces/breakfast-sauces/cid/f804bccc-c565-4879-b6ab-1b964bb1ed41/scid/68922181-4e0e-4a6b-9862-cf1a02ba240e"  # Update this
OUTPUT_CSV = "output/zepto_breakfast_sauces.csv"
OUTPUT_JSON = "output/zepto_breakfast_sauces.json"


def setup_driver():
    """Setup Chrome driver with error suppression."""
    chrome_options = Options()
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option("useAutomationExtension", False)
    chrome_options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    )

    # Suppress console errors and warnings
    chrome_options.add_argument("--log-level=3")  # Only fatal errors
    chrome_options.add_argument("--disable-logging")
    chrome_options.add_experimental_option(
        "excludeSwitches", ["enable-automation", "enable-logging"]
    )

    # Additional stability options
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-extensions")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.execute_script(
        "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
    )

    return driver


def is_valid_product(product):
    """
    Check if product belongs to Breakfast & Sauces categories.
    Returns True if valid, False otherwise.
    """
    name = (product.get("name") or "").lower()
    url = (product.get("product_url") or "").lower()
    combined_text = f"{name} {url}".lower()

    # Keywords that indicate valid products - CHECK THESE FIRST
    valid_keywords = [
        # Breakfast Cereals
        "cereal",
        "corn flakes",
        "chocos",
        "choco flakes",
        "muesli",
        "oat",
        "oats",
        "granola",
        "wheat flakes",
        "bran",
        "breakfast cereal",
        # Muesli & Oats (extra)
        "museli",
        "instant oats",
        "rolled oats",
        "steel cut oats",
        # Honey & Spreads
        "honey",
        "jam",
        "jelly",
        "fruit spread",
        "chocolate spread",
        "hazelnut spread",
        "nutella",
        "choco spread",
        "marmalade",
        # Peanut Butter - MUST CHECK BEFORE "butter" invalid check
        "peanut butter",
        "almond butter",
        "nut butter",
        # Ketchup & Sauces
        "ketchup",
        "tomato ketchup",
        "sauce",
        "sauces",
        "chilli sauce",
        "soy sauce",
        "soya sauce",
        "hot sauce",
        "mustard sauce",
        "pizza sauce",
        "pasta sauce",
        "schezwan",
        "schezuan",
        "dressing",
        "dip",
        "dips",
        "mayonnaise",
        "mayo",
        "salad dressing",
        # Breakfast mixes / batters
        "pancake mix",
        "waffle mix",
        "cake mix",
        "brownie mix",
        "idli mix",
        "dosa mix",
        "batter",
        "batters",
        "ready mix",
        # Tea & Coffee
        "tea",
        "green tea",
        "black tea",
        "chai",
        "ctc tea",
        "coffee",
        "instant coffee",
        "filter coffee",
        "ground coffee",
        "coffee powder",
        # Cafe / beverages powder
        "hot chocolate",
        "cappuccino",
        "latte",
        "mocha",
        "cold coffee",
        # Dates & Seeds (since shown under this menu)
        "dates",
        "seed",
        "seeds",
        "chia seed",
        "sunflower seed",
        "pumpkin seed",
        "flax seed",
    ]

    # Check valid keywords FIRST (especially for peanut butter)
    for valid_kw in valid_keywords:
        if valid_kw in combined_text:
            return True

    # Keywords that indicate invalid products (should be excluded)
    invalid_keywords = [
        # Other main categories
        "chicken",
        "meat",
        "fish",
        "mutton",
        "lamb",
        "goat",
        "prawn",
        "seafood",
        "egg ",
        " eggs",
        "paneer",
        "cheese",
        # Butter - but NOT peanut butter, almond butter, nut butter (already checked above)
        "butter",
        "cream",
        "curd",
        "yogurt",
        "yoghurt",
        "lassi",
        "milk ",
        " milk",
        "bread",
        "bun",
        "buns",
        "bakery",
        "biscuit",
        "biscuits",
        "cake",
        "cakes",
        "pastry",
        "pastries",
        # Atta/Rice/Oil/Dals
        "atta",
        "flour",
        "besan",
        "sooji",
        "rava",
        "rice",
        "dal",
        "pulse",
        "oil",
        "ghee",
        "sunflower oil",
        "groundnut oil",
        # Fruits & Vegetables (fresh)
        "fresh fruit",
        "fresh fruits",
        "fresh vegetable",
        "fresh vegetables",
        # Masala & Dry fruits (whole spices, not seeds for breakfast)
        "whole spice",
        "whole spices",
        "masala",
        "spice",
        "spices",
        "turmeric",
        "cumin",
        "coriander powder",
        "cardamom",
        "dry fruit",
        "dry fruits",
        # Note: almond, cashew, pistachio, walnut excluded UNLESS they're in spreads/butters (already checked)
        # Misc non-breakfast items
        "laundry",
        "detergent",
        "soap",
        "shampoo",
        "toothpaste",
        "cleaner",
        "wipes",
        "tissue",
        "diaper",
        "sanitary",
        "pet food",
        # Text noise
        "incl. of all taxes",
        "buy ",
        "online",
        "combo",
    ]

    # Check invalid keywords (but valid ones already passed above)
    for invalid_kw in invalid_keywords:
        if invalid_kw in combined_text:
            # Special exception: if it's a seed but not a breakfast seed, exclude
            if invalid_kw == "seed" or invalid_kw == "seeds":
                # Already checked for valid seeds above, so this is invalid
                pass
            return False

    # If no valid keywords found, exclude it
    return False


def scroll_page(driver, times=30):
    """Scroll page to load products - stops when no new products found."""
    print("Scrolling to load products...")
    last_count = 0
    no_change_count = 0
    max_no_change = 5  # Stop if no new products for 5 consecutive scrolls (more thorough)

    for i in range(times):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)  # Slightly longer wait for lazy loading

        try:
            current_count = len(
                driver.find_elements(By.XPATH, "//*[contains(text(), '₹')]")
            )
            if current_count > last_count:
                print(
                    f"  Scroll {i+1}/{times} - Found {current_count} price elements (+{current_count - last_count} new)"
                )
                last_count = current_count
                no_change_count = 0
            else:
                no_change_count += 1
                print(
                    f"  Scroll {i+1}/{times} - No new products ({current_count} total)"
                )
                if no_change_count >= max_no_change:
                    print(
                        f"  No new products for {max_no_change} scrolls. Assuming all products loaded."
                    )
                    break
        except Exception:
            print(f"  Scroll {i+1}/{times}")
            no_change_count += 1

    print(f"\n  Final count: {last_count} price elements found")
    driver.execute_script("window.scrollTo(0, 0);")
    time.sleep(2)


def extract_products(driver):
    """Extract products from current page - SIMPLE AND RELIABLE."""
    print("\nExtracting products...")
    products = []

    print("  Waiting for page to fully load...")
    time.sleep(5)

    current_url = driver.current_url
    print(f"  Current URL: {current_url[:80]}...")

    if (
        "breakfast" not in current_url.lower()
        and "sauce" not in current_url.lower()
        and "cereal" not in current_url.lower()
    ):
        print("  [WARNING] Might not be on Breakfast & Sauces page!")

    print("  Finding products by looking for price (₹)...")
    try:
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located(
                    (By.XPATH, "//*[contains(text(), '₹')]")
                )
            )
        except Exception:
            print("  [WARNING] No price elements found yet, continuing anyway...")

        price_elements = driver.find_elements(
            By.XPATH, "//*[contains(text(), '₹')]"
        )
        print(f"  Found {len(price_elements)} elements with ₹ symbol")

        if len(price_elements) == 0:
            print("  [ERROR] No price elements found!")
            print("  Trying to refresh and wait longer...")
            driver.refresh()
            time.sleep(8)
            price_elements = driver.find_elements(
                By.XPATH, "//*[contains(text(), '₹')]"
            )
            print(f"  After refresh: Found {len(price_elements)} elements with ₹")

        if len(price_elements) == 0:
            print("\n[ERROR] No products found on page!")
            return products

        product_containers = {}

        for price_elem in price_elements:
            try:
                try:
                    container = price_elem.find_element(
                        By.XPATH, "./ancestor::a[1]"
                    )
                except Exception:
                    try:
                        container = price_elem.find_element(
                            By.XPATH, "./ancestor::div[position()<=5][1]"
                        )
                    except Exception:
                        container = price_elem

                href = None
                try:
                    href = container.get_attribute("href")
                    if not href:
                        try:
                            a_tag = container.find_element(
                                By.XPATH, ".//a[@href]"
                            )
                            href = a_tag.get_attribute("href") or ""
                        except Exception:
                            pass
                except Exception:
                    pass

                container_text = (container.text or "").strip()[:100]

                if container_text and len(container_text) > 10:
                    text_lower = container_text.lower()
                    if (
                        "explore" not in text_lower
                        and "banner" not in text_lower
                        and "up to" not in text_lower
                    ):
                        if href and "/pn/" in href:
                            try:
                                url_parts = href.split("/pvid/")
                                if len(url_parts) > 1:
                                    product_id = (
                                        url_parts[1].split("/")[0].split("?")[0]
                                    )
                                    key = product_id
                                else:
                                    url_slug = (
                                        href.split("/pn/")[1].split("/")[0]
                                        if "/pn/" in href
                                        else ""
                                    )
                                    price_match = re.search(
                                        r"₹\s*(\d+)", container_text
                                    )
                                    key = f"{url_slug}|{price_match.group(1) if price_match else 'no_price'}"
                            except Exception:
                                price_match = re.search(
                                    r"₹\s*(\d+)", container_text
                                )
                                key = (
                                    f"{container_text.split('\n')[0][:30]}|"
                                    f"{price_match.group(1) if price_match else 'no_price'}"
                                )
                        else:
                            price_match = re.search(
                                r"₹\s*(\d+)", container_text
                            )
                            if price_match:
                                key = (
                                    container_text.split("\n")[0]
                                    + "|"
                                    + price_match.group(1)
                                )
                            else:
                                key = container_text[:50]

                        if key not in product_containers:
                            product_containers[key] = container
            except Exception:
                continue

        product_list = list(product_containers.values())
        print(f"  Found {len(product_list)} unique product containers")

        if len(product_list) == 0:
            print("\n[ERROR] Could not extract product containers!")
            return products

        print(f"\n  Extracting data from {len(product_list)} products...")
        for container in product_list:
            try:
                product = {}
                container_text = (container.text or "").strip()
                lines = [
                    l.strip() for l in container_text.split("\n") if l.strip()
                ]

                href = None
                try:
                    href = container.get_attribute("href")
                    if not href:
                        try:
                            a_tag = container.find_element(By.TAG_NAME, "a")
                            href = a_tag.get_attribute("href") or ""
                        except Exception:
                            try:
                                a_tag = container.find_element(
                                    By.XPATH, ".//a[@href]"
                                )
                                href = a_tag.get_attribute("href") or ""
                            except Exception:
                                pass
                except Exception:
                    pass

                product_name = None
                if href and "/pn/" in href:
                    try:
                        url_parts = href.split("/pn/")
                        if len(url_parts) > 1:
                            product_slug = url_parts[1].split("/")[0]
                            name_parts = product_slug.split("-")
                            product_name = " ".join(
                                word.capitalize() for word in name_parts
                            )
                    except Exception:
                        pass

                if not product_name:
                    try:
                        name_selectors = [
                            "h1",
                            "h2",
                            "h3",
                            "h4",
                            "span[class*='name']",
                            "span[class*='title']",
                            "div[class*='name']",
                            "div[class*='title']",
                            "p[class*='name']",
                            "div[class*='product']",
                        ]
                        for selector in name_selectors:
                            try:
                                name_elem = container.find_element(
                                    By.CSS_SELECTOR, selector
                                )
                                name_text = (name_elem.text or "").strip()
                                if name_text and len(name_text) > 3:
                                    name_upper = name_text.upper()
                                    if name_upper not in [
                                        "ADD",
                                        "NOTIFY",
                                        "EXPLORE",
                                        "EXPLORE NOW",
                                        "BUY NOW",
                                    ] and not re.match(
                                        r"^₹\s*\d+", name_text
                                    ):
                                        product_name = name_text
                                        break
                            except Exception:
                                continue
                    except Exception:
                        pass

                if not product_name:
                    for line in lines:
                        line_clean = line.strip()
                        if line_clean.upper() in [
                            "ADD",
                            "NOTIFY",
                            "EXPLORE",
                            "EXPLORE NOW",
                            "BUY NOW",
                        ]:
                            continue
                        if re.match(r"^₹\s*\d+", line_clean):
                            continue
                        if re.match(
                            r"^₹\s*\d+\s*OFF", line_clean, re.IGNORECASE
                        ):
                            continue
                        if "mins" in line_clean.lower() or "min" in line_clean.lower():
                            continue
                        if re.match(
                            r"^\d+\s*(pack|g|kg|ml|l|pc|pcs|Approx)",
                            line_clean,
                            re.IGNORECASE,
                        ):
                            continue
                        if "price list" in line_clean.lower():
                            continue
                        if re.match(
                            r"^\d+[\s-]+\d+\s*(g|kg)", line_clean, re.IGNORECASE
                        ):
                            continue
                        if len(line_clean) > 3 and not line_clean.isdigit():
                            product_name = line_clean
                            break

                product["name"] = product_name if product_name else "Unknown"

                price_match = re.search(r"₹\s*(\d+)", container_text)
                product["price"] = price_match.group(1) if price_match else "N/A"

                discount_match = re.search(
                    r"₹\s*(\d+)\s*OFF", container_text, re.IGNORECASE
                )
                product["discount"] = (
                    f"₹{discount_match.group(1)}" if discount_match else "N/A"
                )

                qty_match = re.search(
                    r"(\d+\s*(?:pack|g|kg|pc|pcs|ml|l|Approx\.))",
                    container_text,
                    re.IGNORECASE,
                )
                product["quantity"] = qty_match.group(1) if qty_match else "N/A"

                product["product_url"] = href if href else "N/A"

                try:
                    img = container.find_element(By.TAG_NAME, "img")
                    product["image_url"] = (
                        img.get_attribute("src")
                        or img.get_attribute("data-src")
                        or "N/A"
                    )
                except Exception:
                    product["image_url"] = "N/A"

                if product.get("name") and product["name"] != "Unknown":
                    name_upper = product["name"].upper()
                    if name_upper not in ["ADD", "NOTIFY", "EXPLORE", "BUY NOW"]:
                        if is_valid_product(product):
                            product["scraped_at"] = datetime.now().strftime(
                                "%Y-%m-%d %H:%M:%S"
                            )
                            products.append(product)
                            price_display = (
                                f"₹{product['price']}"
                                if product["price"] != "N/A"
                                else "N/A"
                            )
                            print(
                                f"  [{len(products)}] {product['name'][:50]:<50} | {price_display}"
                            )
            except Exception:
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

    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "name",
                "price",
                "discount",
                "quantity",
                "image_url",
                "product_url",
                "scraped_at",
            ],
        )
        writer.writeheader()
        writer.writerows(products)

    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(products, f, indent=2, ensure_ascii=False)

    print(f"\nSaved {len(products)} products to:")
    print(f"  - {OUTPUT_CSV}")
    print(f"  - {OUTPUT_JSON}")


def find_subcategories(driver):
    """Find subcategory links (Breakfast Cereals, Ketchup & Sauces, Muesli & Oats, etc.) on the category page."""
    subcategory_urls = []
    subcategory_names = []

    print(
        "\n  Looking for subcategories (Breakfast Cereals, Ketchup & Sauces, Muesli & Oats, Honey & Spreads, Peanut Butter, Batter & Mixes, Tea & Coffee, Zepto Cafe, Dates & Seeds)..."
    )

    subcategory_keywords = [
        "breakfast cereal",
        "cereal",
        "cereals",
        "muesli",
        "oats",
        "ketchup",
        "sauce",
        "sauces",
        "honey",
        "spread",
        "spreads",
        "peanut butter",
        "peanut-butter",
        "peanutbutter",
        "butter",
        "batter",
        "batters",
        "breakfast mix",
        "tea",
        "coffee",
        "zepto cafe",
        "zepto-cafe",
        "cafe",
        "dates",
        "seeds",
    ]

    excluded_keywords = [
        "meat",
        "fish",
        "egg",
        "eggs",
        "chicken",
        "mutton",
        "rice",
        "atta",
        "oil",
        "dal",
        "pulse",
        "vegetable",
        "fruit",
        "milk",
        "bread",
        "bakery",
        # Note: "butter" is NOT excluded here because "peanut butter" is valid
    ]

    try:
        all_links = driver.find_elements(By.TAG_NAME, "a")

        for link in all_links:
            try:
                href = link.get_attribute("href") or ""
                text = (link.text or "").strip().lower()

                if href and "zepto.com" in href:
                    url_lower = href.lower()
                    text_lower = text.lower()
                    
                    # Check if it's a valid breakfast/sauces subcategory
                    is_subcategory = False
                    
                    # First, check for valid subcategory keywords
                    if any(keyword in url_lower or keyword in text_lower for keyword in subcategory_keywords):
                        # Special handling: "peanut butter" should not be excluded even if "butter" is in excluded list
                        is_peanut_butter = "peanut butter" in text_lower or "peanut butter" in url_lower or "peanut-butter" in url_lower
                        
                        # Check excluded keywords (but allow exceptions)
                        should_exclude = False
                        for excluded_kw in excluded_keywords:
                            if excluded_kw in text_lower or excluded_kw in url_lower:
                                # Exception: if it's peanut butter, don't exclude
                                if is_peanut_butter and excluded_kw == "butter":
                                    continue
                                should_exclude = True
                                break
                        
                        if should_exclude:
                            continue
                        
                        # If text or URL matches subcategory keywords, it's valid
                        if any(keyword in text_lower for keyword in subcategory_keywords):
                            is_subcategory = True
                        elif "/cn/" in href and "/pn/" not in href:
                            # Category URL (not product) - check if it's breakfast/sauces related
                            if any(kw in url_lower for kw in ["breakfast", "sauce", "cereal", "muesli", "oats", "ketchup", "honey", "spread", "peanut", "batter", "tea", "coffee", "cafe", "dates", "seeds"]):
                                is_subcategory = True

                        if is_subcategory and href not in subcategory_urls:
                            subcategory_urls.append(href)
                            subcategory_names.append(
                                link.text.strip() or href.split("/")[-1]
                            )
                            print(
                                f"    Found subcategory: {link.text.strip()[:50] if link.text.strip() else href[:50]}"
                            )
            except Exception:
                continue

        try:
            for keyword in [
                "Breakfast Cereals",
                "Cereals",
                "Muesli & Oats",
                "Muesli",
                "Oats",
                "Ketchup & Sauces",
                "Sauces",
                "Honey & Spreads",
                "Honey",
                "Spreads",
                "Peanut Butter",
                "Batter & Mixes",
                "Batters & Mixes",
                "Tea & Coffee",
                "Tea",
                "Coffee",
                "Zepto Cafe",
                "Dates & Seeds",
                "Dates",
                "Seeds",
            ]:
                if keyword.lower() in [kw.lower() for kw in excluded_keywords]:
                    continue
                try:
                    xpath = (
                        "//a[contains(translate(text(), "
                        "'ABCDEFGHIJKLMNOPQRSTUVWXYZ', "
                        "'abcdefghijklmnopqrstuvwxyz'), "
                        f"'{keyword.lower()}')]"
                    )
                    elements = driver.find_elements(By.XPATH, xpath)
                    for elem in elements:
                        try:
                            href = elem.get_attribute("href") or ""
                            if (
                                href
                                and "zepto.com" in href
                                and "/cn/" in href
                                and "/pn/" not in href
                            ):
                                if href not in subcategory_urls:
                                    subcategory_urls.append(href)
                                    subcategory_names.append(
                                        elem.text.strip() or keyword
                                    )
                                    print(
                                        f"    Found subcategory via text search: {elem.text.strip()[:50] if elem.text.strip() else keyword}"
                                    )
                        except Exception:
                            continue
                except Exception:
                    continue
        except Exception:
            pass

        current_url = driver.current_url
        if "breakfast" in current_url.lower() or "sauce" in current_url.lower():
            base_url = current_url.split("/cn/")[0] + "/cn/"
            potential_subcategories = [
                ("breakfast-cereals", "breakfast cereals"),
                ("breakfast-cereal", "breakfast cereal"),
                ("cereals", "cereals"),
                ("cereal", "cereal"),
                ("muesli-oats", "muesli & oats"),
                ("muesli", "muesli"),
                ("oats", "oats"),
                ("ketchup-sauces", "ketchup & sauces"),
                ("ketchup-sauce", "ketchup & sauce"),
                ("sauces", "sauces"),
                ("sauce", "sauce"),
                ("honey-spreads", "honey & spreads"),
                ("honey-spread", "honey & spread"),
                ("honey", "honey"),
                ("spreads", "spreads"),
                ("spread", "spread"),
                ("peanut-butter", "peanut butter"),
                ("peanutbutter", "peanut butter"),
                ("batters-mixes", "batter & mixes"),
                ("batter-mixes", "batter & mixes"),
                ("batters", "batters"),
                ("batter", "batter"),
                ("tea-coffee", "tea & coffee"),
                ("tea", "tea"),
                ("coffee", "coffee"),
                ("zepto-cafe", "zepto cafe"),
                ("cafe", "cafe"),
                ("dates-seeds", "dates & seeds"),
                ("dates", "dates"),
                ("seeds", "seeds"),
            ]

            for sub_path, sub_name in potential_subcategories:
                try:
                    test_url = base_url + sub_path
                    if not any(test_url in url for url in subcategory_urls):
                        test_links = driver.find_elements(
                            By.XPATH, f"//a[contains(@href, '{sub_path}')]"
                        )
                        if test_links:
                            for link in test_links:
                                href = link.get_attribute("href") or ""
                                if (
                                    href
                                    and "/cn/" in href
                                    and "/pn/" not in href
                                    and href not in subcategory_urls
                                ):
                                    subcategory_urls.append(href)
                                    subcategory_names.append(sub_name.capitalize())
                                    print(
                                        f"    Found subcategory via URL pattern: {sub_name.capitalize()}"
                                    )
                                    break
                except Exception:
                    continue

    except Exception as e:
        print(f"    [WARNING] Error finding subcategories: {str(e)}")

    seen = set()
    unique_urls = []
    unique_names = []
    for url, name in zip(subcategory_urls, subcategory_names):
        if url not in seen:
            seen.add(url)
            unique_urls.append(url)
            unique_names.append(name)

    return unique_urls, unique_names


def main():
    """Main function."""
    driver = None

    try:
        print("=" * 60)
        print("Zepto Scraper - Breakfast & Sauces Category")
        print("=" * 60)

        if "..." in BREAKFAST_SAUCES_URL:
            print("\n[IMPORTANT] Category URL not configured!")
            print(
                "Please update BREAKFAST_SAUCES_URL in the script with the actual category URL."
            )
            print("\nTo find the URL:")
            print("  1. Open Zepto in your browser")
            print("  2. Navigate to 'Breakfast & Sauces' category")
            print("  3. Copy the full URL from the address bar")
            print("  4. Update BREAKFAST_SAUCES_URL in this script")
            print("\nOr you can provide it now:")
            user_url = input(
                "Enter the Breakfast & Sauces category URL (or press Enter to exit): "
            ).strip()
            if not user_url:
                print("Exiting...")
                return
            category_url = user_url
        else:
            category_url = BREAKFAST_SAUCES_URL

        print("\n[1/5] Setting up browser...")
        driver = setup_driver()
        print("  [OK] Browser ready")

        print("\n[2/5] Opening Zepto homepage...")
        driver.get("https://www.zepto.com")
        time.sleep(3)
        print("  [OK] Homepage loaded")

        print("\n" + "=" * 60)
        print("IMPORTANT: Set location manually in the browser")
        print("=" * 60)
        print("\nPlease set the location manually:")
        print("1. Look for location button/display in the header")
        print("2. Click on it to open location modal")
        print("3. Enter PIN code: 560067 (or your preferred location)")
        print("4. Click Apply/Confirm")
        print("\nAfter setting location, press Enter here to continue...")
        input("Press Enter after location is set...")
        print("\n[OK] Continuing with scraping...")

        print("\n[3/5] Navigating to Breakfast & Sauces category...")
        driver.get(category_url)
        print("  Waiting for page to load...")
        time.sleep(8)

        print("\n[4/5] Finding subcategories...")
        subcategory_urls, subcategory_names = find_subcategories(driver)

        all_products = []
        all_product_urls = set()

        print("\n  Extracting from main category page...")
        try:
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located(
                    (By.XPATH, "//*[contains(text(), '₹')]")
                )
            )
            scroll_page(driver, times=30)
            main_products = extract_products(driver)
            for product in main_products:
                if (
                    product.get("product_url")
                    and product["product_url"] not in all_product_urls
                ):
                    all_products.append(product)
                    all_product_urls.add(product["product_url"])
            print(f"  Extracted {len(main_products)} products from main page")
        except Exception:
            print(
                "  [WARNING] Could not extract from main page, continuing with subcategories..."
            )

        if subcategory_urls:
            print(
                f"\n  Found {len(subcategory_urls)} subcategories. Extracting from each..."
            )
            for idx, (sub_url, sub_name) in enumerate(
                zip(subcategory_urls, subcategory_names), 1
            ):
                try:
                    print(
                        f"\n  [{idx}/{len(subcategory_urls)}] Extracting from: {sub_name[:50]}"
                    )
                    driver.get(sub_url)
                    time.sleep(5)

                    try:
                        WebDriverWait(driver, 15).until(
                            EC.presence_of_element_located(
                                (By.XPATH, "//*[contains(text(), '₹')]")
                            )
                        )
                    except Exception:
                        print("    [WARNING] No products found, skipping...")
                        continue

                    scroll_page(driver, times=30)
                    sub_products = extract_products(driver)

                    added_count = 0
                    for product in sub_products:
                        if (
                            product.get("product_url")
                            and product["product_url"] not in all_product_urls
                        ):
                            all_products.append(product)
                            all_product_urls.add(product["product_url"])
                            added_count += 1

                    print(
                        f"    Extracted {added_count} new products (total: {len(all_products)})"
                    )
                except Exception as e:
                    print(
                        f"    [ERROR] Failed to extract from {sub_name}: {str(e)}"
                    )
                    continue
        else:
            print(
                "  [INFO] No subcategories found. Extracting from main page only..."
            )
            if not all_products:
                scroll_page(driver, times=30)
                all_products = extract_products(driver)

        print("\n[5/5] Saving all products...")
        if all_products:
            # Final duplicate removal by name+price (in case some don't have URLs)
            seen_products = set()
            unique_products = []
            for product in all_products:
                # Use URL as primary key, fallback to name+price
                if product.get("product_url") and product["product_url"] != "N/A":
                    key = product["product_url"]
                else:
                    key = f"{product.get('name', '')}|{product.get('price', '')}"
                
                if key not in seen_products:
                    seen_products.add(key)
                    unique_products.append(product)
            
            if len(unique_products) < len(all_products):
                print(f"  Removed {len(all_products) - len(unique_products)} duplicate(s) before saving")
                all_products = unique_products
            
            save_data(all_products)
            print("\n" + "=" * 60)
            print(f"[SUCCESS] Extracted {len(all_products)} total products!")
            print("=" * 60)

            name_lower = lambda p: (p.get("name", "") or "").lower()
            url_lower = lambda p: (p.get("product_url", "") or "").lower()

            cereals_count = sum(
                1
                for p in all_products
                if any(
                    kw in name_lower(p) or kw in url_lower(p)
                    for kw in ["cereal", "muesli", "oats", "granola", "flakes"]
                )
            )
            sauces_count = sum(
                1
                for p in all_products
                if any(
                    kw in name_lower(p) or kw in url_lower(p)
                    for kw in ["ketchup", "sauce", "schezwan", "dip", "mayonnaise"]
                )
            )
            honey_spreads_count = sum(
                1
                for p in all_products
                if any(
                    kw in name_lower(p) or kw in url_lower(p)
                    for kw in ["honey", "jam", "spread", "marmalade", "nutella"]
                )
            )
            peanut_butter_count = sum(
                1
                for p in all_products
                if "peanut butter" in name_lower(p) or "peanut-butter" in url_lower(p)
            )
            mixes_count = sum(
                1
                for p in all_products
                if any(
                    kw in name_lower(p) or kw in url_lower(p)
                    for kw in ["batter", "mix", "pancake", "waffle"]
                )
            )
            tea_coffee_count = sum(
                1
                for p in all_products
                if any(
                    kw in name_lower(p) or kw in url_lower(p)
                    for kw in ["tea", "coffee", "hot chocolate"]
                )
            )

            print(
                "\nProduct breakdown (filtered - only Breakfast & Sauces related items):"
            )
            print(f"  - Breakfast Cereals / Muesli / Oats: {cereals_count}")
            print(f"  - Ketchup & Sauces / Dips: {sauces_count}")
            print(f"  - Honey & Spreads: {honey_spreads_count}")
            print(f"  - Peanut Butter: {peanut_butter_count}")
            print(f"  - Batters & Mixes: {mixes_count}")
            print(f"  - Tea & Coffee: {tea_coffee_count}")

            others = (
                len(all_products)
                - cereals_count
                - sauces_count
                - honey_spreads_count
                - peanut_butter_count
                - mixes_count
                - tea_coffee_count
            )
            if others > 0:
                print(f"  - Others (may overlap with above): {others}")
            else:
                print(f"  - Total: {len(all_products)} products")

        else:
            print("\n[ERROR] No products found!")
            print("Make sure:")
            print("  1. Location is set correctly (560067)")
            print("  2. You're on the Breakfast & Sauces page")
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

