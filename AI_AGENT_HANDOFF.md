# AI Agent Handoff: Quick Start Guide

**Purpose:** Fast onboarding for AI coding agents to recreate this system on any e-commerce platform.

**Read first:** MASTER_CONTEXT.md (complete details)
**This doc:** Quick reference for starting immediately

---

## 🎯 What We're Building

**Online catering menu for Just Salad** with:
- Menu synced from public CDN (28 items, 6 categories)
- Images from CDN displayed on storefront
- Multi-location support (3 now, 50+ potential)
- SQLite tracks all platform IDs (source of truth)
- Hosted solution ($12-50/mo, no custom frontend)

---

## 📊 Critical Data Sources

### Menu Data (28 items)
```bash
GET https://cdn1.justsalad.com/public/menu.json

# Returns:
{
  "menu_items": [
    {
      "name": "Autumn Caesar",
      "category_id": 100,
      "description": "Roasted turkey, kale & romaine...",
      "image_url": "https://cdn.justsalad.com/images/...",
      "price": 15.00
    }
  ]
}
```

### Store Locations
```bash
GET https://cdn1.justsalad.com/public/store_locations.json

# Filter: amenities.catering === true
# Currently 3 catering locations
```

### Category Mapping
```
100 → Signature Salads
105 → Wraps
107 → Smoothies
110 → Snacks
115 → Beverages
120 → Build Your Own
```

---

## 🏗️ Architecture (Critical Patterns)

### 1. SQLite as Source of Truth
```sql
-- Track platform-generated IDs we don't control
locations (environment, platform_id, name, address, phone)
categories (environment, platform_id, name, description)
menu_items (environment, platform_id, name, category_id, price, image_id)
images (environment, platform_id, item_id, source_url, local_path)
sync_log (environment, action, platform_id, status, timestamp)
```

**Why:** Enables rollback, prevents duplicates, audit trail

### 2. Environment Isolation
```python
# .env structure
ACTIVE_ENVIRONMENT=sandbox  # or 'production'

SANDBOX_API_KEY=...
SANDBOX_API_SECRET=...

PRODUCTION_API_KEY=...
PRODUCTION_API_SECRET=...

# One-line switch between environments
```

**Why:** Test safely, prevent production accidents

### 3. Idempotent Operations
```python
def create_item(name, ...):
    # 1. Check database first
    existing = db.get_item(env, name)
    if existing: return existing

    # 2. Check platform API
    if platform_has_item(name):
        raise Error("Duplicate detected")

    # 3. Create with idempotency key
    id = api.create(name, idempotency_key=uuid4())

    # 4. Save to database
    db.save_item(env, id, name)
    return id
```

**Why:** Safe to re-run after failures

### 4. Image Pipeline
```python
def process_image(item_name, item_id, cdn_url, env):
    # 1. Download from CDN → local
    local_path = download(cdn_url, f"data/images/{item_name}.png")

    # 2. Upload to platform → get platform image ID
    image_id = platform_api.upload_image(local_path)

    # 3. Attach to item
    platform_api.attach_image(item_id, image_id)

    # 4. Track in database
    db.save_image(env, image_id, item_id, cdn_url, local_path)
```

**Why:** Preserves originals, tracks relationships, enables re-upload

---

## 📁 Project Structure (Non-Negotiable)

```
project/
├── scripts/              # User-facing workflows
│   ├── auth/test_auth.py
│   ├── catalog/create_catalog.py  # MAIN SCRIPT
│   └── maintenance/cleanup.py
├── src/                  # Importable utilities
│   ├── env_utils.py      # Environment management
│   ├── db_utils.py       # SQLite operations
│   ├── api_utils.py      # Platform API wrapper
│   ├── image_utils.py    # Image processing
│   └── menu_utils.py     # Just Salad CDN fetching
├── data/
│   ├── catalog.db        # SQLite database
│   ├── images/           # Downloaded images
│   └── *.json            # Exported backups
├── .env                  # Credentials (gitignored)
├── .env.example          # Template
└── README.md
```

**Why:** Clear separation, reusable utilities, standard Python structure

---

## 🚀 Implementation Phases (4 hours total)

### Phase 1: Project Setup (30 min)
```bash
# 1. Create structure
mkdir -p scripts/{auth,setup,catalog,maintenance} src data/images

# 2. Create .env
cat > .env << EOF
ACTIVE_ENVIRONMENT=sandbox
SANDBOX_API_KEY=your_sandbox_key
PRODUCTION_API_KEY=your_production_key
EOF

# 3. Install dependencies
pip install requests python-dotenv [platform-sdk]

# 4. Create env_utils.py
def get_credentials():
    env = os.getenv('ACTIVE_ENVIRONMENT', 'sandbox')
    return {
        'api_key': os.getenv(f'{env.upper()}_API_KEY'),
        'api_secret': os.getenv(f'{env.upper()}_API_SECRET')
    }

# 5. Create db_utils.py with schema (see MASTER_CONTEXT.md)
# 6. Run: init_database()
```

### Phase 2: Authentication (15 min)
```python
# scripts/auth/test_auth.py
import sys
sys.path.insert(0, 'src')
from env_utils import get_credentials

creds = get_credentials()
client = PlatformClient(**creds)

# Test: list locations
locations = client.locations.list()
print(f"✅ Found {len(locations)} locations")
```

### Phase 3: Categories (30 min)
```python
# src/api_utils.py
def create_category(client, name, description, idempotency_key):
    return client.catalog.create_category(
        name=name,
        description=description,
        idempotency_key=idempotency_key
    )

# scripts/catalog/create_categories.py
categories = [
    {'name': 'Signature Salads', 'description': '...'},
    {'name': 'Wraps', 'description': '...'},
    {'name': 'Build Your Own', 'description': '...'},
    {'name': 'Smoothies', 'description': '...'},
    {'name': 'Snacks', 'description': '...'},
    {'name': 'Beverages', 'description': '...'}
]

for cat in categories:
    # Check database
    existing = db.get_category(env, cat['name'])
    if existing: continue

    # Create
    cat_id = create_category(client, cat['name'], cat['description'], uuid4())

    # Save
    db.save_category(env, cat_id, cat['name'], cat['description'])
```

### Phase 4: Menu Items (1 hour)
```python
# src/menu_utils.py
def fetch_menu_items():
    r = requests.get('https://cdn1.justsalad.com/public/menu.json')
    return r.json()

def map_category(js_category_id):
    mapping = {100: 'Signature Salads', 105: 'Wraps', ...}
    return mapping.get(js_category_id)

# scripts/catalog/create_items.py
menu_data = fetch_menu_items()

for item in menu_data['menu_items']:
    # Check database
    existing = db.get_item(env, item['name'])
    if existing: continue

    # Get category
    category_name = map_category(item['category_id'])
    category_id = db.get_category(env, category_name)

    # Create
    item_id = create_item(
        client,
        name=item['name'],
        category_id=category_id,
        description=item['description'],
        price_cents=int(item['price'] * 100)
    )

    # Save
    db.save_item(env, item_id, item['name'], category_id, ...)
```

### Phase 5: Images (1 hour)
```python
# src/image_utils.py
def download_image(url, filename):
    r = requests.get(url)
    path = f"data/images/{filename}.png"
    with open(path, 'wb') as f:
        f.write(r.content)
    return path

def process_item_image(client, item_name, item_id, cdn_url, env):
    # Download
    local_path = download_image(cdn_url, item_name)

    # Upload
    with open(local_path, 'rb') as f:
        image_id = client.images.upload(file=f, name=item_name)

    # Attach
    client.items.attach_image(item_id, image_id)

    # Track
    db.save_image(env, image_id, item_id, cdn_url, local_path)

# In create_items.py loop:
if item.get('image_url'):
    process_item_image(client, item['name'], item_id, item['image_url'], env)
```

### Phase 6: Main Script (30 min)
```python
# scripts/catalog/create_catalog.py
def main():
    # Environment check
    if is_production():
        if input("⚠️  Production. Type 'yes': ") != 'yes':
            return

    # Init database
    db.init()

    # Pre-flight
    if check_duplicates(client):
        print("❌ Duplicates detected")
        return

    # Run workflow
    sync_locations()
    create_categories()
    create_items()
    process_images()

    # Export backup
    db.export_to_json(env)

    # Summary
    print(f"✅ Created:")
    print(f"   Categories: {db.count_categories(env)}")
    print(f"   Items: {db.count_items(env)}")
    print(f"   Images: {db.count_images(env)}")
```

---

## ✅ Validation Checklist

After implementation, verify:
- [ ] `python scripts/auth/test_auth.py` → ✅ Authentication works
- [ ] SQLite database created with all tables
- [ ] Can switch environments (change .env, test again)
- [ ] Categories created (6 total)
- [ ] Menu items created (start with 6 POC, then expand to 28)
- [ ] Images downloaded to data/images/
- [ ] Images uploaded and attached to items
- [ ] Database tracks all IDs
- [ ] Platform dashboard shows items with images
- [ ] Scripts are idempotent (can re-run safely)

---

## 🎓 Key Lessons (From Square POC)

### Do This
✅ Always test in sandbox first
✅ Check database before API calls
✅ Require explicit `yes` for production
✅ Mask credentials in logs
✅ Create audit trail (sync_log table)
✅ Download images locally (backup)
✅ Use idempotency keys

### Avoid This
❌ Skipping pre-flight duplicate checks
❌ Making production changes without confirmation
❌ Relying on platform API alone (use database)
❌ Hardcoding credentials
❌ Creating items without checking database first
❌ Assuming APIs work without testing

---

## 📋 Platform Evaluation (If Not Using Square)

### Must-Have Features
- [ ] Hosted solution (no custom frontend)
- [ ] API access (programmatic catalog management)
- [ ] Custom domain (white-label capable)
- [ ] Multi-location support (one site, all locations)
- [ ] $12-50/month cost range
- [ ] <3% transaction fees
- [ ] Image support

### Platforms to Consider
1. **Square Online** - $12/mo (Professional), 2.9%+$0.30 fees
2. **Shopify** - $39/mo (Basic), 2.9%+$0.30 fees, more features
3. **WooCommerce** - $15-30/mo (hosting), requires WordPress setup

### Decision Factors
- **Square:** Lowest cost, integrated POS, good for restaurants
- **Shopify:** More e-commerce features, better for scaling
- **WooCommerce:** Most flexible, highest technical complexity

---

## 🔧 Quick Commands Reference

```bash
# Test authentication
python scripts/auth/test_auth.py

# Create full catalog (sandbox)
python scripts/catalog/create_catalog.py

# Switch to production
# 1. Edit .env: ACTIVE_ENVIRONMENT=production
# 2. Test: python scripts/auth/test_auth.py
# 3. Deploy: python scripts/catalog/create_catalog.py

# Validate catalog
python scripts/catalog/validate_catalog.py

# View database
sqlite3 data/catalog.db "SELECT * FROM menu_items WHERE environment='sandbox';"

# Export backup
python -c "from src.db_utils import export_to_json; export_to_json('sandbox')"

# Cleanup duplicates
python scripts/maintenance/cleanup_duplicates.py
```

---

## 🆘 Common Issues & Solutions

### "Invalid API key"
→ Check `.env` has correct credentials for active environment
→ Verify not using sandbox key in production (or vice versa)

### "Item already exists"
→ Check database first: `db.get_item(env, name)`
→ Run pre-flight: `check_duplicates(client)`

### "Image upload failed"
→ Verify image URL is accessible (try wget)
→ Check file size < platform limit (usually 5-10MB)
→ Ensure correct MIME type (PNG, JPG, JPEG)

### "Location not found"
→ Run: `python scripts/auth/list_locations.py`
→ Update location IDs in database

---

## 📞 Support Resources

- **Just Salad Data:** https://cdn1.justsalad.com/public/
- **Square Docs:** https://developer.squareup.com/docs
- **Shopify Docs:** https://shopify.dev/docs
- **This POC:** MASTER_CONTEXT.md (complete details)

---

## 🎯 Success Criteria

**POC is complete when:**
- [x] 6 categories created
- [x] 6 menu items created (1 per category)
- [x] 4 images uploaded and attached
- [x] SQLite database tracks all IDs
- [x] Scripts are idempotent
- [ ] Deployed to production
- [ ] Hosted storefront live with custom domain

**Full system complete when:**
- [ ] All 28 menu items synced
- [ ] Modifiers added (Build Your Own)
- [ ] Order minimums configured (10 items)
- [ ] Automated CDN sync (daily/weekly)
- [ ] Customer ordering works end-to-end

---

**Quick Start:** Read this doc, then implement Phases 1-6 (4 hours). Test thoroughly in sandbox before production.

**Full Context:** See MASTER_CONTEXT.md for complete architectural details, lessons learned, and platform comparison.
