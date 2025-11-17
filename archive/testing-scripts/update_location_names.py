"""
Purpose: Update test location names to include store numbers
Related: create_test_locations.py, .env
Refactor if: N/A (one-time update script)
"""

import os
import json
from dotenv import load_dotenv
from square import Square
from square.client import SquareEnvironment

def update_location_names():
    """Update location names to include store numbers"""
    load_dotenv()

    access_token = os.getenv('SQUARE_ACCESS_TOKEN')
    environment_name = os.getenv('SQUARE_ENVIRONMENT', 'sandbox')
    environment = SquareEnvironment.SANDBOX if environment_name.lower() == 'sandbox' else SquareEnvironment.PRODUCTION

    client = Square(token=access_token, environment=environment)

    # Load Just Salad locations to get store numbers
    with open('/tmp/store_locations.json', 'r') as f:
        content = f.read()
        if content.startswith('HTTP/'):
            json_start = content.find('{')
            if json_start != -1:
                content = content[json_start:]

        data = json.loads(content)
        locations_data = data.get('storelocations', [])

    # Map of location IDs to update
    updates = [
        {
            'id': os.getenv('SQUARE_TEST_LOCATION_1'),  # LM1357D0WKHRR
            'store_num': locations_data[0].get('store_num'),
            'name': locations_data[0].get('name')
        },
        {
            'id': os.getenv('SQUARE_TEST_LOCATION_2'),  # L075SSAD0HCPR
            'store_num': locations_data[1].get('store_num'),
            'name': locations_data[1].get('name')
        }
    ]

    print("🔄 Updating location names to include store numbers...\n")

    for update in updates:
        location_id = update['id']
        store_num = update['store_num']
        base_name = update['name']
        new_name = f"#{store_num} {base_name}"

        print(f"Updating: {new_name}")

        try:
            response = client.locations.update(
                location_id=location_id,
                location={
                    'name': new_name,
                    'business_name': 'Just Salad Catering Test'
                }
            )

            if hasattr(response, 'errors') and response.errors:
                print(f"   ❌ Error:")
                for error in response.errors:
                    print(f"      - {error.category}: {error.detail}")
                continue

            if hasattr(response, 'location') and response.location:
                print(f"   ✅ Updated: {response.location.name}")
                print(f"   ID: {response.location.id}\n")

        except Exception as e:
            print(f"   ❌ Exception: {str(e)}\n")
            continue

    print("✅ Location names updated with store numbers")

if __name__ == "__main__":
    update_location_names()
