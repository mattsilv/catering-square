"""
Purpose: Safely test production credentials and environment setup (READ-ONLY)
Related: env_utils.py, test_auth.py
Refactor if: N/A (simple validation script)

This script performs read-only checks to verify production setup is correct.
NO data is created or modified.
"""

import sys
from pathlib import Path

# Add src directory to Python path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT / 'src'))

from env_utils import (
    get_environment, get_access_token, get_main_location_id,
    print_environment_info, is_production
)
from square import Square
from square.client import SquareEnvironment


def test_production_setup():
    """Test production credentials and environment (read-only)"""

    print("=" * 70)
    print("🔍 PRODUCTION SETUP VALIDATION (READ-ONLY)")
    print("=" * 70)
    print()

    # Check environment
    env = get_environment()
    if env != 'production':
        print(f"❌ Current environment is '{env}', not 'production'")
        print()
        print("To test production:")
        print("1. Open .env file")
        print("2. Change: SQUARE_ENVIRONMENT=production")
        print("3. Run this script again")
        return False

    # Display environment info
    print_environment_info()

    # Get credentials
    try:
        access_token = get_access_token()
        main_location_id = get_main_location_id()
    except ValueError as e:
        print(f"❌ Configuration error: {e}")
        return False

    # Create Square client
    client = Square(
        token=access_token,
        environment=SquareEnvironment.PRODUCTION
    )

    print("🔧 Running Production Checks...")
    print("-" * 70)
    print()

    all_passed = True

    # TEST 1: Authentication
    print("1️⃣  Testing Authentication...")
    try:
        result = client.locations.list()
        if hasattr(result, 'locations') and result.locations:
            print(f"   ✅ Authentication successful")
            print(f"   Found {len(result.locations)} location(s)")
        else:
            print("   ❌ Authentication failed: No locations returned")
            all_passed = False
    except Exception as e:
        print(f"   ❌ Authentication failed: {e}")
        all_passed = False
    print()

    # TEST 2: List Locations
    print("2️⃣  Listing Production Locations...")
    try:
        result = client.locations.list()
        if hasattr(result, 'locations') and result.locations:
            for loc in result.locations:
                marker = "⭐" if loc.id == main_location_id else "  "
                print(f"   {marker} {loc.name}")
                print(f"      ID: {loc.id}")
                print(f"      Status: {loc.status}")

                if hasattr(loc, 'address'):
                    print(f"      Address: {loc.address.address_line_1 if loc.address.address_line_1 else 'N/A'}")
                print()

            # Verify main location exists
            location_ids = [loc.id for loc in result.locations]
            if main_location_id in location_ids:
                print(f"   ✅ Main location ID verified: {main_location_id}")
            else:
                print(f"   ⚠️  Main location ID not found: {main_location_id}")
                print(f"   Update PRODUCTION_LOCATION_MAIN in .env")
                all_passed = False
        else:
            print("   ❌ No locations found")
            all_passed = False
    except Exception as e:
        print(f"   ❌ Failed to list locations: {e}")
        all_passed = False
    print()

    # TEST 3: Check Existing Catalog
    print("3️⃣  Checking Existing Catalog...")
    try:
        # List categories
        result = client.catalog.list(types='CATEGORY')
        if result.is_success():
            categories = result.body.get('objects', [])
            print(f"   Categories: {len(categories)} found")
            if categories:
                for cat in categories[:5]:  # Show first 5
                    print(f"      • {cat['category_data']['name']}")
                if len(categories) > 5:
                    print(f"      ... and {len(categories) - 5} more")
        else:
            print("   Categories: 0 (none found)")

        print()

        # List items
        result = client.catalog.list(types='ITEM')
        if result.is_success():
            items = result.body.get('objects', [])
            print(f"   Items: {len(items)} found")
            if items:
                for item in items[:5]:  # Show first 5
                    print(f"      • {item['item_data']['name']}")
                if len(items) > 5:
                    print(f"      ... and {len(items) - 5} more")
        else:
            print("   Items: 0 (none found)")

        print()
        if categories or items:
            print("   ⚠️  Production catalog already has items")
            print("   Review before deploying to avoid duplicates")
        else:
            print("   ✅ Production catalog is empty - safe to deploy")

    except Exception as e:
        print(f"   ⚠️  Could not check catalog: {e}")

    print()

    # TEST 4: Check Merchant Info
    print("4️⃣  Checking Merchant Information...")
    try:
        result = client.merchants.list()
        if result.is_success():
            merchants = result.body.get('merchant', [])
            if merchants:
                for merchant in merchants[:1]:  # Show first merchant
                    print(f"   Business Name: {merchant.get('business_name', 'N/A')}")
                    print(f"   Merchant ID: {merchant.get('id', 'N/A')}")
                    print(f"   Country: {merchant.get('country', 'N/A')}")
                    print(f"   Currency: {merchant.get('currency', 'N/A')}")
                print(f"   ✅ Merchant info retrieved")
            else:
                print("   ⚠️  No merchant info found")
        else:
            print("   ⚠️  Could not retrieve merchant info")
    except Exception as e:
        print(f"   ⚠️  Could not check merchant: {e}")

    print()
    print("=" * 70)

    if all_passed:
        print("✅ ALL CHECKS PASSED - Production setup is valid")
        print("=" * 70)
        print()
        print("🎯 Next Steps:")
        print("   1. Review PRODUCTION_DEPLOYMENT.md")
        print("   2. Get stakeholder approval")
        print("   3. Run: python scripts/catalog/create_catalog_with_images.py")
    else:
        print("❌ SOME CHECKS FAILED - Fix issues before deploying")
        print("=" * 70)
        print()
        print("🔧 Troubleshooting:")
        print("   1. Verify PRODUCTION_ACCESS_TOKEN in .env")
        print("   2. Check token hasn't expired")
        print("   3. Verify PRODUCTION_LOCATION_MAIN matches a real location")

    print()
    return all_passed


if __name__ == "__main__":
    success = test_production_setup()
    sys.exit(0 if success else 1)
