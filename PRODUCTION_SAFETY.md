# Production Safety Guidelines

## Critical: Preventing Duplicates in Production

### The Problem
Running catalog creation scripts multiple times can create duplicate items and categories in Square, which is unacceptable in production.

### The Solution: Three-Layer Protection

#### Layer 1: Local State Files (PRIMARY)
- `category_ids.json` - Source of truth for category mappings
- `menu_item_ids.json` - Source of truth for menu item mappings

**Rule:** Always check these files FIRST before creating anything.

#### Layer 2: API Duplicate Detection (SECONDARY)
- Use `catalog_utils.get_existing_catalog_items()` to check Square API
- Use `catalog_utils.check_for_duplicates()` before any batch operations

#### Layer 3: Idempotency Keys (TERTIARY)
- Always use unique UUID-based idempotency keys for all catalog operations
- Square will reject duplicate requests with the same idempotency key within 24 hours

### Production-Safe Scripts

#### ✅ SAFE FOR PRODUCTION
1. **create_catalog_safe.py** - Idempotent catalog creation with duplicate prevention
2. **cleanup_duplicates.py** - Find and remove duplicates
3. **delete_duplicates.py** - Delete duplicate items by name
4. **catalog_utils.py** - Utility functions with built-in safety checks

#### ⚠️ NOT SAFE FOR PRODUCTION (Testing Only)
1. **create_categories.py** - No duplicate checking
2. **create_menu_items.py** - No duplicate checking
3. **add_missing_items.py** - No duplicate checking

### Pre-Deployment Checklist

Before running ANY catalog script in production:

- [ ] Check `category_ids.json` and `menu_item_ids.json` exist and are up-to-date
- [ ] Run `check_for_duplicates()` to verify no existing duplicates
- [ ] Use `create_catalog_safe.py` instead of individual create scripts
- [ ] Test in sandbox first with same data
- [ ] Have rollback plan ready (save backup of JSON files)
- [ ] Monitor Square Dashboard after deployment

### Example: Safe Production Workflow

```bash
# 1. Backup existing state
cp category_ids.json category_ids.backup.json
cp menu_item_ids.json menu_item_ids.backup.json

# 2. Check for duplicates FIRST
python -c "
from catalog_utils import check_for_duplicates
from square import Square
from square.client import SquareEnvironment
import os
from dotenv import load_dotenv

load_dotenv()
client = Square(token=os.getenv('SQUARE_ACCESS_TOKEN'),
                environment=SquareEnvironment.PRODUCTION)

dups = check_for_duplicates(client)
if dups['items'] or dups['categories']:
    print('❌ DUPLICATES FOUND - DO NOT PROCEED')
    exit(1)
print('✅ Safe to proceed')
"

# 3. Run production-safe script
python create_catalog_safe.py

# 4. Verify in Square Dashboard
# https://squareup.com/dashboard/items/library
```

### Rollback Procedure

If duplicates are created:

```bash
# 1. Restore backup JSON files
cp category_ids.backup.json category_ids.json
cp menu_item_ids.backup.json menu_item_ids.json

# 2. Run cleanup
python cleanup_duplicates.py

# 3. Verify cleanup
python -c "from catalog_utils import check_for_duplicates; ..."
```

### Key Principles

1. **Idempotency First** - All scripts must be safe to run multiple times
2. **Check Before Create** - Always verify item doesn't exist before creating
3. **Local State Truth** - JSON files are the source of truth, not the API
4. **Atomic Operations** - Use batch operations where possible
5. **Verify After Changes** - Always check Square Dashboard after deployment

### Square API Limitations (As of Jan 2025)

- `catalog.list()` doesn't reliably return all items/categories
- Categories can't be directly searched - must be inferred from items
- No built-in duplicate prevention in the API
- Idempotency keys only work for 24 hours

Therefore, **we must implement our own duplicate prevention**.
