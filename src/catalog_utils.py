"""
Purpose: Production-safe catalog utilities with duplicate prevention
Related: create_categories.py, create_menu_items.py
Refactor if: >500 lines OR handling unrelated catalog operations

CRITICAL: These utilities prevent duplicates in production
"""

from collections import defaultdict
from square import Square

def get_existing_catalog_items(client: Square, item_type='ITEM'):
    """
    Get all existing catalog items of a specific type.

    Args:
        client: Square API client
        item_type: 'ITEM', 'CATEGORY', etc.

    Returns:
        dict: {name: object} mapping of existing items
    """
    existing = {}

    try:
        if item_type == 'ITEM':
            # Use search_items for items
            response = client.catalog.search_items()

            if hasattr(response, 'items') and response.items:
                # Get full details
                item_ids = [item.id for item in response.items]
                details = client.catalog.batch_get(object_ids=item_ids)

                if hasattr(details, 'objects') and details.objects:
                    for obj in details.objects:
                        existing[obj.item_data.name] = obj

        elif item_type == 'CATEGORY':
            # Categories need to be retrieved via search since list() doesn't work reliably
            # First, get all items which include their category references
            items_response = client.catalog.search_items()

            category_ids = set()

            if hasattr(items_response, 'items') and items_response.items:
                # Get full item details to extract category IDs
                item_ids = [item.id for item in items_response.items]
                if item_ids:
                    details = client.catalog.batch_get(object_ids=item_ids)

                    if hasattr(details, 'objects') and details.objects:
                        for obj in details.objects:
                            if hasattr(obj.item_data, 'category_id') and obj.item_data.category_id:
                                category_ids.add(obj.item_data.category_id)

                    # Also check related_objects which includes categories
                    if hasattr(details, 'related_objects') and details.related_objects:
                        for obj in details.related_objects:
                            if obj.type == 'CATEGORY':
                                existing[obj.category_data.name] = obj

            # If we found category IDs, batch get them
            if category_ids:
                cats_response = client.catalog.batch_get(object_ids=list(category_ids))
                if hasattr(cats_response, 'objects') and cats_response.objects:
                    for obj in cats_response.objects:
                        existing[obj.category_data.name] = obj

    except Exception as e:
        print(f"Warning: Could not fetch existing {item_type}s: {e}")

    return existing


def create_or_update_category(client: Square, category_name, description, idempotency_key):
    """
    Create category only if it doesn't exist, otherwise return existing.

    Args:
        client: Square API client
        category_name: Name of the category
        description: Category description
        idempotency_key: Unique key for this operation

    Returns:
        tuple: (category_id, was_created)
    """
    # Check if category already exists
    existing = get_existing_catalog_items(client, 'CATEGORY')

    if category_name in existing:
        print(f"   ⚠️  Category '{category_name}' already exists (ID: {existing[category_name].id})")
        return (existing[category_name].id, False)

    # Create new category
    import uuid
    temp_id = f"#{uuid.uuid4().hex[:16]}"

    response = client.catalog.batch_upsert(
        idempotency_key=idempotency_key,
        batches=[{
            'objects': [{
                'type': 'CATEGORY',
                'id': temp_id,
                'category_data': {
                    'name': category_name,
                    'description': description
                }
            }]
        }]
    )

    if hasattr(response, 'errors') and response.errors:
        raise Exception(f"Failed to create category: {response.errors[0].detail}")

    if hasattr(response, 'objects') and response.objects:
        return (response.objects[0].id, True)

    raise Exception("Unexpected response from catalog API")


def create_or_update_item(client: Square, item_name, category_id, description,
                          price_cents, variation_name='Regular',
                          image_url=None, idempotency_key=None):
    """
    Create menu item only if it doesn't exist, otherwise return existing.

    Args:
        client: Square API client
        item_name: Name of the item
        category_id: Square category ID
        description: Item description
        price_cents: Price in cents (e.g., 1500 = $15.00)
        variation_name: Name for the price variation
        image_url: Optional image URL
        idempotency_key: Unique key for this operation

    Returns:
        tuple: (item_id, was_created)
    """
    # Check if item already exists
    existing = get_existing_catalog_items(client, 'ITEM')

    if item_name in existing:
        print(f"   ⚠️  Item '{item_name}' already exists (ID: {existing[item_name].id})")
        return (existing[item_name].id, False)

    # Create new item
    import uuid

    if not idempotency_key:
        idempotency_key = str(uuid.uuid4())

    item_id = f"#{uuid.uuid4().hex[:16]}"
    variation_id = f"#{uuid.uuid4().hex[:16]}"

    item_obj = {
        'type': 'ITEM',
        'id': item_id,
        'item_data': {
            'name': item_name,
            'description': description[:500] if description else '',
            'category_id': category_id,
            'variations': [{
                'type': 'ITEM_VARIATION',
                'id': variation_id,
                'item_variation_data': {
                    'name': variation_name,
                    'pricing_type': 'FIXED_PRICING',
                    'price_money': {
                        'amount': price_cents,
                        'currency': 'USD'
                    }
                }
            }]
        }
    }

    if image_url:
        item_obj['item_data']['image_urls'] = [image_url]

    response = client.catalog.batch_upsert(
        idempotency_key=idempotency_key,
        batches=[{
            'objects': [item_obj]
        }]
    )

    if hasattr(response, 'errors') and response.errors:
        raise Exception(f"Failed to create item: {response.errors[0].detail}")

    if hasattr(response, 'objects') and response.objects:
        return (response.objects[0].id, True)

    raise Exception("Unexpected response from catalog API")


def check_for_duplicates(client: Square):
    """
    Check catalog for duplicate items or categories.

    Returns:
        dict: {'items': {name: [ids]}, 'categories': {name: [ids]}}
    """
    duplicates = {'items': {}, 'categories': {}}

    # Check items
    items_response = client.catalog.search_items()
    if hasattr(items_response, 'items') and items_response.items:
        item_ids = [item.id for item in items_response.items]
        details = client.catalog.batch_get(object_ids=item_ids)

        if hasattr(details, 'objects') and details.objects:
            items_by_name = defaultdict(list)
            for obj in details.objects:
                items_by_name[obj.item_data.name].append(obj.id)

            duplicates['items'] = {name: ids for name, ids in items_by_name.items() if len(ids) > 1}

    # Check categories
    categories_response = client.catalog.list(types='CATEGORY')
    if hasattr(categories_response, 'objects') and categories_response.objects:
        cats_by_name = defaultdict(list)
        for obj in categories_response.objects:
            cats_by_name[obj.category_data.name].append(obj.id)

        duplicates['categories'] = {name: ids for name, ids in cats_by_name.items() if len(ids) > 1}

    return duplicates
