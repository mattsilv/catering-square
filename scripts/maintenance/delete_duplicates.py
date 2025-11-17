"""
Purpose: Delete duplicate catalog items - keep only the newest version of each
Related: cleanup_duplicates.py
Refactor if: N/A (one-time cleanup)
"""

import os
import json
from collections import defaultdict
from dotenv import load_dotenv
from square import Square
from square.client import SquareEnvironment

def delete_duplicates():
    """Find and delete duplicate items, keeping the newest version"""
    load_dotenv()

    client = Square(
        token=os.getenv('SQUARE_ACCESS_TOKEN'),
        environment=SquareEnvironment.SANDBOX
    )

    print("🔍 Finding all items...\n")

    # Get all item IDs
    search_response = client.catalog.search_items()

    if not (hasattr(search_response, 'items') and search_response.items):
        print("No items found")
        return

    all_item_ids = [item.id for item in search_response.items]
    print(f"Found {len(all_item_ids)} total items\n")

    # Batch get to retrieve full details
    details_response = client.catalog.batch_get(object_ids=all_item_ids)

    if not (hasattr(details_response, 'objects') and details_response.objects):
        print("Could not retrieve item details")
        return

    # Group by name
    items_by_name = defaultdict(list)
    for obj in details_response.objects:
        name = obj.item_data.name
        items_by_name[name].append(obj)

    # Find duplicates
    duplicates = {name: items for name, items in items_by_name.items() if len(items) > 1}

    if not duplicates:
        print("✅ No duplicates found!")
        return

    print(f"Found {len(duplicates)} items with duplicates:\n")

    ids_to_delete = []
    items_to_keep = {}

    for name, items in duplicates.items():
        # Sort by version (descending) - keep the highest version
        sorted_items = sorted(items, key=lambda x: x.version, reverse=True)
        keep = sorted_items[0]
        delete = sorted_items[1:]

        print(f"📦 {name}:")
        print(f"   ✓ Keeping: {keep.id} (v{keep.version})")

        items_to_keep[name] = keep.id

        for item in delete:
            print(f"   ✗ Deleting: {item.id} (v{item.version})")
            ids_to_delete.append(item.id)
        print()

    # Also keep non-duplicate items
    for name, items in items_by_name.items():
        if len(items) == 1:
            items_to_keep[name] = items[0].id

    if ids_to_delete:
        print(f"🗑️  Deleting {len(ids_to_delete)} duplicate items...\n")

        delete_response = client.catalog.batch_delete(object_ids=ids_to_delete)

        if hasattr(delete_response, 'errors') and delete_response.errors:
            print("❌ Errors:")
            for error in delete_response.errors:
                print(f"   - {error.category}: {error.detail}")
        else:
            print(f"✅ Successfully deleted {len(ids_to_delete)} duplicates\n")

            # Update menu_item_ids.json
            with open('menu_item_ids.json', 'w') as f:
                json.dump(items_to_keep, f, indent=2)
            print("📝 Updated menu_item_ids.json with clean IDs")

if __name__ == "__main__":
    delete_duplicates()
