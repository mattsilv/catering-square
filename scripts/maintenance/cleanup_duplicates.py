"""
Purpose: Remove duplicate items and categories from Square Catalog
Related: create_menu_items.py, create_categories.py
Refactor if: N/A (cleanup script)
"""

import os
import json
from collections import defaultdict
from dotenv import load_dotenv
from square import Square
from square.client import SquareEnvironment

def cleanup_duplicates():
    """Find and remove duplicate catalog items"""
    load_dotenv()

    client = Square(
        token=os.getenv('SQUARE_ACCESS_TOKEN'),
        environment=SquareEnvironment.SANDBOX
    )

    print("🔍 Scanning catalog for duplicates...\n")

    # Search for all items and categories
    try:
        response = client.catalog.list(
            types='ITEM,CATEGORY'
        )

        items_by_name = defaultdict(list)
        categories_by_name = defaultdict(list)

        if hasattr(response, 'objects') and response.objects:
            for obj in response.objects:
                if obj.type == 'ITEM':
                    items_by_name[obj.item_data.name].append(obj)
                elif obj.type == 'CATEGORY':
                    categories_by_name[obj.category_data.name].append(obj)

        # Find duplicates
        duplicate_items = {name: objs for name, objs in items_by_name.items() if len(objs) > 1}
        duplicate_categories = {name: objs for name, objs in categories_by_name.items() if len(objs) > 1}

        print(f"Found {len(duplicate_items)} duplicate item names")
        print(f"Found {len(duplicate_categories)} duplicate category names\n")

        # Collect IDs to delete (keep the newest version of each)
        ids_to_delete = []

        # Process duplicate items - keep the one with highest version
        for name, objects in duplicate_items.items():
            sorted_objs = sorted(objects, key=lambda x: x.version, reverse=True)
            keep = sorted_objs[0]
            delete = sorted_objs[1:]

            print(f"📦 {name}:")
            print(f"   Keeping: {keep.id} (version {keep.version})")
            for obj in delete:
                print(f"   Deleting: {obj.id} (version {obj.version})")
                ids_to_delete.append(obj.id)
            print()

        # Process duplicate categories
        for name, objects in duplicate_categories.items():
            sorted_objs = sorted(objects, key=lambda x: x.version, reverse=True)
            keep = sorted_objs[0]
            delete = sorted_objs[1:]

            print(f"📁 {name}:")
            print(f"   Keeping: {keep.id} (version {keep.version})")
            for obj in delete:
                print(f"   Deleting: {obj.id} (version {obj.version})")
                ids_to_delete.append(obj.id)
            print()

        if ids_to_delete:
            print(f"\n🗑️  Deleting {len(ids_to_delete)} duplicate objects...")

            # Batch delete
            delete_response = client.catalog.batch_delete(
                object_ids=ids_to_delete
            )

            if hasattr(delete_response, 'errors') and delete_response.errors:
                print("❌ Errors during deletion:")
                for error in delete_response.errors:
                    print(f"   - {error.category}: {error.detail}")
            else:
                print(f"✅ Successfully deleted {len(ids_to_delete)} duplicates")

                # Update our JSON files with the correct IDs
                print("\n📝 Updating local ID files...")

                # Update category_ids.json
                updated_categories = {}
                for name, objs in categories_by_name.items():
                    if name in duplicate_categories:
                        # Use the one we kept (highest version)
                        kept = sorted(objs, key=lambda x: x.version, reverse=True)[0]
                        updated_categories[name] = kept.id
                    else:
                        updated_categories[name] = objs[0].id

                with open('category_ids.json', 'w') as f:
                    json.dump(updated_categories, f, indent=2)
                print("   ✓ Updated category_ids.json")

                # Update menu_item_ids.json
                updated_items = {}
                for name, objs in items_by_name.items():
                    if name in duplicate_items:
                        # Use the one we kept (highest version)
                        kept = sorted(objs, key=lambda x: x.version, reverse=True)[0]
                        updated_items[name] = kept.id
                    else:
                        updated_items[name] = objs[0].id

                with open('menu_item_ids.json', 'w') as f:
                    json.dump(updated_items, f, indent=2)
                print("   ✓ Updated menu_item_ids.json")

        else:
            print("✅ No duplicates found!")

    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    cleanup_duplicates()
