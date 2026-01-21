"""
Zepto Scraper - Cold Drinks & Juices Category
Extracts all products from the Cold Drinks & Juices category with accurate values.
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
# TODO: Replace with the actual Cold Drinks & Juices category URL
# You can find this by navigating to the category in your browser and copying the URL
COLD_DRINKS_JUICES_URL = "https://www.zepto.com/cn/cold-drinks-juices/cold-drinks-juices/cid/947a72ae-b371-45cb-ad3a-778c05b64399/scid/7dceec53-78f9-4f06-83d7-c8edd9c2f71a"  # Update this
OUTPUT_CSV = "output/zepto_cold_drinks_juices.csv"
OUTPUT_JSON = "output/zepto_cold_drinks_juices.json"


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
    Check if product belongs to Cold Drinks & Juices categories.
    Returns True if valid, False otherwise.
    """
    name = (product.get("name") or "").lower()
    url = (product.get("product_url") or "").lower()
    combined_text = f"{name} {url}".lower()

    # Keywords that indicate valid products - CHECK THESE FIRST
    valid_keywords = [
        # Soft Drinks
        "soft drink",
        "soft drinks",
        "cola",
        "cola",
        "pepsi",
        "coca cola",
        "coca-cola",
        "coke",
        "sprite",
        "fanta",
        "7up",
        "thums up",
        "limca",
        "mirinda",
        "soda",
        "sodas",
        # Soda & Mixers
        "tonic water",
        "tonic",
        "soda water",
        "club soda",
        "ginger ale",
        "ginger beer",
        "mixer",
        "mixers",
        "schweppes",
        # Fruit Juices & Drinks
        "fruit juice",
        "fruit juices",
        "juice",
        "juices",
        "orange juice",
        "apple juice",
        "mango juice",
        "pineapple juice",
        "cranberry juice",
        "grape juice",
        "pomegranate juice",
        "guava juice",
        "fruit drink",
        "fruit drinks",
        "nectar",
        "nectars",
        "real",
        "tropicana",
        "minute maid",
        # Cold Coffee & Ice
        "cold coffee",
        "iced coffee",
        "ice coffee",
        "coffee drink",
        "coffee drinks",
        "frappe",
        "frappes",
        "iced tea",
        "ice tea",
        "cold tea",
        # Energy Drink
        "energy drink",
        "energy drinks",
        "red bull",
        "monster",
        "powerade",
        "gatorade",
        "electral",
        # Non-Alcoholic
        "non-alcoholic",
        "non alcoholic",
        "mocktail",
        "mocktails",
        "virgin",
        "bira",
        # Water
        "water",
        "mineral water",
        "drinking water",
        "bisleri",
        "aquafina",
        "kinley",
        "himalayan",
        # Premium
        "premium",
        # Hydration
        "hydration",
        "sports drink",
        "sports drinks",
        "electrolyte",
        "electrolytes",
        "coconut water",
        # Milk Drinks
        "milk drink",
        "milk drinks",
        "flavored milk",
        "flavoured milk",
        "lassi",
        "buttermilk",
        "chaas",
        "milkshake",
        "milkshakes",
        # Vegan Drinks
        "vegan drink",
        "vegan drinks",
        "almond milk",
        "soy milk",
        "soya milk",
        "oat milk",
        "coconut milk",
        "rice milk",
        "plant milk",
        "plant-based milk",
        "so good",
        # Instant Drink Mixes
        "instant drink mix",
        "instant drink mixes",
        "drink mix",
        "drink mixes",
        "tang",
        "rasna",
        "lemonade mix",
        "orange mix",
        "instant mix",
        # Kombucha
        "kombucha",
        "kombuchas",
        # Zepto Cafe
        "zepto cafe",
        "zepto-cafe",
        "cafe",
    ]

    # Check valid keywords FIRST
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
        "butter",
        "cream",
        "curd",
        "yogurt",
        "yoghurt",
        # Fresh milk (not drinks)
        "milk ",
        " milk",
        "fresh milk",
        "toned milk",
        "full cream milk",
        # Bread & Bakery
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
        # Masala & Spices
        "masala",
        "spice",
        "spices",
        "turmeric",
        "cumin",
        "coriander",
        "cardamom",
        # Breakfast items (cereals, oats, etc.)
        "cereal",
        "corn flakes",
        "chocos",
        "muesli",
        "oats",
        "granola",
        # Sauces & Spreads
        "ketchup",
        "sauce",
        "honey",
        "jam",
        "jelly",
        "spread",
        "peanut butter",
        "mayonnaise",
        "mayo",
        # Packaged Food items
        "noodle",
        "noodles",
        "pasta",
        "soup",
        "soups",
        "pickle",
        "pickles",
        "papad",
        "papads",
        "achaar",
        "chutney",
        "chutneys",
        "ready to cook",
        "ready-to-cook",
        "ready to eat",
        "ready-to-eat",
        "baby food",
        "infant food",
        # Tea & Coffee (hot, not cold drinks)
        "tea",
        "coffee",
        "green tea",
        "black tea",
        "chai",
        "instant coffee",
        "coffee powder",
        # Frozen Foods
        "frozen",
        "ice cream",
        "icecream",
        "ice-cream",
        "kulfi",
        # Sweet Cravings
        "chocolate",
        "chocolates",
        "candy",
        "candies",
        "mithai",
        # Misc non-food items
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
            # Special exceptions
            # "coffee" is invalid for hot coffee, but "cold coffee" or "iced coffee" is valid (already checked)
            # "tea" is invalid for hot tea, but "iced tea" or "cold tea" is valid (already checked)
            # "milk" is invalid for fresh milk, but "milk drink" or "flavored milk" is valid (already checked)
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
        "drink" not in current_url.lower()
        and "juice" not in current_url.lower()
        and "beverage" not in current_url.lower()
    ):
        print("  [WARNING] Might not be on Cold Drinks & Juices page!")

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
    """Find subcategory links (Soft Drinks, Fruit Juices, Energy Drinks, etc.) on the category page."""
    subcategory_urls = []
    subcategory_names = []

    print(
        "\n  Looking for subcategories (Top Picks, Soft Drinks, Soda & Mixers, Fruit Juices & Drinks, Cold Coffee & Ice, Energy Drink, Non-Alcoholic, Water, Premium, Hydration, Milk Drinks, Vegan Drinks, Instant Drink Mixes, Kombucha, Zepto Cafe)..."
    )

    subcategory_keywords = [
        "top picks",
        "soft drink",
        "soft drinks",
        "soda",
        "mixer",
        "mixers",
        "fruit juice",
        "fruit juices",
        "juice",
        "juices",
        "cold coffee",
        "iced coffee",
        "ice coffee",
        "energy drink",
        "energy drinks",
        "non-alcoholic",
        "non alcoholic",
        "water",
        "premium",
        "hydration",
        "milk drink",
        "milk drinks",
        "vegan drink",
        "vegan drinks",
        "instant drink mix",
        "instant drink mixes",
        "drink mix",
        "drink mixes",
        "kombucha",
        "zepto cafe",
        "zepto-cafe",
        "cafe",
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
        "bread",
        "bakery",
        "biscuit",
        "biscuits",
        "tea",
        "coffee",
        "cereal",
        "oats",
        "muesli",
        "sauce",
        "ketchup",
        "honey",
        "spread",
        "frozen",
        "ice cream",
        "icecream",
        "chocolate",
        "candy",
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

                    # Check if it's a valid cold drinks/juices subcategory
                    is_subcategory = False

                    # First, check for valid subcategory keywords
                    if any(keyword in url_lower or keyword in text_lower for keyword in subcategory_keywords):
                        # Check excluded keywords (but allow exceptions)
                        should_exclude = False
                        for excluded_kw in excluded_keywords:
                            if excluded_kw in text_lower or excluded_kw in url_lower:
                                # Exception: "coffee" is excluded for hot coffee, but "cold coffee" is valid
                                if "cold coffee" in text_lower or "iced coffee" in text_lower or "cold coffee" in url_lower or "iced coffee" in url_lower:
                                    if excluded_kw == "coffee":
                                        continue
                                should_exclude = True
                                break

                        if should_exclude:
                            continue

                        # If text or URL matches subcategory keywords, it's valid
                        if any(keyword in text_lower for keyword in subcategory_keywords):
                            is_subcategory = True
                        elif "/cn/" in href and "/pn/" not in href:
                            # Category URL (not product) - check if it's cold drinks/juices related
                            if any(kw in url_lower for kw in ["drink", "juice", "beverage", "soda", "cola", "energy", "water", "hydration", "milk", "vegan", "kombucha", "cafe"]):
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
                "Top Picks",
                "Soft Drinks",
                "Soft Drink",
                "Soda & Mixers",
                "Soda Mixers",
                "Fruit Juices & Drinks",
                "Fruit Juices",
                "Fruit Juice",
                "Juices",
                "Juice",
                "Cold Coffee & Ice",
                "Cold Coffee",
                "Iced Coffee",
                "Energy Drink",
                "Energy Drinks",
                "Non-Alcoholic",
                "Non Alcoholic",
                "Water",
                "Premium",
                "Hydration",
                "Milk Drinks",
                "Milk Drink",
                "Vegan Drinks",
                "Vegan Drink",
                "Instant Drink Mixes",
                "Instant Drink Mix",
                "Drink Mixes",
                "Drink Mix",
                "Kombucha",
                "Zepto Cafe",
                "Zepto-Cafe",
                "Cafe",
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
        if "drink" in current_url.lower() or "juice" in current_url.lower() or "beverage" in current_url.lower():
            base_url = current_url.split("/cn/")[0] + "/cn/"
            potential_subcategories = [
                ("top-picks", "top picks"),
                ("soft-drinks", "soft drinks"),
                ("soft-drink", "soft drink"),
                ("soda-mixers", "soda & mixers"),
                ("soda", "soda"),
                ("fruit-juices-drinks", "fruit juices & drinks"),
                ("fruit-juices", "fruit juices"),
                ("fruit-juice", "fruit juice"),
                ("juices", "juices"),
                ("juice", "juice"),
                ("cold-coffee-ice", "cold coffee & ice"),
                ("cold-coffee", "cold coffee"),
                ("iced-coffee", "iced coffee"),
                ("energy-drink", "energy drink"),
                ("energy-drinks", "energy drinks"),
                ("non-alcoholic", "non-alcoholic"),
                ("non-alcoholic", "non alcoholic"),
                ("water", "water"),
                ("premium", "premium"),
                ("hydration", "hydration"),
                ("milk-drinks", "milk drinks"),
                ("milk-drink", "milk drink"),
                ("vegan-drinks", "vegan drinks"),
                ("vegan-drink", "vegan drink"),
                ("instant-drink-mixes", "instant drink mixes"),
                ("instant-drink-mix", "instant drink mix"),
                ("drink-mixes", "drink mixes"),
                ("drink-mix", "drink mix"),
                ("kombucha", "kombucha"),
                ("zepto-cafe", "zepto cafe"),
                ("cafe", "cafe"),
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
        print("Zepto Scraper - Cold Drinks & Juices Category")
        print("=" * 60)

        if "..." in COLD_DRINKS_JUICES_URL:
            print("\n[IMPORTANT] Category URL not configured!")
            print(
                "Please update COLD_DRINKS_JUICES_URL in the script with the actual category URL."
            )
            print("\nTo find the URL:")
            print("  1. Open Zepto in your browser")
            print("  2. Navigate to 'Cold Drinks & Juices' category")
            print("  3. Copy the full URL from the address bar")
            print("  4. Update COLD_DRINKS_JUICES_URL in this script")
            print("\nOr you can provide it now:")
            user_url = input(
                "Enter the Cold Drinks & Juices category URL (or press Enter to exit): "
            ).strip()
            if not user_url:
                print("Exiting...")
                return
            category_url = user_url
        else:
            category_url = COLD_DRINKS_JUICES_URL

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

        print("\n[3/5] Navigating to Cold Drinks & Juices category...")
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

            soft_drinks_count = sum(
                1
                for p in all_products
                if any(
                    kw in name_lower(p) or kw in url_lower(p)
                    for kw in ["soft drink", "cola", "pepsi", "coca cola", "coke", "sprite", "fanta", "soda"]
                )
            )
            juices_count = sum(
                1
                for p in all_products
                if any(
                    kw in name_lower(p) or kw in url_lower(p)
                    for kw in ["juice", "juices", "fruit juice", "nectar"]
                )
            )
            cold_coffee_count = sum(
                1
                for p in all_products
                if any(
                    kw in name_lower(p) or kw in url_lower(p)
                    for kw in ["cold coffee", "iced coffee", "frappe"]
                )
            )
            energy_drinks_count = sum(
                1
                for p in all_products
                if any(
                    kw in name_lower(p) or kw in url_lower(p)
                    for kw in ["energy drink", "red bull", "monster", "gatorade", "powerade"]
                )
            )
            water_count = sum(
                1
                for p in all_products
                if "water" in name_lower(p) or "water" in url_lower(p)
            )
            milk_drinks_count = sum(
                1
                for p in all_products
                if any(
                    kw in name_lower(p) or kw in url_lower(p)
                    for kw in ["milk drink", "flavored milk", "lassi", "buttermilk", "milkshake"]
                )
            )
            vegan_drinks_count = sum(
                1
                for p in all_products
                if any(
                    kw in name_lower(p) or kw in url_lower(p)
                    for kw in ["vegan drink", "almond milk", "soy milk", "oat milk", "coconut milk", "plant milk"]
                )
            )
            instant_mixes_count = sum(
                1
                for p in all_products
                if any(
                    kw in name_lower(p) or kw in url_lower(p)
                    for kw in ["drink mix", "instant mix", "tang", "rasna"]
                )
            )

            print(
                "\nProduct breakdown (filtered - only Cold Drinks & Juices related items):"
            )
            print(f"  - Soft Drinks: {soft_drinks_count}")
            print(f"  - Fruit Juices & Drinks: {juices_count}")
            print(f"  - Cold Coffee & Ice: {cold_coffee_count}")
            print(f"  - Energy Drinks: {energy_drinks_count}")
            print(f"  - Water: {water_count}")
            print(f"  - Milk Drinks: {milk_drinks_count}")
            print(f"  - Vegan Drinks: {vegan_drinks_count}")
            print(f"  - Instant Drink Mixes: {instant_mixes_count}")

            others = (
                len(all_products)
                - soft_drinks_count
                - juices_count
                - cold_coffee_count
                - energy_drinks_count
                - water_count
                - milk_drinks_count
                - vegan_drinks_count
                - instant_mixes_count
            )
            if others > 0:
                print(f"  - Others (may overlap with above): {others}")
            else:
                print(f"  - Total: {len(all_products)} products")

        else:
            print("\n[ERROR] No products found!")
            print("Make sure:")
            print("  1. Location is set correctly (560067)")
            print("  2. You're on the Cold Drinks & Juices page")
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
