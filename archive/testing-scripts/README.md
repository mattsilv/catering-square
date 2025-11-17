# Archived Testing Scripts

⚠️ **WARNING: These scripts are NOT production-safe!**

These scripts were used during POC development and testing. They do NOT include duplicate prevention and should NEVER be used in production.

## Scripts in this folder:

1. **create_categories.py** - Creates categories without checking for duplicates
2. **create_menu_items.py** - Creates menu items without checking for duplicates
3. **add_missing_items.py** - Adds items without duplicate prevention
4. **fix_item_categories.py** - One-time fix for category associations
5. **update_location_names.py** - One-time update for location names
6. **analyze_menu.py** - Exploratory script for menu data
7. **check_catalog.py** - Early diagnostic script
8. **check_item_visibility.py** - Early diagnostic script

## Why are these archived?

These scripts were created during development to understand the Square API and test different approaches. They lack:
- Duplicate prevention
- Idempotency
- Production safety checks
- Error recovery

## For Production Use:

Use these scripts instead (in parent directory):
- **create_catalog_safe.py** - Production-safe catalog creation
- **catalog_utils.py** - Safe utility functions
- **cleanup_duplicates.py** - Remove duplicates if they occur

See `PRODUCTION_SAFETY.md` for complete guidelines.
