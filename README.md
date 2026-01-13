# Zepto Web Scraper - Whitefield, Bangalore

A beginner-friendly Selenium-based web scraper for extracting product data from Zepto, specifically configured for **Whitefield, Bangalore (PIN: 560067)**.

## 📋 Overview

This scraper is designed for educational and MVP purposes. It extracts product information from Zepto's website, handling JavaScript rendering, lazy loading, and location-based product availability.

### What It Does

1. **Launches Chrome browser** (visible by default for debugging)
2. **Opens Zepto homepage** and sets delivery location to Whitefield (560067)
3. **Navigates to product pages** (category or search results)
4. **Scrolls to load products** (handles infinite scroll/lazy loading)
5. **Extracts product data**:
   - Product Name
   - Price
   - Discount (if available)
   - Quantity/Size
   - Product Image URL
   - Product Page URL
6. **Saves data** to CSV and JSON files

## 🚀 Quick Start

### Prerequisites

- Python 3.7 or higher
- Google Chrome browser installed
- Internet connection

### Installation

1. **Clone or download this repository**

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

   This will install:
   - `selenium` - Web browser automation
   - `webdriver-manager` - Automatic ChromeDriver management

### Running the Scraper

1. **Basic usage:**
   ```bash
   python scraper.py
   ```

2. **The scraper will:**
   - Open Chrome browser automatically
   - Navigate to Zepto homepage
   - Attempt to set location to Whitefield (560067)
   - Wait for you to navigate to a category or search page (if needed)
   - Extract products and save to `output/zepto_whitefield_products.csv`

3. **Output files:**
   - `output/zepto_whitefield_products.csv` - Product data in CSV format
   - `output/zepto_whitefield_products.json` - Product data in JSON format

## 📖 End-to-End Scraping Flow

Here's what happens step-by-step when you run the scraper:

### Step 1: Browser Setup
- Chrome browser launches with optimized settings
- User-Agent is set to mimic a real browser
- Automation detection flags are disabled

### Step 2: Navigate to Zepto
- Opens `https://www.zepto.com`
- Waits for page to fully load (handles JavaScript rendering)

### Step 3: Set Location
- **Detects location modal** (if present)
- **Searches for PIN code input field** using multiple selector strategies
- **Enters PIN code 560067** (Whitefield, Bangalore)
- **Submits location** and waits for confirmation
- **Verifies location** by checking page content

### Step 4: Navigate to Products
- You can either:
  - **Let the scraper stay on homepage** (you navigate manually)
  - **Modify the code** to search for specific products
  - **Modify the code** to navigate to a category URL

### Step 5: Load Products
- **Scrolls the page incrementally** to trigger lazy loading
- **Waits between scrolls** to allow content to load
- **Detects when no more content loads** (reached end of page)

### Step 6: Extract Data
- **Finds product containers** using defensive selectors
- **Extracts data from each product**:
  - Name (from headings or text)
  - Price (extracts numeric value from price text)
  - Discount (extracts percentage)
  - Quantity/Size (if available)
  - Image URL (from img tags)
  - Product URL (from link tags)
- **Handles missing data gracefully** (marks as "N/A")

### Step 7: Save Data
- **Saves to CSV** with proper headers
- **Saves to JSON** for structured data access
- **Includes timestamp** of when data was scraped

## 🔍 Verifying Whitefield Location

### Method 1: Visual Check
- After the scraper sets location, check the browser window
- Look for location indicator (usually top-right or in header)
- Should show "Whitefield" or "560067"

### Method 2: Check Page Source
- Right-click on page → "View Page Source"
- Search for "560067" or "Whitefield"
- If found, location is set correctly

### Method 3: Check Product Availability
- Navigate to a product category
- If products show prices and "Add to Cart" buttons, location is likely set
- If you see "Not available in your area", location might be wrong

### Method 4: Manual Verification
- The scraper will pause if it can't set location automatically
- You can manually:
  1. Click on location selector
  2. Enter "560067"
  3. Confirm
  4. Press Enter in terminal to continue

## 🐛 Debugging: No Products Found

If the scraper doesn't find any products, try these steps:

### 1. Check Location
- **Verify location is set to 560067** (see section above)
- Try manually setting location in browser
- Refresh page after setting location

### 2. Navigate to Products
- The scraper might be on homepage with no products visible
- **Manually navigate** to a category (e.g., "Groceries", "Fruits & Vegetables")
- Or modify `scraper.py` to automatically navigate:
  ```python
  # In main() function, uncomment and modify:
  navigate_to_category_or_search(driver, search_term="milk")
  # OR
  navigate_to_category_or_search(driver, category_url="https://www.zepto.com/category/groceries")
  ```

### 3. Check Selectors
- Zepto may have changed their HTML structure
- **Inspect the page** (F12 → Elements tab)
- Look for product containers and their classes/IDs
- Update selectors in `extract_product_data()` function

### 4. Check Network/JavaScript
- Ensure JavaScript is enabled
- Check browser console (F12) for errors
- Verify internet connection is stable

### 5. Increase Wait Times
- Some pages load slowly
- In `scraper.py`, increase wait times:
  ```python
  WebDriverWait(driver, 20)  # Increase from 10 to 20
  ```

### 6. Run in Non-Headless Mode
- The scraper runs with visible browser by default
- Watch what happens in the browser
- This helps identify where the process fails

## 🔧 Extending to Other Bangalore PIN Codes

To scrape for other locations, modify the configuration:

### Option 1: Change PIN Code
In `scraper.py`, change:
```python
WHITEFIELD_PIN = "560067"  # Change to your PIN code
```

### Option 2: Make It Configurable
Add command-line argument support:
```python
import sys

if len(sys.argv) > 1:
    PIN_CODE = sys.argv[1]
else:
    PIN_CODE = "560067"
```

Then run:
```bash
python scraper.py 560066  # For another PIN code
```

### Option 3: Multiple Locations
Modify the scraper to loop through multiple PIN codes:
```python
PIN_CODES = ["560067", "560066", "560068"]

for pin in PIN_CODES:
    # Set location for each PIN
    set_location_whitefield(driver, pin_code=pin)
    # Scrape products
    products = extract_product_data(driver)
    # Save with location-specific filename
    save_to_csv(products, f"output/zepto_{pin}_products.csv")
```

## 📁 Project Structure

```
zepto_scraper/
│
├── scraper.py                    # Main scraper script
├── requirements.txt              # Python dependencies
├── README.md                     # This file
│
└── output/                       # Output directory
    ├── zepto_whitefield_products.csv
    └── zepto_whitefield_products.json
```

## 🎯 Key Features

### Modular Functions
- `setup_driver()` - Browser initialization
- `set_location_whitefield()` - Location configuration
- `scroll_and_load_products()` - Handles lazy loading
- `extract_product_data()` - Data extraction
- `save_to_csv()` / `save_to_json()` - Data persistence

### Defensive Programming
- **Multiple selector strategies** - Tries different CSS selectors if one fails
- **Try/except blocks** - Handles errors gracefully
- **Explicit waits** - Waits for elements instead of hard sleeps
- **Human-like delays** - Random delays between actions

### Bot-Safe Behavior
- Realistic User-Agent
- Disabled automation flags
- Natural scrolling patterns
- Human-like interaction delays

## ⚠️ Important Notes

### Legal & Ethical
- **Educational/MVP purposes only** - Not for aggressive scraping
- **Respect robots.txt** - Check Zepto's robots.txt before scraping
- **Rate limiting** - Don't scrape too frequently
- **Terms of Service** - Review Zepto's ToS before use

### Technical Limitations
- **DOM changes** - Zepto may update their HTML, requiring selector updates
- **CAPTCHA** - May encounter CAPTCHA if scraping too frequently
- **Dynamic content** - Some content may load via AJAX after initial page load
- **Location dependency** - Products/prices vary by location

### Best Practices
- **Test selectors first** - Use browser DevTools to verify selectors
- **Start small** - Test with a few products before full scrape
- **Monitor behavior** - Watch the browser during first runs
- **Update regularly** - Check if selectors need updates

## 🔄 Updating Selectors

If Zepto changes their HTML structure, you'll need to update selectors:

1. **Open browser DevTools** (F12)
2. **Inspect a product element**
3. **Note the class/ID/data attributes**
4. **Update selectors in `extract_product_data()`**:
   ```python
   product_container_selectors = [
       "[class*='NewProductCard']",  # Add new selector
       # ... existing selectors
   ]
   ```

## 📊 Output Format

### CSV Columns
- `name` - Product name
- `price` - Product price (numeric)
- `discount` - Discount percentage (if available)
- `quantity` - Quantity/Size information
- `image_url` - Product image URL
- `product_url` - Link to product page
- `scraped_at` - Timestamp of scraping

### JSON Structure
```json
[
  {
    "name": "Product Name",
    "price": "99",
    "discount": "10%",
    "quantity": "500ml",
    "image_url": "https://...",
    "product_url": "https://...",
    "scraped_at": "2024-01-15 10:30:00"
  }
]
```

## 🆘 Troubleshooting

### ChromeDriver Issues (WinError 193)

If you encounter `WinError 193: %1 is not a valid Win32 application`:

1. **Clear ChromeDriver cache:**
   ```bash
   python fix_chromedriver.py
   ```
   Then try running the scraper again.

2. **Update webdriver-manager:**
   ```bash
   pip install --upgrade webdriver-manager
   ```

3. **Update Google Chrome:**
   - Make sure Chrome is up to date
   - ChromeDriver version must match your Chrome version

4. **Manual ChromeDriver download:**
   - Check your Chrome version: `chrome://version/`
   - Download matching ChromeDriver from: https://chromedriver.chromium.org/downloads
   - Place it in your PATH or project directory

5. **Architecture mismatch:**
   - Ensure you're using 64-bit Python if you have 64-bit Chrome
   - Check: `python -c "import platform; print(platform.architecture())"`

The scraper now automatically retries and clears cache on errors, so most issues should resolve automatically.

### Import Errors
- Ensure all dependencies are installed: `pip install -r requirements.txt`
- Use virtual environment: `python -m venv venv` then activate it

### No Products Extracted
- See "Debugging: No Products Found" section above
- Check if you're on a page with products
- Verify location is set correctly

### Browser Crashes
- Close other Chrome instances
- Update Chrome browser
- Try reducing `max_scrolls` in `scroll_and_load_products()`

## 📝 Customization Examples

### Search for Specific Products
```python
# In main() function:
navigate_to_category_or_search(driver, search_term="organic milk")
```

### Navigate to Specific Category
```python
# In main() function:
navigate_to_category_or_search(driver, category_url="https://www.zepto.com/category/fruits")
```

### Run in Headless Mode
```python
# At top of scraper.py:
HEADLESS_MODE = True
```

### Increase Scroll Count
```python
# In main() function:
scroll_and_load_products(driver, max_scrolls=10)  # Default is 5
```

## 🤝 Contributing

This is an educational project. Feel free to:
- Improve selectors
- Add error handling
- Enhance data extraction
- Add new features

## 📄 License

Educational/MVP purposes only. Use responsibly and in accordance with Zepto's Terms of Service.

---

**Happy Scraping! 🕷️**
