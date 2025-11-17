"""
Purpose: Single source of truth for store naming and utilities
Related: create_test_locations.py, update_location_names.py
Refactor if: >300 lines OR handling unrelated store operations
"""

def format_store_name(store_data, include_suffix=False):
    """
    Format store name consistently across the application.
    This is the SINGLE SOURCE OF TRUTH for store naming.

    Args:
        store_data: Dict with 'store_num' and 'name' keys from Just Salad data
        include_suffix: Whether to append ' - Catering Test' suffix

    Returns:
        Formatted store name: "#{store_num} {name}" or "#{store_num} {name} - Catering Test"

    Examples:
        >>> format_store_name({'store_num': '8', 'name': 'Midtown East (Lexington Ave)'})
        '#8 Midtown East (Lexington Ave)'

        >>> format_store_name({'store_num': '8', 'name': 'Midtown East (Lexington Ave)'}, include_suffix=True)
        '#8 Midtown East (Lexington Ave) - Catering Test'
    """
    store_num = store_data.get('store_num', '0')
    name = store_data.get('name', 'Unknown Store')

    base_name = f"#{store_num} {name}"

    if include_suffix:
        return f"{base_name} - Catering Test"

    return base_name


def parse_store_number(store_name):
    """
    Extract store number from formatted store name.

    Args:
        store_name: Formatted store name like "#8 Midtown East (Lexington Ave)"

    Returns:
        Store number as string, or None if not found

    Examples:
        >>> parse_store_number('#8 Midtown East (Lexington Ave)')
        '8'
    """
    if store_name.startswith('#'):
        parts = store_name[1:].split(' ', 1)
        if parts:
            return parts[0]
    return None


def format_location_for_square(store_data, is_test=True):
    """
    Format Just Salad store data into Square Location API format.

    Args:
        store_data: Dict from Just Salad store_locations.json
        is_test: Whether this is a test/sandbox location

    Returns:
        Dict formatted for Square Locations API
    """
    address = store_data.get('address', {})

    location_name = format_store_name(store_data, include_suffix=is_test)

    return {
        'name': location_name,
        'address': {
            'address_line_1': address.get('address_1', ''),
            'address_line_2': address.get('address_2', ''),
            'locality': address.get('city', ''),
            'administrative_district_level_1': 'NY',
            'postal_code': address.get('zipcode', ''),
            'country': 'US'
        },
        'phone_number': store_data.get('phone', ''),
        'business_name': 'Just Salad Catering' + (' Test' if is_test else ''),
        'type': 'PHYSICAL',
        'description': f"Store #{store_data.get('store_num', 'N/A')}" + (' - Test Location' if is_test else '')
    }
