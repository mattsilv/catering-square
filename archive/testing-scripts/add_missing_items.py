"""
Purpose: Add placeholder items for Snacks and Beverages categories
Related: category_ids.json, create_menu_items.py
Refactor if: N/A (one-time script)
"""

import json
import uuid
from dotenv import load_dotenv
from square import Square
from square.client import SquareEnvironment
import os

def add_missing_items():
    """Add Snacks and Beverages placeholder items"""
    load_dotenv()

    access_token = os.getenv('SQUARE_ACCESS_TOKEN')
    environment_name = os.getenv('SQUARE_ENVIRONMENT', 'sandbox')
    environment = SquareEnvironment.SANDBOX if environment_name.lower() == 'sandbox' else SquareEnvironment.PRODUCTION

    client = Square(token=access_token, environment=environment)

    # Load category IDs
    with open('category_ids.json', 'r') as f:
        category_ids = json.load(f)

    # Define placeholder items
    placeholder_items = [
        {
            'category': 'Snacks',
            'name': 'Mixed Nuts & Trail Mix',
            'description': 'Assorted nuts, dried fruits, and healthy snack mix perfect for catering events'
        },
        {
            'category': 'Beverages',
            'name': 'Bottled Water & Drinks',
            'description': 'Selection of bottled water, sparkling water, and refreshing beverages'
        }
    ]

    print("📦 Adding missing menu items...\n")

    catalog_objects = []

    for item_data in placeholder_items:
        item_id = f"#{uuid.uuid4().hex[:16]}"
        variation_id = f"#{uuid.uuid4().hex[:16]}"

        square_category_id = category_ids.get(item_data['category'])

        catalog_objects.append({
            'type': 'ITEM',
            'id': item_id,
            'item_data': {
                'name': item_data['name'],
                'description': item_data['description'],
                'category_id': square_category_id,
                'variations': [{
                    'type': 'ITEM_VARIATION',
                    'id': variation_id,
                    'item_variation_data': {
                        'name': 'Regular',
                        'pricing_type': 'FIXED_PRICING',
                        'price_money': {
                            'amount': 500,  # $5.00 in cents
                            'currency': 'USD'
                        }
                    }
                }]
            }
        })

        print(f"Preparing: {item_data['name']}")
        print(f"   Category: {item_data['category']}\n")

    # Batch create items
    try:
        idempotency_key = str(uuid.uuid4())

        response = client.catalog.batch_upsert(
            idempotency_key=idempotency_key,
            batches=[{
                'objects': catalog_objects
            }]
        )

        if hasattr(response, 'errors') and response.errors:
            print("❌ API Error:")
            for error in response.errors:
                print(f"   - {error.category}: {error.detail}")
            return

        if hasattr(response, 'objects') and response.objects:
            # Load existing menu items
            with open('menu_item_ids.json', 'r') as f:
                existing_items = json.load(f)

            print(f"\n✅ Successfully created {len(response.objects)} items:\n")

            for obj in response.objects:
                if hasattr(obj, 'item_data'):
                    item_name = obj.item_data.name
                    item_id = obj.id
                    existing_items[item_name] = item_id
                    print(f"   ✓ {item_name}")
                    print(f"     ID: {item_id}\n")

            # Update menu_item_ids.json
            with open('menu_item_ids.json', 'w') as f:
                json.dump(existing_items, f, indent=2)

            print(f"💾 Updated menu_item_ids.json")
            print(f"📊 Total menu items: {len(existing_items)}")

    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    add_missing_items()
