"""
Purpose: Create 2 test catering locations in Square based on Just Salad data
Related: .env, list_locations.py
Refactor if: N/A (one-time setup script)
"""

import os
import json
from dotenv import load_dotenv
from square import Square
from square.client import SquareEnvironment

def create_test_locations():
    """Create 2 test locations based on Just Salad store data"""
    load_dotenv()

    access_token = os.getenv('SQUARE_ACCESS_TOKEN')
    environment_name = os.getenv('SQUARE_ENVIRONMENT', 'sandbox')
    environment = SquareEnvironment.SANDBOX if environment_name.lower() == 'sandbox' else SquareEnvironment.PRODUCTION

    client = Square(token=access_token, environment=environment)

    # Load Just Salad locations
    with open('/tmp/store_locations.json', 'r') as f:
        content = f.read()
        if content.startswith('HTTP/'):
            json_start = content.find('{')
            if json_start != -1:
                content = content[json_start:]

        data = json.loads(content)
        locations_data = data.get('storelocations', [])

    # Select 2 locations to create
    test_locations = locations_data[:2]

    created_locations = []

    print("🏢 Creating test catering locations...\n")

    for i, loc_data in enumerate(test_locations, 1):
        location_name = f"{loc_data['name']} - Catering Test"
        address = loc_data.get('address', {})

        print(f"{i}. Creating: {location_name}")

        try:
            # Create location in Square
            response = client.locations.create(
                location={
                    'name': location_name,
                    'address': {
                        'address_line_1': address.get('address_1', ''),
                        'address_line_2': address.get('address_2', ''),
                        'locality': address.get('city', ''),
                        'administrative_district_level_1': 'NY',
                        'postal_code': address.get('zipcode', ''),
                        'country': 'US'
                    },
                    'phone_number': loc_data.get('phone', ''),
                    'business_name': 'Just Salad Catering Test',
                    'type': 'PHYSICAL',
                    'description': f"Test location for catering menu POC (Store #{loc_data.get('store_num', 'N/A')})"
                }
            )

            if hasattr(response, 'errors') and response.errors:
                print(f"   ❌ Error creating location:")
                for error in response.errors:
                    print(f"      - {error.category}: {error.detail}")
                continue

            if hasattr(response, 'location') and response.location:
                loc = response.location
                created_locations.append({
                    'name': loc.name,
                    'id': loc.id,
                    'original_store_num': loc_data.get('store_num')
                })
                print(f"   ✅ Created: {loc.name}")
                print(f"   ID: {loc.id}\n")

        except Exception as e:
            print(f"   ❌ Exception: {str(e)}\n")
            continue

    # Summary
    print(f"\n📊 Summary: Created {len(created_locations)} location(s)")

    if created_locations:
        print("\n📝 Location IDs to add to .env:")
        for loc in created_locations:
            print(f"   {loc['name']}: {loc['id']}")

        print(f"\n💡 Add these to your .env file:")
        print(f"SQUARE_TEST_LOCATION_1={created_locations[0]['id']}")
        if len(created_locations) > 1:
            print(f"SQUARE_TEST_LOCATION_2={created_locations[1]['id']}")

    return created_locations

if __name__ == "__main__":
    create_test_locations()
