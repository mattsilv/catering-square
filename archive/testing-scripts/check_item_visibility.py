"""
Purpose: Check item visibility and location availability settings
Related: check_catalog.py
Refactor if: N/A (diagnostic script)
"""

import os
import json
from dotenv import load_dotenv
from square import Square
from square.client import SquareEnvironment

def check_item_visibility():
    """Check if items exist and their visibility settings"""
    load_dotenv()

    client = Square(
        token=os.getenv('SQUARE_ACCESS_TOKEN'),
        environment=SquareEnvironment.SANDBOX
    )

    # Load menu item IDs
    with open('menu_item_ids.json', 'r') as f:
        item_ids = json.load(f)

    print(f"🔍 Checking {len(item_ids)} menu items...\n")

    try:
        # Batch get all items
        response = client.catalog.batch_get(object_ids=list(item_ids.values()))

        if hasattr(response, 'errors') and response.errors:
            print("❌ Errors:")
            for error in response.errors:
                print(f"   {error.category}: {error.detail}")
            return

        if hasattr(response, 'objects') and response.objects:
            print(f"✅ Found {len(response.objects)} items:\n")

            for obj in response.objects:
                print(f"📦 {obj.item_data.name}")
                print(f"   ID: {obj.id}")
                print(f"   Type: {obj.type}")

                # Check location availability
                if hasattr(obj, 'present_at_all_locations'):
                    print(f"   Present at ALL locations: {obj.present_at_all_locations}")

                if hasattr(obj, 'present_at_location_ids'):
                    print(f"   Present at specific locations: {obj.present_at_location_ids}")

                if hasattr(obj, 'absent_at_location_ids'):
                    print(f"   Absent at locations: {obj.absent_at_location_ids}")

                # Check if it has category
                if hasattr(obj.item_data, 'category_id'):
                    print(f"   Category ID: {obj.item_data.category_id}")

                # Check variations
                if hasattr(obj.item_data, 'variations'):
                    print(f"   Variations: {len(obj.item_data.variations)}")

                print()

        else:
            print("❌ No items found")

        print("\n💡 Note: Items created via API should be visible at all locations by default.")
        print("   If not appearing in dashboard, try:")
        print("   1. Refresh the Square Dashboard")
        print("   2. Check you're logged into the correct sandbox account")
        print("   3. Navigate to: Items & Orders → Items")

    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_item_visibility()
