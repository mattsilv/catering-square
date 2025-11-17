# Public Data Endpoints

Just Salad provides public JSON endpoints for menu data and location information. Use these for UI mockups and location filtering.

## Menu Endpoint

**URL**: `https://cdn1.justsalad.com/public/menu.json`

**Purpose**: Full menu catalog with items, nutrition, images, seasonal flags

### Response Structure

```json
{
  "menu_items": [
    {
      "id": 4807,
      "name": "Orchard Bowl",
      "image_url": "https://res.cloudinary.com/...",
      "image_hi_res_url": "https://res.cloudinary.com/...",
      "description": "Arugula, Regenerative Organic Quinoa...",
      "nutrition_info": {
        "calories": 430,
        "carbon_footprint": 1.0,
        "protein": 36,
        "carbohydrates": 27
      },
      "suggested_ingredient": "Balsamic Vinaigrette",
      "category_id": 103,
      "fall_seasonal": true,
      "diets": []
    }
  ]
}
```

### Key Fields

- `id` - Unique menu item identifier
- `name` - Display name
- `image_url` / `image_hi_res_url` - Product images
- `description` - Ingredient list
- `nutrition_info` - Calories, macros, carbon footprint
- `category_id` - Menu category (103=bowls, 107=smoothies, 117=market plates)
- `{season}_seasonal` - Boolean flags for seasonal items
- `suggested_ingredient` - Recommended dressing/topping

### Usage

Use for mockups of:
- Menu item cards
- Ingredient lists
- Nutrition labels
- Seasonal promotions

**Note**: This is Just Salad's general menu, not catering-specific. Cross-reference with catering menu requirements in [menu-structure.md](menu-structure.md).

## Locations Endpoint

**URL**: `https://cdn1.justsalad.com/public/store_locations.json`

**Purpose**: Store locations with catering availability, hours, contact info

### Response Structure

```json
{
  "storelocations": [
    {
      "name": "Midtown East (Lexington Ave)",
      "store_num": "8",
      "phone": "8666733757",
      "address": {
        "address_1": "663 Lexington Avenue",
        "city": "New York",
        "state": 32,
        "zipcode": "10022",
        "lat": "40.75981",
        "lng": "-73.96975"
      },
      "hours_line_1": "Mon-Fri: 10:30am-9:30pm",
      "order_link": "https://order.justsalad.com/menu/6",
      "amenities": {
        "catering": true,
        "bbb_program": true,
        "outdoor_seat": true
      },
      "business_status": "OPERATIONAL",
      "coming_soon": false
    }
  ]
}
```

### Filtering for Catering

**IMPORTANT**: Only include locations where `amenities.catering === true`

```javascript
const cateringLocations = data.storelocations.filter(
  location => location.amenities?.catering === true &&
              location.business_status === 'OPERATIONAL' &&
              !location.coming_soon
);
```

### Key Fields

- `name` - Store display name
- `store_num` - Internal store identifier
- `phone` - Contact number
- `address` - Full address with lat/lng for mapping
- `hours_line_1/2/3` - Human-readable hours
- `opening_hours` - Structured hours (day/time format)
- `amenities.catering` - **Filter on this field**
- `business_status` - OPERATIONAL vs CLOSED_TEMPORARILY
- `order_link` - Direct ordering URL

### Usage

- Location selector/dropdown
- Service area mapping (lat/lng)
- Contact information display
- Market-specific pricing zones (if applicable)

## Implementation Notes

### Caching

Both endpoints are static CDN resources:
- Cache-Control: public, max-age=3600 (1 hour)
- Safe to cache client-side or in CDN
- Poll for updates every 1-24 hours depending on use case

### Error Handling

```javascript
async function fetchMenu() {
  try {
    const response = await fetch('https://cdn1.justsalad.com/public/menu.json');
    if (!response.ok) throw new Error('Menu fetch failed');
    return await response.json();
  } catch (error) {
    console.error('Menu unavailable:', error);
    return { menu_items: [] }; // Fallback
  }
}
```

### Data Transformation

Menu endpoint uses general categories, not catering categories. Map as needed:

```javascript
// Example: Filter to potential catering items
const cateringItems = menuData.menu_items.filter(item =>
  item.category_id !== 107 // Exclude smoothies if not in catering menu
);
```

## Related Docs

- [Menu Structure](menu-structure.md) - Catering-specific menu requirements
- [Business Rules](business-rules.md) - Minimums and pricing
- [Data Models](data-models.md) - Internal schema design
