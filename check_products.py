"""Quick script to check extracted products."""
import csv

with open('output/zepto_products.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    products = list(reader)

print(f"Total products extracted: {len(products)}")
print(f"Unique product names: {len(set(p['name'] for p in products))}")

# Check for duplicates
names = [p['name'] for p in products]
duplicates = [name for name in names if names.count(name) > 1]
if duplicates:
    print(f"\nDuplicate names found: {set(duplicates)}")

# Show first few products
print("\nFirst 5 products:")
for i, p in enumerate(products[:5], 1):
    print(f"{i}. {p['name']} - Rs.{p['price']}")
