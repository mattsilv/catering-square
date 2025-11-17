"""
Purpose: Check catalog items and their visibility
Related: validate_poc.py
Refactor if: N/A (diagnostic script)
"""

import os
from dotenv import load_dotenv
from square import Square
from square.client import SquareEnvironment

def check_catalog():
    """Check what items exist in the catalog"""
    load_dotenv()

    access_token = os.getenv('SQUARE_ACCESS_TOKEN')
    environment_name = os.getenv('SQUARE_ENVIRONMENT', 'sandbox')
    environment = SquareEnvironment.SANDBOX if environment_name.lower() == 'sandbox' else SquareEnvironment.PRODUCTION

    client = Square(token=access_token, environment=environment)

    print("🔍 Checking Square Catalog...\n")

    try:
        # List all catalog objects
        response = client.catalog.list(
            types='ITEM,CATEGORY'
        )

        if hasattr(response, 'errors') and response.errors:
            print("❌ API Error:")
            for error in response.errors:
                print(f"   - {error.category}: {error.detail}")
            return

        items = []
        categories = []

        if hasattr(response, 'objects') and response.objects:
            for obj in response.objects:
                if obj.type == 'ITEM':
                    items.append(obj)
                elif obj.type == 'CATEGORY':
                    categories.append(obj)

        print(f"📁 Categories found: {len(categories)}")
        for cat in categories:
            print(f"   • {cat.category_data.name} (ID: {cat.id})")

        print(f"\n📦 Items found: {len(items)}")
        for item in items:
            print(f"   • {item.item_data.name} (ID: {item.id})")
            if hasattr(item.item_data, 'category_id') and item.item_data.category_id:
                print(f"     Category: {item.item_data.category_id}")

            # Check if item has location associations
            if hasattr(item, 'present_at_all_locations'):
                print(f"     Present at all locations: {item.present_at_all_locations}")

            if hasattr(item, 'present_at_location_ids'):
                print(f"     Present at specific locations: {item.present_at_location_ids}")

            print()

        if len(items) == 0:
            print("\n⚠️  No items found in catalog!")
            print("   This could mean:")
            print("   1. Items weren't created successfully")
            print("   2. You're logged into a different Square account")
            print("   3. Items are in a different environment (sandbox vs production)")

    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_catalog()
