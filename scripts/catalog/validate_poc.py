"""
Purpose: Validate POC setup - verify locations, categories, and menu items
Related: .env, category_ids.json, menu_item_ids.json
Refactor if: N/A (validation script)
"""

import os
import json
from pathlib import Path
from dotenv import load_dotenv
from square import Square
from square.client import SquareEnvironment

# Get project root and data directory
PROJECT_ROOT = Path(__file__).parent.parent.parent
DATA_DIR = PROJECT_ROOT / 'data'

def validate_poc():
    """Validate the complete POC setup"""
    load_dotenv()

    access_token = os.getenv('SQUARE_ACCESS_TOKEN')
    environment_name = os.getenv('SQUARE_ENVIRONMENT', 'sandbox')
    environment = SquareEnvironment.SANDBOX if environment_name.lower() == 'sandbox' else SquareEnvironment.PRODUCTION

    client = Square(token=access_token, environment=environment)

    print("=" * 60)
    print("SQUARE CATERING MENU POC - VALIDATION REPORT")
    print("=" * 60)
    print()

    # 1. Validate Locations
    print("📍 LOCATIONS")
    print("-" * 60)

    response = client.locations.list()
    locations = response.locations if hasattr(response, 'locations') and response.locations else []

    expected_location_count = 3  # Default + 2 test locations
    actual_count = len(locations)

    print(f"Expected: {expected_location_count} locations")
    print(f"Found: {actual_count} locations")

    if actual_count >= expected_location_count:
        print("✅ PASS: Locations created successfully\n")
        for loc in locations:
            print(f"   • {loc.name} (ID: {loc.id})")
    else:
        print("❌ FAIL: Missing locations\n")

    print()

    # 2. Validate Categories
    print("📁 CATEGORIES")
    print("-" * 60)

    expected_categories = [
        'Signature Salads',
        'Wraps',
        'Build Your Own',
        'Smoothies',
        'Snacks',
        'Beverages'
    ]

    try:
        with open(DATA_DIR / 'category_ids.json', 'r') as f:
            category_ids = json.load(f)

        print(f"Expected: {len(expected_categories)} categories")
        print(f"Found: {len(category_ids)} categories")

        all_found = all(cat in category_ids for cat in expected_categories)

        if all_found:
            print("✅ PASS: All categories created\n")
            for cat_name, cat_id in category_ids.items():
                print(f"   • {cat_name} (ID: {cat_id})")
        else:
            print("❌ FAIL: Missing categories")
            missing = [cat for cat in expected_categories if cat not in category_ids]
            print(f"   Missing: {', '.join(missing)}\n")

    except FileNotFoundError:
        print("❌ FAIL: data/category_ids.json not found\n")
        category_ids = {}

    print()

    # 3. Validate Menu Items
    print("📦 MENU ITEMS")
    print("-" * 60)

    try:
        with open(DATA_DIR / 'menu_item_ids.json', 'r') as f:
            menu_items = json.load(f)

        expected_item_count = 6  # 1 per category
        actual_item_count = len(menu_items)

        print(f"Expected: {expected_item_count} menu items")
        print(f"Found: {actual_item_count} menu items")

        if actual_item_count >= expected_item_count:
            print("✅ PASS: Menu items created\n")
            for item_name, item_id in menu_items.items():
                print(f"   • {item_name} (ID: {item_id})")
        else:
            print(f"❌ FAIL: Only {actual_item_count}/{expected_item_count} items created\n")

    except FileNotFoundError:
        print("❌ FAIL: data/menu_item_ids.json not found\n")
        menu_items = {}

    print()

    # 4. Overall Summary
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)

    all_passed = (
        actual_count >= expected_location_count and
        len(category_ids) >= len(expected_categories) and
        len(menu_items) >= expected_item_count
    )

    if all_passed:
        print("✅ POC VALIDATION PASSED")
        print()
        print("Next Steps:")
        print("1. Log into Square Dashboard: https://squareup.com/dashboard")
        print("2. Navigate to: Items & Orders → Items")
        print("3. Verify categories and menu items appear correctly")
        print("4. Test creating an order with the catering items")
        print()
        print("Square Dashboard URLs:")
        if environment_name.lower() == 'sandbox':
            print("   • Sandbox: https://squareup.com/dashboard/items/library")
            print("   • Locations: https://squareup.com/dashboard/locations")
    else:
        print("❌ POC VALIDATION FAILED")
        print("Please review the errors above and fix missing components.")

    print("=" * 60)
    print()

if __name__ == "__main__":
    validate_poc()
