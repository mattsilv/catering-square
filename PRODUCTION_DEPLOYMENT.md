# Production Deployment Guide

**⚠️ CRITICAL:** This guide walks through deploying your Just Salad catering menu to production Square.

## Pre-Deployment Checklist

### ✅ Sandbox Testing Complete

- [ ] All 6 POC menu items created in sandbox
- [ ] Images uploaded and displaying correctly
- [ ] Database tracking working (data/square_catalog.db)
- [ ] Validation script passes (`python scripts/catalog/validate_poc.py`)
- [ ] Square Online free plan tested (optional)

### ✅ Production Credentials Ready

- [ ] Production Square access token obtained
- [ ] Production app ID documented
- [ ] Main production location ID identified (663 Lexington Ave)
- [ ] Backup of .env file created

### ✅ Stakeholder Approval

- [ ] Menu items reviewed and approved
- [ ] Pricing confirmed ($15.00 for POC items)
- [ ] Images approved
- [ ] Go-live date confirmed

---

## Step 1: Verify Production Credentials

Your `.env` file already has production credentials:

```bash
PRODUCTION_APP_ID=sq0idp-elZiQswW79_tUgRb0d2v-g
PRODUCTION_ACCESS_TOKEN=EAAAl1UqsXQqoB5MXjz7PMF-o_yPPn6M1PQAV3X6nz_FzS5-_wfFgeU8-bAKmD6z
PRODUCTION_LOCATION_MAIN=LZ3GAW84ENWVV  # 663 Lexington Ave
```

**Verify these are correct:**
1. Log into Square Dashboard (production): https://squareup.com/dashboard
2. Go to **Developer** → **Applications** → Find your app
3. Confirm **Application ID** matches `PRODUCTION_APP_ID`
4. Generate/verify **Production Access Token** matches `PRODUCTION_ACCESS_TOKEN`

---

## Step 2: Test Production Connection (Read-Only)

**Before making any changes**, verify you can connect to production:

```bash
# 1. Update .env to use production
# Change this line:
SQUARE_ENVIRONMENT=production

# 2. Test authentication (READ-ONLY)
python scripts/auth/test_auth.py
```

**Expected output:**
```
🔧 ENVIRONMENT: PRODUCTION
⚠️  WARNING: PRODUCTION MODE - Changes affect live data!
======================================================================

🔑 Testing Square API authentication...
   Environment: PRODUCTION

✅ Authentication successful!
   Found X location(s):
   - [Your actual Just Salad locations]
```

**⚠️ If you see errors:**
- Double-check `PRODUCTION_ACCESS_TOKEN` is correct
- Verify token has not expired
- Ensure you're using **production** token (not sandbox)

---

## Step 3: List Production Locations

Get all Just Salad location IDs:

```bash
python scripts/auth/list_locations.py > production_locations.txt
```

**Review output:**
- Identify which locations should have the catering menu
- Update `.env` if needed with correct `PRODUCTION_LOCATION_MAIN`
- Document location IDs for future reference

---

## Step 4: Check for Existing Catalog Items

**CRITICAL:** Check if production already has catalog items to avoid duplicates:

```bash
python scripts/catalog/validate_poc.py
```

**If items exist:**
- Review them in Square Dashboard
- Decide: Keep, Delete, or Merge with new items
- Use `scripts/maintenance/cleanup_duplicates.py` if needed

**If no items exist:**
- ✅ Safe to proceed with fresh catalog creation

---

## Step 5: Create Production Catalog (POC Items)

**This step creates 6 menu items in production.**

### Dry Run (Recommended)

Review the script before running:
```bash
# Just review what will be created
cat scripts/catalog/create_catalog_with_images.py | grep "items_config ="
```

Verify:
- Item names match approved menu
- Prices are correct ($15.00 for POC)
- Categories are appropriate

### Execute Production Deployment

```bash
python scripts/catalog/create_catalog_with_images.py
```

**You will see:**
```
🔧 ENVIRONMENT: PRODUCTION
⚠️  WARNING: PRODUCTION MODE - Changes affect live data!
======================================================================
⚠️  You are in PRODUCTION mode. Type 'yes' to continue:
```

**Type `yes` and press Enter** to proceed.

**Expected results:**
```
📍 STEP 1: Syncing Locations to Database
   ✓ Synced: [Location names]

📁 STEP 2: Creating Categories
   ✓ Created: Signature Salads
   ✓ Created: Wraps
   ✓ Created: Build Your Own
   ✓ Created: Smoothies
   ✓ Created: Snacks
   ✓ Created: Beverages

📦 STEP 4: Creating Menu Items
   ✓ Created in Square: Autumn Caesar
   [... 5 more items]

🖼️  STEP 5: Processing Images
   ✓ Downloaded: Autumn_Caesar.png
   ✓ Uploaded to Square
   [... 3 more images]

✅ CATALOG SETUP COMPLETE
```

---

## Step 6: Verify in Production Dashboard

1. **Go to Square Dashboard:** https://squareup.com/dashboard/items/library
2. **Check Categories:**
   - Navigate to **Items & Orders** → **Categories**
   - Verify all 6 categories appear
3. **Check Menu Items:**
   - Go to **Items & Orders** → **Items**
   - Verify all 6 items appear with:
     - ✅ Correct names
     - ✅ Correct prices
     - ✅ Images attached (4 items)
     - ✅ Assigned to correct categories
4. **Check Locations:**
   - Verify items are available at correct locations

---

## Step 7: Test Order Creation (Optional)

Create a test order to verify checkout works:

```bash
# This creates a $15 test order (not charged)
python scripts/catalog/create_test_order.py
# (Note: This script needs to be created if you want order testing)
```

**Or manually test in Dashboard:**
1. Go to **Point of Sale** → **New Sale**
2. Add one of your catering items
3. Use test card: `4111 1111 1111 1111`
4. Complete checkout
5. Verify order appears in **Orders** tab

---

## Step 8: Enable Square Online (Production)

If using Square Online for customer-facing orders:

1. **Dashboard** → **Online** → **Turn On Square Online**
2. **Choose "Professional Plan"** ($12/month for custom domain)
3. **Customize Branding:**
   - Upload Just Salad logo
   - Set brand colors
   - Choose template
4. **Connect Custom Domain:** (e.g., catering.justsalad.com)
   - Follow Square's domain setup wizard
   - Update DNS records at your domain registrar
5. **Publish Site**

**Your menu items will automatically appear on Square Online!**

---

## Step 9: Update Database Tracking

Verify production data is tracked:

```bash
python -c "
import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd() / 'src'))
from db_utils import show_summary
show_summary('production')
"
```

**Expected output:**
```
📊 Database Summary - PRODUCTION
============================================================
Locations: X
Categories: 6
Menu Items: 6
Images: 4
```

---

## Step 10: Switch Back to Sandbox

**After deployment, switch back to sandbox for future development:**

```bash
# Edit .env
SQUARE_ENVIRONMENT=sandbox
```

**Verify:**
```bash
python src/env_utils.py
# Should show: 🔧 ENVIRONMENT: SANDBOX
```

---

## Rollback Procedure

If something goes wrong, here's how to rollback:

### Delete Items Created
```bash
# Set to production
SQUARE_ENVIRONMENT=production

# Run cleanup
python scripts/maintenance/cleanup_duplicates.py
```

### Manual Deletion
1. Go to Square Dashboard → **Items & Orders** → **Items**
2. Select all newly created items
3. Click **Actions** → **Delete**
4. Repeat for categories if needed

### Database Cleanup
```bash
# Clear production data from database
sqlite3 data/square_catalog.db "DELETE FROM menu_items WHERE environment='production';"
sqlite3 data/square_catalog.db "DELETE FROM categories WHERE environment='production';"
```

---

## Post-Deployment Tasks

### Immediate (Within 1 hour)
- [ ] Monitor Square Dashboard for errors
- [ ] Test one order end-to-end
- [ ] Verify Square Online displays items (if enabled)
- [ ] Send test order to team for QA

### Within 24 hours
- [ ] Expand menu (add remaining 22 items from menu.json)
- [ ] Set up modifiers (proteins, toppings, dressings)
- [ ] Configure order minimums (10-item minimum)
- [ ] Train staff on new system

### Within 1 week
- [ ] Enable production logging/monitoring
- [ ] Set up automated menu syncs (if desired)
- [ ] Gather customer feedback
- [ ] Optimize based on usage patterns

---

## Support & Troubleshooting

### Common Issues

**"Invalid access token"**
- Verify `PRODUCTION_ACCESS_TOKEN` is production token (not sandbox)
- Check if token expired → regenerate in Square Dashboard

**"Location not found"**
- Run `scripts/auth/list_locations.py` to get correct ID
- Update `PRODUCTION_LOCATION_MAIN` in `.env`

**"Duplicate items detected"**
- Run `scripts/maintenance/cleanup_duplicates.py`
- Or manually delete via Dashboard

**Images not uploading**
- Check image URL is accessible
- Verify image format (PNG, JPG supported)
- Try downloading image manually to test

### Emergency Contacts

- **Square Support:** https://squareup.com/help/us/en/contact
- **Developer Support:** https://developer.squareup.com/forums

### Logs & Debugging

Check database for production records:
```bash
sqlite3 data/square_catalog.db "SELECT * FROM sync_log WHERE environment='production' ORDER BY timestamp DESC LIMIT 10;"
```

---

## Success Criteria

✅ **Deployment is successful when:**
- All 6 menu items visible in production Dashboard
- 4 images uploaded and attached
- Items available at correct locations
- Test order completes successfully
- Database tracks all production IDs
- Square Online displays menu (if enabled)

🎉 **You're live!** Customers can now order Just Salad catering through Square.

---

## Next Steps

After successful deployment, see **POC_SUMMARY.md** for:
- Adding remaining 22 menu items
- Setting up modifiers (Build Your Own)
- Configuring catering-specific rules
- Automating menu syncs
