"""
Purpose: Create sample menu items (1 per category) from Just Salad menu data
Related: category_ids.json, menu.json
Refactor if: >500 lines OR handling complex menu transformations
"""

import os
import json
import uuid
from dotenv import load_dotenv
from square import Square
from square.client import SquareEnvironment

def create_menu_items():
    """Create 1 sample menu item per category"""
    load_dotenv()

    access_token = os.getenv('SQUARE_ACCESS_TOKEN')
    environment_name = os.getenv('SQUARE_ENVIRONMENT', 'sandbox')
    environment = SquareEnvironment.SANDBOX if environment_name.lower() == 'sandbox' else SquareEnvironment.PRODUCTION

    client = Square(token=access_token, environment=environment)

    # Load category IDs from our previous script
    with open('category_ids.json', 'r') as f:
        category_ids = json.load(f)

    # Load Just Salad menu data
    with open('/tmp/menu.json', 'r') as f:
        content = f.read()
        if content.startswith('HTTP/'):
            json_start = max(content.find('{'), content.find('['))
            if json_start != -1:
                content = content[json_start:]
        menu_data = json.loads(content)

    # Map Just Salad category IDs to our Square category names
    category_mapping = {
        'Signature Salads': 100,   # Salads
        'Wraps': 105,              # Wraps
        'Build Your Own': 100,     # Also Salads (we'll pick a different item)
        'Smoothies': 107,          # Smoothies
        'Snacks': 71,              # Snacks
        'Beverages': 81            # Drinks
    }

    # Find one menu item per category
    items_to_create = {}

    for square_cat_name, js_cat_id in category_mapping.items():
        # Find first item from this Just Salad category
        for item in menu_data['menu_items']:
            if item.get('category_id') == js_cat_id:
                # Skip duplicates for "Build Your Own" (pick 2nd salad)
                if square_cat_name == 'Build Your Own' and 'Signature Salads' in items_to_create:
                    if items_to_create['Signature Salads']['name'] == item.get('name'):
                        continue

                items_to_create[square_cat_name] = item
                break

    print(f"📦 Creating {len(items_to_create)} menu items in Square Catalog...\n")

    # Prepare catalog objects
    catalog_objects = []

    for square_cat_name, menu_item in items_to_create.items():
        item_id = f"#{uuid.uuid4().hex[:16]}"
        variation_id = f"#{uuid.uuid4().hex[:16]}"

        # Get category ID from our mapping
        square_category_id = category_ids.get(square_cat_name)

        item_obj = {
            'type': 'ITEM',
            'id': item_id,
            'item_data': {
                'name': menu_item.get('name', 'Unnamed Item'),
                'description': menu_item.get('description', '')[:500],  # Max 500 chars
                'category_id': square_category_id,
                'variations': [{
                    'type': 'ITEM_VARIATION',
                    'id': variation_id,
                    'item_variation_data': {
                        'name': 'Regular',
                        'pricing_type': 'FIXED_PRICING',
                        'price_money': {
                            'amount': 1500,  # $15.00 in cents (placeholder price)
                            'currency': 'USD'
                        }
                    }
                }]
            }
        }

        # Add image URL if available
        if menu_item.get('image_url'):
            item_obj['item_data']['image_urls'] = [menu_item['image_url']]

        catalog_objects.append(item_obj)

        print(f"Preparing: {menu_item.get('name')}")
        print(f"   Category: {square_cat_name}")
        print(f"   Image: {menu_item.get('image_url', 'N/A')[:60]}...")
        print()

    # Batch create all items
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
            return None

        if hasattr(response, 'objects') and response.objects:
            created_items = {}

            print(f"\n✅ Successfully created {len(response.objects)} menu items:\n")

            for obj in response.objects:
                if hasattr(obj, 'item_data'):
                    item_name = obj.item_data.name
                    item_id = obj.id
                    created_items[item_name] = item_id
                    print(f"   ✓ {item_name}")
                    print(f"     ID: {item_id}\n")

            # Save item IDs to JSON file
            output_file = 'menu_item_ids.json'
            with open(output_file, 'w') as f:
                json.dump(created_items, f, indent=2)

            print(f"💾 Saved menu item IDs to {output_file}")
            print(f"\n📊 Summary: Created {len(created_items)} menu items")

            return created_items

    except Exception as e:
        print(f"❌ Exception occurred: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    create_menu_items()
