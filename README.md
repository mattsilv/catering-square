# Square Catering Menu POC

Production-ready system for managing Just Salad catering menu in Square with SQLite tracking.

## 📁 Project Structure

```
catering-square/
├── scripts/              # Executable scripts
│   ├── auth/            # Authentication & verification
│   ├── setup/           # Initial setup scripts
│   ├── catalog/         # Catalog management (main scripts)
│   └── maintenance/     # Cleanup & maintenance
├── src/                 # Core utilities (importable modules)
├── data/                # Data files & SQLite database
│   ├── square_catalog.db       # SQLite tracking (source of truth)
│   ├── category_ids.json       # Exported category mappings
│   ├── menu_item_ids.json      # Exported menu item mappings
│   └── images/                 # Downloaded menu images
├── docs/                # Additional documentation
├── archive/             # Legacy scripts (not production-safe)
└── tests/               # Test files (future)
```

## 🚀 Quick Start

### 1. Setup Environment
```bash
source ~/.venv/bin/activate
uv pip install squareup python-dotenv
```

### 2. Test Authentication
```bash
python scripts/auth/test_auth.py
```

### 3. Create Complete Catalog (Production-Safe)
```bash
python scripts/catalog/create_catalog_with_images.py
```

### 4. Validate Setup
```bash
python scripts/catalog/validate_poc.py
```

### 5. Verify in Dashboard
- Sandbox: https://app.squareupsandbox.com/dashboard/items/library

## 🔧 Key Scripts

### Authentication & Setup
- **scripts/auth/test_auth.py** - Verify Square API credentials
- **scripts/auth/list_locations.py** - List all Square locations
- **scripts/setup/create_test_locations.py** - Create test locations

### Catalog Management
- **scripts/catalog/create_catalog_with_images.py** ⭐ **PRIMARY SCRIPT** - Complete workflow with images & SQLite tracking
- **scripts/catalog/create_catalog_safe.py** - Catalog creation without images
- **scripts/catalog/validate_poc.py** - Validate catalog structure

### Maintenance
- **scripts/maintenance/cleanup_duplicates.py** - Remove duplicate items/categories
- **scripts/maintenance/delete_duplicates.py** - Delete specific duplicates

### Core Utilities (src/)
- **catalog_utils.py** - Safe catalog operations with duplicate prevention
- **db_utils.py** - SQLite database utilities (source of truth for IDs)
- **image_utils.py** - Image download & upload to Square
- **store_utils.py** - Store naming conventions

## 🛡️ Safety Features

### Multi-Layer Protection
1. **SQLite Database** - Tracks all Square IDs across sandbox + production
2. **Pre-flight Checks** - Scans for duplicates before operations
3. **Idempotency Keys** - Prevents duplicate API requests
4. **Database Audit Trail** - sync_log table tracks all operations

### Production Safeguards
- All scripts check for existing items before creating
- Database prevents duplicate tracking
- Safe to run scripts multiple times (idempotent)

## 📊 Data Management

### SQLite Database (data/square_catalog.db)
Single source of truth for Square catalog IDs:
- Tracks sandbox AND production environments
- Tables: locations, categories, menu_items, images, item_variations, sync_log
- Exports to JSON for backward compatibility

### View Database Contents
```bash
python src/db_utils.py
```

## 📋 Configuration

### Environment Variables (.env)
```bash
SQUARE_ACCESS_TOKEN=your_token_here
SQUARE_ENVIRONMENT=sandbox  # or production
```

See `.env.example` for template.

## 📚 Documentation

### Quick Start Guides
- **README.md** (this file) - Project overview and quick start
- **POC_SUMMARY.md** - Current implementation status & results
- **PRODUCTION_DEPLOYMENT.md** - Complete production deployment guide

### Platform Migration/Replication
- **MASTER_CONTEXT.md** - Complete system documentation (platform-agnostic)
- **AI_AGENT_HANDOFF.md** - Quick start guide for AI agents
- Use these to recreate this system on Shopify, WooCommerce, etc.

### Reference Documentation
- **PRODUCTION_SAFETY.md** - Critical production safety guidelines
- **CLAUDE.md** - Development workflow and instructions
- **docs/** - Detailed specifications:
  - `business-rules.md` - Business logic and requirements
  - `data-models.md` - Database schema and data structures
  - `menu-structure.md` - Just Salad menu organization
  - `public-data-endpoints.md` - API endpoints reference
  - `square-integration.md` - Square-specific implementation details

## ⚠️ Important Notes

- **Archive folder** contains old scripts - NOT production-safe
- **Always use scripts from scripts/ directory** for production operations
- **Database is source of truth** - JSON files are exported for backward compatibility
- **Test in sandbox first** before any production operations
