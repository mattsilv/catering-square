"""
Purpose: Production-safe catalog creation with image handling and SQLite tracking
Related: catalog_utils.py, db_utils.py, image_utils.py
Refactor if: N/A (production-ready script)

CRITICAL: This script is safe for production use
- Prevents duplicates
- Tracks all IDs in SQLite database
- Downloads and uploads menu item images
"""

import sys
import json
import uuid
from pathlib import Path
from square import Square
from square.client import SquareEnvironment

# Add src directory to Python path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT / 'src'))

# Import our utilities
from env_utils import get_access_token, get_environment, print_environment_info, is_production
from catalog_utils import create_or_update_category, create_or_update_item, check_for_duplicates
from db_utils import (init_database, save_category, save_menu_item, save_location,
                      get_category_by_name, get_item_by_name, export_to_json, show_summary)
from image_utils import process_item_image


def create_catalog_with_images():
    """
    Complete catalog setup with images and database tracking.

    Features:
    - SQLite database tracking (sandbox + production)
    - Image download and upload
    - Duplicate prevention
    - Idempotent operations
    """
    # Get credentials from environment
    access_token = get_access_token()
    environment_name = get_environment()
    environment = SquareEnvironment.SANDBOX if environment_name == 'sandbox' else SquareEnvironment.PRODUCTION

    client = Square(token=access_token, environment=environment)

    # Display environment info
    print_environment_info()

    # Production safety check
    if is_production():
        response = input("⚠️  You are in PRODUCTION mode. Type 'yes' to continue: ")
        if response.lower() != 'yes':
            print("❌ Aborted. Change SQUARE_ENVIRONMENT to 'sandbox' in .env to test first.")
            return

    print("=" * 70)
    print("🔒 PRODUCTION-SAFE CATALOG SETUP WITH IMAGES")
    print(f"   Environment: {environment_name.upper()}")
    print(f"   Database: data/square_catalog.db")
    print("=" * 70)
    print()

    # Initialize database
    print("📊 Initializing database...")
    init_database()
    print()

    # PRE-FLIGHT CHECK
    print("🔍 Pre-flight check: Scanning for duplicates...")
    duplicates = check_for_duplicates(client)

    if duplicates['items'] or duplicates['categories']:
        print("❌ DUPLICATES DETECTED - ABORTING!")
        print("\nFound duplicates:")
        for name, ids in duplicates['items'].items():
            print(f"   Item: {name} ({len(ids)} copies)")
        for name, ids in duplicates['categories'].items():
            print(f"   Category: {name} ({len(ids)} copies)")
        print("\nRun cleanup_duplicates.py first.")
        return

    print("✅ No duplicates - safe to proceed\n")

    # STEP 1: Sync existing locations to database
    print("📍 STEP 1: Syncing Locations to Database")
    print("-" * 70)

    locations_response = client.locations.list()
    if hasattr(locations_response, 'locations') and locations_response.locations:
        for loc in locations_response.locations:
            save_location(
                environment=environment_name,
                square_id=loc.id,
                name=loc.name,
                address=str(loc.address) if hasattr(loc, 'address') else None,
                phone=loc.phone_number if hasattr(loc, 'phone_number') else None
            )
            print(f"   ✓ Synced: {loc.name}")

    print()

    # STEP 2: Create Categories
    print("📁 STEP 2: Creating Categories")
    print("-" * 70)

    categories_config = [
        {'name': 'Signature Salads', 'description': 'Just Salad signature salad bowls and plates for catering'},
        {'name': 'Wraps', 'description': 'Fresh wraps and sandwiches for catering orders'},
        {'name': 'Build Your Own', 'description': 'Customizable salads and bowls - build your own'},
        {'name': 'Smoothies', 'description': 'Fresh fruit smoothies and healthy beverages'},
        {'name': 'Snacks', 'description': 'Sides, snacks, and appetizers for catering'},
        {'name': 'Beverages', 'description': 'Drinks, juices, and beverage options'}
    ]

    created_count = 0
    existing_count = 0

    for cat in categories_config:
        # Check database first
        existing_id = get_category_by_name(environment_name, cat['name'])

        if existing_id:
            print(f"   → DB cache: {cat['name']} ({existing_id})")
            existing_count += 1
            continue

        # Create in Square
        cat_id, was_created = create_or_update_category(
            client,
            cat['name'],
            cat['description'],
            idempotency_key=str(uuid.uuid4())
        )

        # Save to database
        save_category(environment_name, cat_id, cat['name'], cat['description'])

        if was_created:
            print(f"   ✓ Created: {cat['name']}")
            created_count += 1
        else:
            print(f"   → Existing: {cat['name']}")
            existing_count += 1

    print(f"\nCategories: {created_count} created, {existing_count} existing\n")

    # STEP 3: Load Menu Data
    print("📥 STEP 3: Loading Just Salad Menu Data")
    print("-" * 70)

    with open('/tmp/menu.json', 'r') as f:
        content = f.read()
        if content.startswith('HTTP/'):
            json_start = max(content.find('{'), content.find('['))
            if json_start != -1:
                content = content[json_start:]
        menu_data = json.loads(content)

    print(f"   Loaded {len(menu_data.get('menu_items', []))} menu items from source\n")

    # STEP 4: Create Menu Items
    print("📦 STEP 4: Creating Menu Items")
    print("-" * 70)

    items_config = [
        {'name': 'Autumn Caesar', 'category': 'Signature Salads', 'js_cat': 100, 'price': 1500},
        {'name': 'Honey Crispy Chicken Wrap', 'category': 'Wraps', 'js_cat': 105, 'price': 1500},
        {'name': 'Buffalo Cauliflower', 'category': 'Build Your Own', 'js_cat': 100, 'price': 1500},
        {'name': 'Strawberry Banana', 'category': 'Smoothies', 'js_cat': 107, 'price': 1500},
        {
            'name': 'Mixed Nuts & Trail Mix',
            'category': 'Snacks',
            'description': 'Assorted nuts, dried fruits, and healthy snack mix',
            'price': 500
        },
        {
            'name': 'Bottled Water & Drinks',
            'category': 'Beverages',
            'description': 'Selection of bottled water and refreshing beverages',
            'price': 500
        }
    ]

    items_created = 0
    items_existing = 0

    for item_config in items_config:
        print(f"\n{item_config['name']}:")

        # Check database first
        existing_id = get_item_by_name(environment_name, item_config['name'])

        if existing_id:
            print(f"   → DB cache: {existing_id}")
            items_existing += 1
            continue

        # Find menu data from Just Salad
        description = item_config.get('description', '')
        image_url = None

        if 'js_cat' in item_config:
            for menu_item in menu_data['menu_items']:
                if menu_item.get('name') == item_config['name']:
                    description = menu_item.get('description', description)
                    image_url = menu_item.get('image_url')
                    break

        # Get category Square ID from database
        category_square_id = get_category_by_name(environment_name, item_config['category'])

        # Create item in Square
        item_id, was_created = create_or_update_item(
            client,
            item_name=item_config['name'],
            category_id=category_square_id,
            description=description,
            price_cents=item_config['price'],
            idempotency_key=str(uuid.uuid4())
        )

        if was_created:
            print(f"   ✓ Created in Square: {item_id}")
            items_created += 1
        else:
            print(f"   → Existing in Square: {item_id}")
            items_existing += 1

        # Save to database (without image ID initially)
        save_menu_item(
            environment=environment_name,
            square_id=item_id,
            name=item_config['name'],
            category_square_id=category_square_id,
            description=description,
            price_cents=item_config['price'],
            source_url=image_url
        )

    print(f"\nMenu Items: {items_created} created, {items_existing} existing\n")

    # STEP 5: Process Images
    print("🖼️  STEP 5: Processing Images")
    print("-" * 70)

    images_processed = 0

    for item_config in items_config:
        # Get item Square ID from database
        item_square_id = get_item_by_name(environment_name, item_config['name'])

        if not item_square_id:
            continue

        # Find image URL
        image_url = None

        if 'js_cat' in item_config:
            for menu_item in menu_data['menu_items']:
                if menu_item.get('name') == item_config['name']:
                    image_url = menu_item.get('image_url')
                    break

        if image_url:
            image_id = process_item_image(
                client,
                item_config['name'],
                item_square_id,
                image_url,
                environment_name
            )

            if image_id:
                # Update database with image ID
                category_square_id = get_category_by_name(environment_name, item_config['category'])
                save_menu_item(
                    environment=environment_name,
                    square_id=item_square_id,
                    name=item_config['name'],
                    category_square_id=category_square_id,
                    description=item_config.get('description', ''),
                    price_cents=item_config['price'],
                    image_square_id=image_id,
                    source_url=image_url
                )
                images_processed += 1

    print(f"\n✅ Images processed: {images_processed}\n")

    # STEP 6: Export to JSON (backward compatibility)
    print("📤 STEP 6: Exporting to JSON Files")
    print("-" * 70)

    export_to_json(environment_name)
    print()

    # Final Summary
    print("=" * 70)
    print("✅ CATALOG SETUP COMPLETE")
    print("=" * 70)

    show_summary(environment_name)

    print("\nFiles created:")
    print("   • data/square_catalog.db - SQLite database (source of truth)")
    print("   • data/category_ids.json - Category mappings (exported)")
    print("   • data/menu_item_ids.json - Menu item mappings (exported)")
    print(f"   • data/images/ - Downloaded images ({images_processed} files)")
    print()
    print("This script is idempotent - safe to run multiple times.")
    print()


if __name__ == "__main__":
    create_catalog_with_images()
