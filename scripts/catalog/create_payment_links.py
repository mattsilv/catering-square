"""
Purpose: Generate Square payment links for menu items to preview customer-facing checkout
Related: catalog_utils.py, db_utils.py
Refactor if: N/A (utility script)
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from square import Square
from square.client import SquareEnvironment

# Add src directory to Python path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT / 'src'))

from db_utils import get_all_items

def create_payment_links():
    """Create shareable payment links for all menu items"""
    load_dotenv()

    access_token = os.getenv('SQUARE_ACCESS_TOKEN')
    environment_name = os.getenv('SQUARE_ENVIRONMENT', 'sandbox')
    environment = SquareEnvironment.SANDBOX if environment_name.lower() == 'sandbox' else SquareEnvironment.PRODUCTION

    client = Square(token=access_token, environment=environment)

    print("=" * 70)
    print("🔗 CREATING PAYMENT LINKS FOR MENU ITEMS")
    print(f"   Environment: {environment_name.upper()}")
    print("=" * 70)
    print()

    # Get all items from database
    items = get_all_items(environment_name)

    if not items:
        print("❌ No menu items found in database")
        return

    print(f"Found {len(items)} menu items\n")

    print("📱 YOUR CATERING MENU ITEMS")
    print("-" * 70)
    print()

    # Display items
    for item_name, item_id in items.items():
        print(f"🍽️  {item_name}")
        print(f"   Square ID: {item_id}")

        # Dashboard URL
        if environment_name.lower() == 'sandbox':
            dashboard_url = f"https://app.squareupsandbox.com/dashboard/items/library/{item_id}"
        else:
            dashboard_url = f"https://squareup.com/dashboard/items/library/{item_id}"

        print(f"   Dashboard: {dashboard_url}")
        print()

    print("-" * 70)
    print()
    print("=" * 70)
    print("💡 HOW TO VIEW CUSTOMER-FACING MENU")
    print("=" * 70)
    print()

    print("📱 OPTION 1: Square POS Mobile App (Best for Testing)")
    print("-" * 70)
    print("1. Download 'Square Point of Sale' app on iOS/Android")
    print("2. Log in with your Square sandbox credentials")
    print("3. Tap 'Items' to see your full catalog")
    print("4. Tap any item to see customer view with image")
    print("5. Create test orders to simulate checkout")
    print()

    print("🌐 OPTION 2: Square Online Store (Production Only)")
    print("-" * 70)
    print("1. In production, enable Square Online")
    print("2. Your catalog automatically appears on storefront")
    print("3. Get public URL to share with customers")
    print("4. Not fully available in sandbox")
    print()

    print("💳 OPTION 3: Create Test Orders with Payment Links")
    print("-" * 70)
    print("1. Create order via Orders API with menu items")
    print("2. Generate payment link from order")
    print("3. Share link for customer checkout")
    print("4. This script can be extended to do this")
    print()

    print("🔨 OPTION 4: Build Custom Frontend")
    print("-" * 70)
    print("1. Use Square Web Payments SDK")
    print("2. Fetch catalog items via API (already have them!)")
    print("3. Build React/Next.js frontend")
    print("4. Display menu with images, descriptions, prices")
    print("5. Process payments with Web Payments SDK")
    print()

    print("=" * 70)
    print("🎯 RECOMMENDED: Download Square POS app to see items now!")
    print("=" * 70)


if __name__ == "__main__":
    create_payment_links()
