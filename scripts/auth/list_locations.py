"""
Purpose: List all existing locations in Square sandbox
Related: .env, test_auth.py
Refactor if: N/A (simple utility script)
"""

import os
from dotenv import load_dotenv
from square import Square
from square.client import SquareEnvironment

def list_locations():
    """List all locations in the Square account"""
    load_dotenv()

    access_token = os.getenv('SQUARE_ACCESS_TOKEN')
    environment_name = os.getenv('SQUARE_ENVIRONMENT', 'sandbox')
    environment = SquareEnvironment.SANDBOX if environment_name.lower() == 'sandbox' else SquareEnvironment.PRODUCTION

    client = Square(token=access_token, environment=environment)

    print("📍 Fetching all locations...\n")
    response = client.locations.list()

    if hasattr(response, 'errors') and response.errors:
        print("❌ API Error:")
        for error in response.errors:
            print(f"   - {error.category}: {error.detail}")
        return

    locations = response.locations if hasattr(response, 'locations') and response.locations else []

    print(f"Found {len(locations)} location(s):\n")

    for i, loc in enumerate(locations, 1):
        print(f"{i}. {loc.name}")
        print(f"   ID: {loc.id}")
        print(f"   Status: {loc.status if hasattr(loc, 'status') else 'N/A'}")
        print(f"   Type: {loc.type if hasattr(loc, 'type') else 'N/A'}")

        if hasattr(loc, 'address') and loc.address:
            addr = loc.address
            print(f"   Address: {addr.address_line_1 if hasattr(addr, 'address_line_1') else ''}")
            if hasattr(addr, 'locality') and hasattr(addr, 'administrative_district_level_1'):
                print(f"            {addr.locality}, {addr.administrative_district_level_1} {addr.postal_code if hasattr(addr, 'postal_code') else ''}")

        if hasattr(loc, 'capabilities'):
            print(f"   Capabilities: {', '.join(loc.capabilities)}")

        print()

if __name__ == "__main__":
    list_locations()
