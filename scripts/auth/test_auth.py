"""
Purpose: Test Square API authentication with sandbox credentials
Related: .env configuration file
Refactor if: N/A (simple test script)
"""

import os
from dotenv import load_dotenv
from square import Square
from square.client import SquareEnvironment

def test_authentication():
    """Test Square API authentication and basic connectivity"""

    # Load environment variables
    load_dotenv()

    access_token = os.getenv('SQUARE_ACCESS_TOKEN')
    environment_name = os.getenv('SQUARE_ENVIRONMENT', 'sandbox')

    if not access_token:
        print("❌ Error: SQUARE_ACCESS_TOKEN not found in .env file")
        return False

    # Convert environment string to enum
    environment = SquareEnvironment.SANDBOX if environment_name.lower() == 'sandbox' else SquareEnvironment.PRODUCTION

    print(f"🔑 Testing Square API authentication...")
    print(f"   Environment: {environment_name.upper()}")
    print(f"   Access Token: {access_token[:10]}...{access_token[-10:]}")
    print()

    try:
        # Initialize Square client
        client = Square(
            token=access_token,
            environment=environment
        )

        # Test API connectivity by listing locations
        print("📍 Fetching locations...")
        response = client.locations.list()

        # Check for errors
        if hasattr(response, 'errors') and response.errors:
            print("❌ API Error:")
            for error in response.errors:
                print(f"   - {error.category}: {error.detail}")
            return False

        # Get locations from response
        locations = response.locations if hasattr(response, 'locations') and response.locations else []

        print(f"✅ Authentication successful!")
        print(f"   Found {len(locations)} location(s):")

        for loc in locations:
            print(f"   - {loc.name} (ID: {loc.id})")
            print(f"     Status: {loc.status if hasattr(loc, 'status') else 'N/A'}")
            if hasattr(loc, 'address') and loc.address:
                print(f"     Address: {loc.address.address_line_1 if hasattr(loc.address, 'address_line_1') else 'N/A'}")
            print()

        return True

    except Exception as e:
        print(f"❌ Exception occurred: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_authentication()
    exit(0 if success else 1)
