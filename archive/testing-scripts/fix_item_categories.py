"""
Purpose: Fix item category associations
Related: create_menu_items.py, category_ids.json
Refactor if: N/A (fix script)
"""

import os
import json
import uuid
from dotenv import load_dotenv
from square import Square
from square.client import SquareEnvironment

def fix_item_categories():
    """Update items to properly associate with categories"""
    load_dotenv()

    client = Square(
        token=os.getenv('SQUARE_ACCESS_TOKEN'),
        environment=SquareEnvironment.SANDBOX
    )

    # Load category and item mappings
    with open('category_ids.json', 'r') as f:
        category_ids = json.load(f)

    with open('menu_item_ids.json', 'r') as f:
        menu_items = json.load(f)

    # Define item-to-category mapping
    item_category_map = {
        'Autumn Caesar': 'Signature Salads',
        'Honey Crispy Chicken Wrap': 'Wraps',
        'Buffalo Cauliflower': 'Build Your Own',
        'Strawberry Banana': 'Smoothies',
        'Mixed Nuts & Trail Mix': 'Snacks',
        'Bottled Water & Drinks': 'Beverages'
    }

    print("🔧 Fixing item category associations...\n")

    # First, retrieve all items to get their current state
    item_ids = list(menu_items.values())
    response = client.catalog.batch_get(object_ids=item_ids)

    if not (hasattr(response, 'objects') and response.objects):
        print("❌ Could not retrieve items")
        return

    # Prepare updated items
    updated_objects = []

    for obj in response.objects:
        item_name = obj.item_data.name
        category_name = item_category_map.get(item_name)

        if not category_name:
            print(f"⚠️  No category mapping for: {item_name}")
            continue

        category_id = category_ids.get(category_name)

        if not category_id:
            print(f"⚠️  Category ID not found for: {category_name}")
            continue

        # Update the item to include category_id
        updated_obj = {
            'type': 'ITEM',
            'id': obj.id,
            'version': obj.version,  # Important: include version for updates
            'item_data': {
                'name': obj.item_data.name,
                'description': obj.item_data.description if hasattr(obj.item_data, 'description') else '',
                'category_id': category_id,
                'variations': []
            }
        }

        # Preserve variations
        if hasattr(obj.item_data, 'variations'):
            for var in obj.item_data.variations:
                updated_obj['item_data']['variations'].append({
                    'type': 'ITEM_VARIATION',
                    'id': var.id,
                    'version': var.version,
                    'item_variation_data': {
                        'name': var.item_variation_data.name,
                        'pricing_type': var.item_variation_data.pricing_type,
                        'price_money': {
                            'amount': var.item_variation_data.price_money.amount,
                            'currency': var.item_variation_data.price_money.currency
                        }
                    }
                })

        # Preserve image URLs if they exist
        if hasattr(obj.item_data, 'image_ids') and obj.item_data.image_ids:
            updated_obj['item_data']['image_ids'] = obj.item_data.image_ids

        updated_objects.append(updated_obj)

        print(f"Updating: {item_name} → {category_name}")

    # Batch update all items
    try:
        idempotency_key = str(uuid.uuid4())

        update_response = client.catalog.batch_upsert(
            idempotency_key=idempotency_key,
            batches=[{
                'objects': updated_objects
            }]
        )

        if hasattr(update_response, 'errors') and update_response.errors:
            print("\n❌ API Errors:")
            for error in update_response.errors:
                print(f"   - {error.category}: {error.detail}")
            return

        if hasattr(update_response, 'objects') and update_response.objects:
            print(f"\n✅ Successfully updated {len(update_response.objects)} items")

            # Verify categories were set
            print("\nVerifying category assignments...")
            verify_response = client.catalog.batch_get(object_ids=item_ids)

            if hasattr(verify_response, 'objects') and verify_response.objects:
                for obj in verify_response.objects:
                    cat_id = obj.item_data.category_id if hasattr(obj.item_data, 'category_id') else 'None'
                    print(f"   • {obj.item_data.name}: {cat_id}")

    except Exception as e:
        print(f"\n❌ Exception: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    fix_item_categories()
