"""
Purpose: Create 6 catering categories in Square Catalog
Related: .env, category_ids.json
Refactor if: N/A (one-time setup script)
"""

import os
import json
from dotenv import load_dotenv
from square import Square
from square.client import SquareEnvironment
import uuid

def create_catering_categories():
    """Create 6 catering menu categories in Square Catalog"""
    load_dotenv()

    access_token = os.getenv('SQUARE_ACCESS_TOKEN')
    environment_name = os.getenv('SQUARE_ENVIRONMENT', 'sandbox')
    environment = SquareEnvironment.SANDBOX if environment_name.lower() == 'sandbox' else SquareEnvironment.PRODUCTION

    client = Square(token=access_token, environment=environment)

    # Define the 6 catering categories
    categories = [
        {
            'name': 'Signature Salads',
            'description': 'Just Salad signature salad bowls and plates for catering'
        },
        {
            'name': 'Wraps',
            'description': 'Fresh wraps and sandwiches for catering orders'
        },
        {
            'name': 'Build Your Own',
            'description': 'Customizable salads and bowls - build your own'
        },
        {
            'name': 'Smoothies',
            'description': 'Fresh fruit smoothies and healthy beverages'
        },
        {
            'name': 'Snacks',
            'description': 'Sides, snacks, and appetizers for catering'
        },
        {
            'name': 'Beverages',
            'description': 'Drinks, juices, and beverage options'
        }
    ]

    created_categories = {}

    print("📁 Creating catering categories in Square Catalog...\n")

    # Prepare batch upsert request
    catalog_objects = []

    for category in categories:
        # Generate unique ID for this category
        temp_id = f"#{uuid.uuid4().hex[:16]}"

        catalog_objects.append({
            'type': 'CATEGORY',
            'id': temp_id,
            'category_data': {
                'name': category['name'],
                'description': category['description']
            }
        })

    try:
        # Batch create all categories at once
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
            print(f"✅ Successfully created {len(response.objects)} categories:\n")

            for obj in response.objects:
                if hasattr(obj, 'category_data'):
                    cat_name = obj.category_data.name
                    cat_id = obj.id
                    created_categories[cat_name] = cat_id
                    print(f"   ✓ {cat_name}")
                    print(f"     ID: {cat_id}\n")

        # Save category IDs to JSON file
        output_file = 'category_ids.json'
        with open(output_file, 'w') as f:
            json.dump(created_categories, f, indent=2)

        print(f"💾 Saved category IDs to {output_file}")
        print(f"\n📊 Summary: Created {len(created_categories)} categories")

        return created_categories

    except Exception as e:
        print(f"❌ Exception occurred: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    create_catering_categories()
