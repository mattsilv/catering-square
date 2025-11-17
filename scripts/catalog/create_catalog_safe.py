"""
Purpose: Production-safe catalog creation with duplicate prevention
Related: catalog_utils.py
Refactor if: N/A (production-ready script)

CRITICAL: This script is safe for production use - prevents duplicates
"""

import os
import sys
import json
import uuid
from pathlib import Path
from dotenv import load_dotenv
from square import Square
from square.client import SquareEnvironment

# Add src directory to Python path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT / 'src'))

from catalog_utils import create_or_update_category, create_or_update_item, check_for_duplicates

def create_catalog_safe():
    """
    Safely create/update catalog - prevents duplicates in production.

    This is the PRODUCTION-SAFE version that:
    1. Checks for existing items before creating
    2. Prevents duplicates
    3. Is idempotent (can be run multiple times safely)
    """
    load_dotenv()

    access_token = os.getenv('SQUARE_ACCESS_TOKEN')
    environment_name = os.getenv('SQUARE_ENVIRONMENT', 'sandbox')
    environment = SquareEnvironment.SANDBOX if environment_name.lower() == 'sandbox' else SquareEnvironment.PRODUCTION

    client = Square(token=access_token, environment=environment)

    print(f"🔒 PRODUCTION-SAFE Catalog Setup")
    print(f"   Environment: {environment_name.upper()}")
    print("=" * 60)
    print()

    # PRE-FLIGHT CHECK: Look for existing duplicates
    print("🔍 Pre-flight check: Scanning for existing duplicates...")
    duplicates = check_for_duplicates(client)

    if duplicates['items'] or duplicates['categories']:
        print("❌ DUPLICATES DETECTED - ABORTING!")
        print("\nFound duplicates:")
        for name, ids in duplicates['items'].items():
            print(f"   Item: {name} ({len(ids)} copies)")
        for name, ids in duplicates['categories'].items():
            print(f"   Category: {name} ({len(ids)} copies)")
        print("\nRun cleanup_duplicates.py first, then try again.")
        return

    print("✅ No duplicates found - safe to proceed\n")

    # Step 1: Create Categories
    print("📁 STEP 1: Creating Categories")
    print("-" * 60)

    categories_to_create = [
        {'name': 'Signature Salads', 'description': 'Just Salad signature salad bowls and plates for catering'},
        {'name': 'Wraps', 'description': 'Fresh wraps and sandwiches for catering orders'},
        {'name': 'Build Your Own', 'description': 'Customizable salads and bowls - build your own'},
        {'name': 'Smoothies', 'description': 'Fresh fruit smoothies and healthy beverages'},
        {'name': 'Snacks', 'description': 'Sides, snacks, and appetizers for catering'},
        {'name': 'Beverages', 'description': 'Drinks, juices, and beverage options'}
    ]

    category_ids = {}
    created_count = 0
    existing_count = 0

    for cat in categories_to_create:
        cat_id, was_created = create_or_update_category(
            client,
            cat['name'],
            cat['description'],
            idempotency_key=str(uuid.uuid4())
        )

        category_ids[cat['name']] = cat_id

        if was_created:
            print(f"   ✓ Created: {cat['name']}")
            created_count += 1
        else:
            print(f"   → Existing: {cat['name']}")
            existing_count += 1

    print(f"\nCategories: {created_count} created, {existing_count} existing\n")

    # Save category IDs
    with open('category_ids.json', 'w') as f:
        json.dump(category_ids, f, indent=2)

    # Step 2: Create Menu Items
    print("📦 STEP 2: Creating Menu Items")
    print("-" * 60)

    # Load Just Salad menu data
    with open('/tmp/menu.json', 'r') as f:
        content = f.read()
        if content.startswith('HTTP/'):
            json_start = max(content.find('{'), content.find('['))
            if json_start != -1:
                content = content[json_start:]
        menu_data = json.loads(content)

    # Define items to create
    items_to_create = [
        {
            'name': 'Autumn Caesar',
            'category': 'Signature Salads',
            'source_category_id': 100,
            'price': 1500
        },
        {
            'name': 'Honey Crispy Chicken Wrap',
            'category': 'Wraps',
            'source_category_id': 105,
            'price': 1500
        },
        {
            'name': 'Buffalo Cauliflower',
            'category': 'Build Your Own',
            'source_category_id': 100,
            'price': 1500
        },
        {
            'name': 'Strawberry Banana',
            'category': 'Smoothies',
            'source_category_id': 107,
            'price': 1500
        },
        {
            'name': 'Mixed Nuts & Trail Mix',
            'category': 'Snacks',
            'description': 'Assorted nuts, dried fruits, and healthy snack mix',
            'price': 500
        },
        {
            'name': 'Bottled Water & Drinks',
            'category': 'Beverages',
            'description': 'Selection of bottled water, sparkling water, and refreshing beverages',
            'price': 500
        }
    ]

    menu_item_ids = {}
    items_created_count = 0
    items_existing_count = 0

    for item_config in items_to_create:
        # Find menu data if from Just Salad
        description = item_config.get('description', '')
        image_url = None

        if 'source_category_id' in item_config:
            for menu_item in menu_data['menu_items']:
                if menu_item.get('name') == item_config['name']:
                    description = menu_item.get('description', '')
                    image_url = menu_item.get('image_url')
                    break

        # Create item
        item_id, was_created = create_or_update_item(
            client,
            item_name=item_config['name'],
            category_id=category_ids[item_config['category']],
            description=description,
            price_cents=item_config['price'],
            image_url=image_url,
            idempotency_key=str(uuid.uuid4())
        )

        menu_item_ids[item_config['name']] = item_id

        if was_created:
            print(f"   ✓ Created: {item_config['name']}")
            items_created_count += 1
        else:
            print(f"   → Existing: {item_config['name']}")
            items_existing_count += 1

    print(f"\nMenu Items: {items_created_count} created, {items_existing_count} existing\n")

    # Save menu item IDs
    with open('menu_item_ids.json', 'w') as f:
        json.dump(menu_item_ids, f, indent=2)

    # Final Summary
    print("=" * 60)
    print("✅ CATALOG SETUP COMPLETE")
    print("=" * 60)
    print(f"Categories: {len(category_ids)} total")
    print(f"Menu Items: {len(menu_item_ids)} total")
    print()
    print("This script is idempotent - safe to run multiple times.")
    print()

if __name__ == "__main__":
    create_catalog_safe()
