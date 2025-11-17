# Master Context: Just Salad Catering Menu Management System

**Purpose:** Complete context document for recreating this catering menu management system on any e-commerce platform (Square, Shopify, etc.)

**Use Case:** Hand this to an AI coding agent to build the same system from scratch.

---

## 🎯 Business Goals

### Primary Objective
Create an online ordering system for **Just Salad catering** that:
- Displays menu items with images, descriptions, and prices
- Allows customers to browse and order catering items
- Syncs menu data from Just Salad's public CDN
- Tracks all platform IDs in local database (source of truth)
- Supports multiple locations (currently 3, potentially 50+)
- **Avoids building custom frontend** (use hosted e-commerce solution)

### Success Criteria
- ✅ Menu items appear online with images
- ✅ Customers can place catering orders
- ✅ $12/month or less for hosting (prefer out-of-the-box solution)
- ✅ Custom domain with branding (no "powered by X" visible)
- ✅ Multi-location support (one site, all locations)
- ✅ Easy to add/update menu items programmatically

---

## 📊 Data Sources (Public APIs)

### 1. Just Salad Menu Data
**Endpoint:** `https://cdn1.justsalad.com/public/menu.json`

**Response Structure:**
```json
{
  "menu_items": [
    {
      "id": 4021,
      "name": "Autumn Caesar",
      "category_id": 100,
      "description": "Roasted turkey, kale & romaine, fall veggies...",
      "image_url": "https://cdn.justsalad.com/images/menu/autumn-caesar.png",
      "price": 15.00,
      "available": true,
      "nutrition": { ... },
      "allergens": ["dairy", "gluten"]
    }
  ],
  "total_items": 28
}
```

**Key Fields:**
- `name` - Item name (e.g., "Autumn Caesar")
- `description` - Full menu description
- `image_url` - CDN link to item image
- `category_id` - Maps to categories (100=Salads, 105=Wraps, etc.)
- `price` - Pricing in USD

**Category Mapping:**
```
100 → Signature Salads
105 → Wraps
107 → Smoothies
110 → Snacks
115 → Beverages
120 → Build Your Own
```

### 2. Just Salad Store Locations
**Endpoint:** `https://cdn1.justsalad.com/public/store_locations.json`

**Response Structure:**
```json
{
  "locations": [
    {
      "id": 663,
      "name": "Midtown East - Lexington",
      "address": {
        "street": "663 Lexington Ave",
        "city": "New York",
        "state": "NY",
        "zip": "10022"
      },
      "phone": "(212) 555-1234",
      "amenities": {
        "catering": true,
        "delivery": true,
        "pickup": true
      },
      "hours": { ... }
    }
  ]
}
```

**Catering Locations:** Filter by `amenities.catering === true`

---

## 🏗️ Architecture Patterns (Platform-Agnostic)

### Pattern 1: SQLite as Source of Truth

**Why:** E-commerce platforms generate IDs we don't control. SQLite tracks the mapping.

**Schema:**
```sql
-- Track locations across environments
CREATE TABLE locations (
    id INTEGER PRIMARY KEY,
    environment TEXT NOT NULL,      -- 'sandbox' or 'production'
    platform_id TEXT NOT NULL,      -- Square/Shopify location ID
    name TEXT NOT NULL,
    address TEXT,
    phone TEXT,
    created_at TIMESTAMP,
    UNIQUE(environment, platform_id)
);

-- Track categories
CREATE TABLE categories (
    id INTEGER PRIMARY KEY,
    environment TEXT NOT NULL,
    platform_id TEXT NOT NULL,      -- Platform category ID
    name TEXT NOT NULL,
    description TEXT,
    created_at TIMESTAMP,
    UNIQUE(environment, platform_id)
);

-- Track menu items
CREATE TABLE menu_items (
    id INTEGER PRIMARY KEY,
    environment TEXT NOT NULL,
    platform_id TEXT NOT NULL,      -- Platform item ID
    name TEXT NOT NULL,
    category_platform_id TEXT,      -- Links to categories table
    description TEXT,
    price_cents INTEGER,
    image_platform_id TEXT,         -- Platform image ID
    source_url TEXT,                -- Original Just Salad image URL
    created_at TIMESTAMP,
    UNIQUE(environment, platform_id)
);

-- Track images
CREATE TABLE images (
    id INTEGER PRIMARY KEY,
    environment TEXT NOT NULL,
    platform_id TEXT NOT NULL,
    item_platform_id TEXT,
    source_url TEXT,
    local_path TEXT,                -- Downloaded image path
    created_at TIMESTAMP
);

-- Audit trail
CREATE TABLE sync_log (
    id INTEGER PRIMARY KEY,
    environment TEXT,
    action TEXT,                     -- 'create_category', 'create_item', etc.
    platform_id TEXT,
    status TEXT,                     -- 'success', 'error'
    error_message TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Benefits:**
- Single source of truth for all IDs
- Tracks sandbox AND production separately
- Enables rollback (know what was created)
- Audit trail for debugging

### Pattern 2: Idempotent Operations

**Principle:** Scripts can be run multiple times safely.

**Implementation:**
```python
def create_category(name, description):
    # 1. Check database first
    existing_id = get_category_by_name(environment, name)
    if existing_id:
        print(f"→ Already exists: {name} ({existing_id})")
        return existing_id

    # 2. Check platform API (pre-flight)
    duplicates = check_platform_for_duplicates(name)
    if duplicates:
        raise Error("Duplicate detected - cleanup required")

    # 3. Create with idempotency key
    idempotency_key = uuid.uuid4()
    platform_id = platform_api.create_category(
        name=name,
        description=description,
        idempotency_key=idempotency_key
    )

    # 4. Save to database
    save_category(environment, platform_id, name, description)

    return platform_id
```

**Benefits:**
- Safe to re-run scripts
- Prevents duplicates
- Graceful error recovery

### Pattern 3: Environment Isolation

**Environments:**
- **Sandbox/Test:** Safe testing without affecting real data
- **Production:** Live customer-facing system

**Implementation:**
```python
# .env file structure
ACTIVE_ENVIRONMENT=sandbox  # or 'production'

# Sandbox credentials
SANDBOX_API_KEY=...
SANDBOX_API_SECRET=...

# Production credentials
PRODUCTION_API_KEY=...
PRODUCTION_API_SECRET=...

# Helper function
def get_credentials():
    env = os.getenv('ACTIVE_ENVIRONMENT', 'sandbox')
    if env == 'production':
        return {
            'api_key': os.getenv('PRODUCTION_API_KEY'),
            'api_secret': os.getenv('PRODUCTION_API_SECRET')
        }
    else:
        return {
            'api_key': os.getenv('SANDBOX_API_KEY'),
            'api_secret': os.getenv('SANDBOX_API_SECRET')
        }
```

**Benefits:**
- Test everything in sandbox first
- One-line switch to production
- Prevents accidental production changes

### Pattern 4: Image Handling Pipeline

**Flow:**
```
1. Download from CDN → local storage
2. Upload to platform → get platform image ID
3. Attach to menu item → update database
4. Track in database → audit trail
```

**Implementation:**
```python
def process_item_image(item_name, item_id, image_url, environment):
    # 1. Download image
    local_path = download_image(image_url, item_name)

    # 2. Upload to platform
    with open(local_path, 'rb') as f:
        image_id = platform_api.upload_image(
            file=f,
            name=f"{item_name}_image"
        )

    # 3. Attach to item
    platform_api.attach_image_to_item(
        item_id=item_id,
        image_id=image_id
    )

    # 4. Track in database
    save_image(
        environment=environment,
        platform_id=image_id,
        item_platform_id=item_id,
        source_url=image_url,
        local_path=local_path
    )

    return image_id
```

**Benefits:**
- Preserves original images locally (backup)
- Tracks image-to-item relationships
- Can re-upload if platform deletes

---

## 📁 Project Structure (Best Practices)

```
project-root/
├── scripts/              # Executable scripts (main workflows)
│   ├── auth/            # Authentication testing
│   │   ├── test_auth.py
│   │   └── list_locations.py
│   ├── setup/           # Initial setup (one-time)
│   │   └── create_locations.py
│   ├── catalog/         # Catalog management (main workflows)
│   │   ├── create_catalog.py         # Main deployment script
│   │   ├── validate_catalog.py       # Verify setup
│   │   └── sync_menu_from_cdn.py     # Update from Just Salad
│   └── maintenance/     # Cleanup & fixes
│       ├── cleanup_duplicates.py
│       └── rollback.py
├── src/                 # Core utilities (importable modules)
│   ├── __init__.py
│   ├── env_utils.py     # Environment/credential management
│   ├── db_utils.py      # SQLite database operations
│   ├── api_utils.py     # Platform API wrapper functions
│   ├── image_utils.py   # Image download/upload
│   └── menu_utils.py    # Just Salad CDN data fetching
├── data/                # Data files
│   ├── catalog.db       # SQLite database (source of truth)
│   ├── images/          # Downloaded menu images
│   ├── category_ids.json  # Exported mappings (backup)
│   └── menu_item_ids.json # Exported mappings (backup)
├── docs/                # Documentation
│   ├── api-reference.md
│   ├── deployment.md
│   └── architecture.md
├── .env                 # Environment config (DO NOT COMMIT)
├── .env.example         # Example config template
├── .gitignore           # Git ignore patterns
├── requirements.txt     # Python dependencies
└── README.md            # Quick start guide
```

**Key Principles:**
- **scripts/** = User runs these (workflows)
- **src/** = Code imports these (libraries)
- **data/** = Generated/downloaded files
- **One main script** = `scripts/catalog/create_catalog.py` does full deployment

---

## 🔧 Core Utilities (src/ modules)

### env_utils.py - Environment Management
```python
"""
Purpose: Flexible sandbox/production credential switching
Related: All scripts
Refactor if: Supporting >2 environments OR multi-region
"""

def get_environment():
    """Returns 'sandbox' or 'production'"""

def get_api_credentials():
    """Returns correct credentials for active environment"""

def is_production():
    """Safety check before destructive operations"""

def print_environment_info():
    """Show current environment, credentials (masked), dashboard URL"""
```

### db_utils.py - SQLite Operations
```python
"""
Purpose: SQLite database as single source of truth for platform IDs
Related: All catalog scripts
Refactor if: >500 lines OR handling unrelated database operations
"""

def init_database():
    """Create tables if not exist"""

def save_category(environment, platform_id, name, description):
    """Insert or update category"""

def save_menu_item(environment, platform_id, name, category_id, price, ...):
    """Insert or update menu item"""

def get_category_by_name(environment, name):
    """Lookup category platform ID by name"""

def get_all_items(environment):
    """Get all items for environment"""

def export_to_json(environment, output_dir='data'):
    """Export database to JSON files (backup)"""
```

### api_utils.py - Platform API Wrapper
```python
"""
Purpose: Abstraction layer for e-commerce platform API
Related: All catalog scripts
Refactor if: Switching to different platform OR >10 API methods
"""

def create_category(client, name, description, idempotency_key):
    """Create category on platform"""

def create_item(client, name, category_id, description, price, ...):
    """Create menu item on platform"""

def upload_image(client, file_path, name):
    """Upload image to platform"""

def attach_image_to_item(client, item_id, image_id):
    """Link image to menu item"""

def check_for_duplicates(client):
    """Pre-flight check: scan for duplicate items/categories"""
```

### image_utils.py - Image Processing
```python
"""
Purpose: Download images from CDN, upload to platform
Related: api_utils.py, db_utils.py
Refactor if: >400 lines OR handling multiple image sources
"""

def download_image(url, filename, output_dir='data/images'):
    """Download image from Just Salad CDN"""

def upload_image_to_platform(client, local_path, item_name):
    """Upload image to platform, return platform image ID"""

def process_item_image(client, item_name, item_id, image_url, environment):
    """Full pipeline: download → upload → attach → track"""
```

### menu_utils.py - Just Salad Data
```python
"""
Purpose: Fetch and parse Just Salad CDN data
Related: create_catalog.py
Refactor if: Menu data structure changes OR multiple data sources
"""

def fetch_menu_items():
    """GET https://cdn1.justsalad.com/public/menu.json"""

def fetch_locations():
    """GET https://cdn1.justsalad.com/public/store_locations.json"""

def filter_catering_locations(locations):
    """Return only locations with amenities.catering === true"""

def map_category_id_to_name(category_id):
    """Convert Just Salad category ID to standard name"""
```

---

## 🚀 Main Deployment Script

**File:** `scripts/catalog/create_catalog.py`

**Purpose:** Complete catalog deployment (locations → categories → items → images)

**Workflow:**
```python
def create_catalog():
    # 0. Environment check
    print_environment_info()
    if is_production():
        confirm = input("⚠️  Production mode. Type 'yes' to continue: ")
        if confirm != 'yes':
            return

    # 1. Initialize database
    init_database()

    # 2. Pre-flight check (no duplicates)
    duplicates = check_for_duplicates(client)
    if duplicates:
        print("❌ Duplicates detected - run cleanup first")
        return

    # 3. Sync locations to database
    locations = platform_api.list_locations()
    for loc in locations:
        save_location(environment, loc.id, loc.name, loc.address, loc.phone)

    # 4. Create categories
    categories = [
        {'name': 'Signature Salads', 'description': '...'},
        {'name': 'Wraps', 'description': '...'},
        {'name': 'Build Your Own', 'description': '...'},
        {'name': 'Smoothies', 'description': '...'},
        {'name': 'Snacks', 'description': '...'},
        {'name': 'Beverages', 'description': '...'}
    ]

    for cat in categories:
        # Check database first
        existing_id = get_category_by_name(environment, cat['name'])
        if existing_id:
            continue

        # Create on platform
        cat_id = create_category(client, cat['name'], cat['description'])

        # Save to database
        save_category(environment, cat_id, cat['name'], cat['description'])

    # 5. Fetch Just Salad menu data
    menu_data = fetch_menu_items()

    # 6. Create menu items
    for menu_item in menu_data['menu_items']:
        # Check database
        existing_id = get_item_by_name(environment, menu_item['name'])
        if existing_id:
            continue

        # Get category ID
        category_name = map_category_id_to_name(menu_item['category_id'])
        category_id = get_category_by_name(environment, category_name)

        # Create on platform
        item_id = create_item(
            client,
            name=menu_item['name'],
            category_id=category_id,
            description=menu_item['description'],
            price_cents=int(menu_item['price'] * 100)
        )

        # Save to database
        save_menu_item(
            environment=environment,
            platform_id=item_id,
            name=menu_item['name'],
            category_platform_id=category_id,
            price_cents=int(menu_item['price'] * 100),
            source_url=menu_item.get('image_url')
        )

        # Process image if available
        if menu_item.get('image_url'):
            process_item_image(
                client,
                menu_item['name'],
                item_id,
                menu_item['image_url'],
                environment
            )

    # 7. Export to JSON (backup)
    export_to_json(environment)

    # 8. Display summary
    show_summary(environment)
```

---

## 📋 Platform Requirements Checklist

**When evaluating Shopify, WooCommerce, or other platforms:**

### Must-Have Features
- [ ] **Hosted solution** - Don't build custom frontend
- [ ] **API access** - Programmatic catalog management
- [ ] **Custom domain** - White-label (remove platform branding)
- [ ] **Multi-location support** - One site, multiple pickup/delivery locations
- [ ] **Image support** - Display menu item images
- [ ] **Pricing flexibility** - $12-50/month acceptable
- [ ] **Category/collection support** - Organize items by category
- [ ] **Order management** - View/manage customer orders
- [ ] **Transaction fees** - <3% online (Square is 2.9% + $0.30)

### Nice-to-Have Features
- [ ] **Sandbox/test mode** - Test before production
- [ ] **Order minimums** - Enforce 10-item catering minimum
- [ ] **Modifiers/variants** - Build-your-own with toppings
- [ ] **Inventory tracking** - Track item availability by location
- [ ] **Customer accounts** - Order history, reordering
- [ ] **Mobile app** - POS for in-person orders
- [ ] **Analytics** - Order insights, popular items

### Deal-Breakers (Avoid)
- ❌ **Per-location fees** - Should be per-account, not per-location
- ❌ **Transaction lock-in** - Must process through their payment gateway
- ❌ **No API access** - Need programmatic catalog updates
- ❌ **High monthly costs** - >$100/month not justified for 50 locations

---

## 🎓 Key Lessons Learned (Square POC)

### What Worked Well
1. **SQLite as source of truth** - Invaluable for tracking IDs
2. **Environment isolation** - Sandbox testing saved us from production errors
3. **Idempotent scripts** - Could re-run safely after failures
4. **Image pipeline** - Download → Upload → Attach worked smoothly
5. **Pre-flight duplicate checks** - Caught issues before creating data
6. **API wrapper functions** - Abstracted platform-specific logic
7. **Audit trail** - sync_log table helped debug issues

### Challenges Encountered
1. **No sandbox for Square Online** - Had to use free plan to preview
2. **API method discovery** - SDK documentation wasn't always clear
3. **Image upload complexity** - Required multipart/form-data, not simple POST
4. **Variation requirements** - Square requires ≥1 variation per item (even if not needed)
5. **Catalog list API unreliable** - Had to use search instead

### Best Practices Established
1. **Always test in sandbox first** - Never skip this step
2. **Database before API** - Check database before making API calls
3. **Explicit confirmations** - Require `yes` input for production
4. **Masked credentials** - Never print full tokens in logs
5. **Descriptive error messages** - Help future debugging
6. **Version control .env.example** - But never commit .env

---

## 📊 Current Status (Square POC)

### What Was Built
- ✅ 3 sandbox locations created
- ✅ 6 categories (Signature Salads, Wraps, Build Your Own, Smoothies, Snacks, Beverages)
- ✅ 6 menu items with real Just Salad data
- ✅ 4 images downloaded and uploaded
- ✅ SQLite database tracking all IDs
- ✅ Production credentials configured (not deployed yet)
- ✅ Complete deployment guide written

### Data Tracked in Database
```sql
-- Sandbox environment
Locations: 3
Categories: 6
Menu Items: 6
Images: 4

-- Production environment
Not deployed yet (credentials ready)
```

### Scripts Created
- `scripts/auth/test_auth.py` - Test authentication
- `scripts/auth/list_locations.py` - List all locations
- `scripts/auth/test_production_setup.py` - Validate production (read-only)
- `scripts/setup/create_test_locations.py` - Create locations
- `scripts/catalog/create_catalog_with_images.py` - **Main deployment script**
- `scripts/catalog/validate_poc.py` - Validate catalog structure
- `scripts/catalog/create_payment_links.py` - Generate payment links
- `scripts/maintenance/cleanup_duplicates.py` - Remove duplicates
- `scripts/maintenance/delete_duplicates.py` - Delete specific items

### Files & Docs
- `data/square_catalog.db` (60KB) - SQLite database
- `data/images/` - 4 menu images (2.5MB)
- `data/category_ids.json` - Category mappings (exported)
- `data/menu_item_ids.json` - Menu item mappings (exported)
- `PRODUCTION_DEPLOYMENT.md` - Complete deployment guide
- `PRODUCTION_SAFETY.md` - Production safety guidelines
- `POC_SUMMARY.md` - POC results summary
- `README.md` - Quick start guide

---

## 🔄 Recreating This System (New Platform Guide)

### Phase 1: Project Setup (30 min)
1. Create project structure (scripts/, src/, data/)
2. Set up .env with sandbox/production credentials
3. Install dependencies (requests, python-dotenv, platform SDK)
4. Create `src/env_utils.py` (environment management)
5. Create `src/db_utils.py` (SQLite operations)
6. Initialize database: `init_database()`

### Phase 2: Authentication (15 min)
1. Create `scripts/auth/test_auth.py`
2. Test sandbox credentials work
3. Verify can list locations
4. Document platform dashboard URLs

### Phase 3: Location Setup (30 min)
1. Fetch Just Salad locations: `https://cdn1.justsalad.com/public/store_locations.json`
2. Filter catering locations: `amenities.catering === true`
3. Create locations on platform (or use existing)
4. Save to database: `save_location()`
5. Verify in platform dashboard

### Phase 4: Category Creation (45 min)
1. Create `src/api_utils.py` with `create_category()`
2. Define 6 categories (see data sources section)
3. Implement duplicate checking
4. Create script: `scripts/catalog/create_categories.py`
5. Test in sandbox
6. Verify in database and platform dashboard

### Phase 5: Menu Items (1 hour)
1. Fetch menu data: `https://cdn1.justsalad.com/public/menu.json`
2. Create `src/menu_utils.py` for data parsing
3. Map Just Salad category IDs to platform categories
4. Implement `create_item()` in api_utils.py
5. Create POC: 6 items (1 per category)
6. Test in sandbox
7. Verify in database

### Phase 6: Image Pipeline (1 hour)
1. Create `src/image_utils.py`
2. Implement `download_image()` from CDN
3. Implement `upload_image_to_platform()`
4. Implement `attach_image_to_item()`
5. Test with 4 items that have images
6. Verify images appear in platform

### Phase 7: Main Deployment Script (1 hour)
1. Create `scripts/catalog/create_catalog.py`
2. Combine all workflows: locations → categories → items → images
3. Add production safety checks
4. Add progress logging
5. Test complete workflow in sandbox

### Phase 8: Validation & Cleanup (30 min)
1. Create `scripts/catalog/validate_catalog.py`
2. Create `scripts/maintenance/cleanup_duplicates.py`
3. Test rollback procedures
4. Document success criteria

### Phase 9: Production Deployment (30 min)
1. Write `PRODUCTION_DEPLOYMENT.md`
2. Test production credentials (read-only)
3. Deploy to production (with approval)
4. Verify in production dashboard
5. Enable hosted storefront (if applicable)

### Phase 10: Post-Deployment (ongoing)
1. Expand to all 28 menu items
2. Add modifiers/variants (Build Your Own)
3. Set up automated CDN syncs
4. Configure order minimums
5. Train staff

---

## 💰 Cost Comparison (For Reference)

### Square Online
- **Free:** $0/mo (Square branding, square.site subdomain)
- **Professional:** $12/mo (custom domain, no branding)
- **Performance:** $26/mo (cart recovery, reviews)
- **Premium:** $72/mo (lower transaction fees)
- **Transaction fees:** 2.9% + $0.30 online, 2.6% + $0.15 in-person
- **Multi-location:** No per-location fee (one site, all locations)

### Shopify (For Comparison)
- **Basic:** $39/mo (custom domain, unlimited products)
- **Shopify:** $105/mo (professional reports, lower fees)
- **Advanced:** $399/mo (advanced reports, lowest fees)
- **Transaction fees:** 2.9% + $0.30 (with Shopify Payments)
- **Multi-location:** No per-location fee

### WooCommerce (WordPress)
- **Hosting:** $10-30/mo (varies by host)
- **WooCommerce:** Free plugin
- **Transaction fees:** Varies by payment gateway (Stripe: 2.9% + $0.30)
- **Multi-location:** Requires plugins ($50-200/yr)
- **Requires:** More technical setup than Square/Shopify

---

## 🎯 Next Steps (Platform Evaluation)

### Evaluate Shopify
- [ ] Create Shopify account
- [ ] Test product creation via API
- [ ] Check multi-location support
- [ ] Verify custom domain capabilities
- [ ] Test hosted checkout
- [ ] Compare transaction fees

### Evaluate WooCommerce
- [ ] Set up WordPress + WooCommerce
- [ ] Test REST API access
- [ ] Check multi-location plugins
- [ ] Estimate total cost (hosting + plugins)
- [ ] Assess technical complexity

### Decision Criteria
| Feature | Square | Shopify | WooCommerce |
|---------|--------|---------|-------------|
| Monthly Cost | $12 | $39 | $15-30 |
| Transaction Fee | 2.9%+$0.30 | 2.9%+$0.30 | 2.9%+$0.30 |
| Setup Time | Low | Low | Medium |
| API Access | ✅ | ✅ | ✅ |
| Multi-location | ✅ | ✅ | Plugin |
| Custom Domain | ✅ | ✅ | ✅ |
| Hosted Solution | ✅ | ✅ | Need hosting |

**Recommendation:** Start with lowest-cost hosted solution (Square $12/mo), expand later if needed.

---

## 📝 Template: AI Agent Prompt

**When handing this to a new AI agent:**

```
Build a catering menu management system using [PLATFORM_NAME].

Context: Read MASTER_CONTEXT.md completely first.

Requirements:
1. Fetch menu data from: https://cdn1.justsalad.com/public/menu.json
2. Fetch locations from: https://cdn1.justsalad.com/public/store_locations.json
3. Create SQLite database to track all platform IDs
4. Support sandbox and production environments
5. Implement idempotent operations (safe to re-run)
6. Download and upload menu images
7. Create 6 categories, 28 menu items
8. Use project structure from MASTER_CONTEXT.md

Follow patterns documented in MASTER_CONTEXT.md for:
- Database schema (SQLite)
- Environment management (.env structure)
- API wrapper functions (src/api_utils.py)
- Image processing pipeline
- Main deployment script

Start with Phase 1 (Project Setup) and progress through Phase 10.
```

---

## 🔗 Reference URLs

### Just Salad Public Data
- **Menu:** https://cdn1.justsalad.com/public/menu.json
- **Locations:** https://cdn1.justsalad.com/public/store_locations.json
- **Image CDN:** https://cdn.justsalad.com/images/menu/

### Current Implementation (Square)
- **Dashboard (Sandbox):** https://app.squareupsandbox.com/dashboard
- **Dashboard (Production):** https://squareup.com/dashboard
- **Developer Docs:** https://developer.squareup.com/docs
- **GitHub:** (Not public - local project)

---

**Document Version:** 1.0
**Last Updated:** 2025-11-17
**Author:** Claude (AI Agent)
**Purpose:** Complete handoff document for recreating system on any platform
