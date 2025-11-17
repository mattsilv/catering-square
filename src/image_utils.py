"""
Purpose: Download and upload menu item images to Square Catalog
Related: catalog_utils.py, db_utils.py
Refactor if: >400 lines OR handling multiple image sources
"""

import os
import requests
from pathlib import Path
from square import Square
import mimetypes

# Get project root and set images directory
PROJECT_ROOT = Path(__file__).parent.parent
IMAGES_DIR = PROJECT_ROOT / 'data' / 'images'


def ensure_images_dir():
    """Create images directory if it doesn't exist"""
    Path(IMAGES_DIR).mkdir(exist_ok=True)
    return IMAGES_DIR


def download_image(url, item_name):
    """
    Download image from URL and save locally.

    Args:
        url: Source image URL
        item_name: Name of menu item (for filename)

    Returns:
        str: Local file path, or None if download failed
    """
    ensure_images_dir()

    # Clean item name for filename
    safe_name = "".join(c for c in item_name if c.isalnum() or c in (' ', '-', '_')).strip()
    safe_name = safe_name.replace(' ', '_')

    # Get extension from URL
    ext = Path(url).suffix or '.jpg'

    local_path = os.path.join(IMAGES_DIR, f"{safe_name}{ext}")

    # Skip if already downloaded
    if os.path.exists(local_path):
        print(f"   → Image already downloaded: {safe_name}{ext}")
        return local_path

    try:
        print(f"   ⬇️  Downloading: {url[:60]}...")

        response = requests.get(url, timeout=30, stream=True)
        response.raise_for_status()

        with open(local_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        print(f"   ✅ Downloaded: {safe_name}{ext}")
        return local_path

    except Exception as e:
        print(f"   ❌ Download failed: {str(e)}")
        return None


def upload_image_to_square(client: Square, local_path, item_name):
    """
    Upload image to Square Catalog.

    Args:
        client: Square API client
        local_path: Path to local image file
        item_name: Name of menu item (for image caption)

    Returns:
        str: Square image ID, or None if upload failed
    """
    if not os.path.exists(local_path):
        print(f"   ❌ Image file not found: {local_path}")
        return None

    try:
        # Detect MIME type
        mime_type, _ = mimetypes.guess_type(local_path)
        if not mime_type or not mime_type.startswith('image/'):
            mime_type = 'image/jpeg'  # Default fallback

        print(f"   ⬆️  Uploading to Square: {Path(local_path).name}")

        # Create image in Square catalog
        import uuid

        # Open file for upload
        with open(local_path, 'rb') as image_file:
            response = client.catalog.images.create(
                request={
                    'idempotency_key': str(uuid.uuid4()),
                    'image': {
                        'type': 'IMAGE',
                        'id': f'#{uuid.uuid4().hex[:16]}',
                        'image_data': {
                            'caption': item_name
                        }
                    }
                },
                image_file=image_file
            )

        if hasattr(response, 'errors') and response.errors:
            print(f"   ❌ Upload failed: {response.errors[0].detail}")
            return None

        if hasattr(response, 'image') and response.image:
            image_id = response.image.id
            print(f"   ✅ Uploaded: {image_id}")
            return image_id

        print(f"   ❌ Unexpected response from Square")
        return None

    except Exception as e:
        print(f"   ❌ Upload exception: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


def attach_image_to_item(client: Square, item_square_id, image_square_id):
    """
    Attach uploaded image to menu item.

    Args:
        client: Square API client
        item_square_id: Square ID of the menu item
        image_square_id: Square ID of the image

    Returns:
        bool: True if successful
    """
    try:
        print(f"   🔗 Attaching image {image_square_id} to item {item_square_id}")

        # Get current item to preserve its data
        item_response = client.catalog.object.get(object_id=item_square_id)

        if hasattr(item_response, 'errors') and item_response.errors:
            print(f"   ❌ Failed to retrieve item: {item_response.errors[0].detail}")
            return False

        if not hasattr(item_response, 'object'):
            print(f"   ❌ Item not found")
            return False

        item = item_response.object

        # Update item with image ID - must preserve variations!
        import uuid
        idempotency_key = str(uuid.uuid4())

        # Preserve variations from original item
        variations = []
        if hasattr(item.item_data, 'variations'):
            for var in item.item_data.variations:
                var_data = {
                    'type': 'ITEM_VARIATION',
                    'id': var.id,
                    'version': var.version,
                    'item_variation_data': {
                        'name': var.item_variation_data.name,
                        'pricing_type': var.item_variation_data.pricing_type
                    }
                }
                # Add price if it exists
                if hasattr(var.item_variation_data, 'price_money'):
                    var_data['item_variation_data']['price_money'] = {
                        'amount': var.item_variation_data.price_money.amount,
                        'currency': var.item_variation_data.price_money.currency
                    }
                variations.append(var_data)

        update_response = client.catalog.batch_upsert(
            idempotency_key=idempotency_key,
            batches=[{
                'objects': [{
                    'type': 'ITEM',
                    'id': item.id,
                    'version': item.version,
                    'item_data': {
                        'name': item.item_data.name,
                        'description': item.item_data.description if hasattr(item.item_data, 'description') else '',
                        'category_id': item.item_data.category_id if hasattr(item.item_data, 'category_id') else None,
                        'variations': variations,
                        'image_ids': [image_square_id]
                    }
                }]
            }]
        )

        if hasattr(update_response, 'errors') and update_response.errors:
            print(f"   ❌ Failed to attach image: {update_response.errors[0].detail}")
            return False

        print(f"   ✅ Image attached successfully")
        return True

    except Exception as e:
        print(f"   ❌ Exception: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def process_item_image(client: Square, item_name, item_square_id, source_url, environment):
    """
    Complete image workflow: download, upload to Square, attach to item, save to DB.

    Args:
        client: Square API client
        item_name: Name of menu item
        item_square_id: Square ID of menu item
        source_url: URL of source image
        environment: 'sandbox' or 'production'

    Returns:
        str: Square image ID, or None if failed
    """
    from db_utils import save_image

    if not source_url:
        return None

    print(f"\n📸 Processing image for: {item_name}")

    # Step 1: Download image
    local_path = download_image(source_url, item_name)
    if not local_path:
        return None

    # Step 2: Upload to Square
    image_square_id = upload_image_to_square(client, local_path, item_name)
    if not image_square_id:
        return None

    # Step 3: Attach to item
    success = attach_image_to_item(client, item_square_id, image_square_id)
    if not success:
        return None

    # Step 4: Save to database
    save_image(environment, image_square_id, source_url, local_path)

    return image_square_id


def cleanup_old_images(days_old=30):
    """Remove downloaded images older than specified days"""
    import time
    from datetime import datetime, timedelta

    if not os.path.exists(IMAGES_DIR):
        return

    cutoff = time.time() - (days_old * 86400)
    removed = 0

    for filename in os.listdir(IMAGES_DIR):
        filepath = os.path.join(IMAGES_DIR, filename)
        if os.path.isfile(filepath):
            if os.path.getmtime(filepath) < cutoff:
                os.remove(filepath)
                removed += 1

    if removed:
        print(f"🗑️  Removed {removed} old image(s)")


if __name__ == "__main__":
    ensure_images_dir()
    print(f"✅ Images directory ready: {IMAGES_DIR}")
