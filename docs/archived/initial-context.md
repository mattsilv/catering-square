# Just Salad Catering Online Ordering System - Requirements

## Executive Summary
Build an online ordering system for Just Salad catering that mirrors the physical menu structure. System must support minimum order quantities, customization options, bundling logic, and market-specific pricing.

---

## System-Wide Requirements

### Business Rules
- **Minimum Order Quantities**
  - Individual meals: 10 person minimum
  - Build Your Own Salad Bar: 10 person minimum
  - Chocolate Chip Cookie Platters: 10 minimum
- **Pricing**: Market-variable (pricing structure not provided in menu - needs definition)
- **Contact**: catering@justsalad.com for customization requests
- **Phone**: (332) 267-0060

### Legal/Compliance
- Display allergen warning: "Allergies? Let our team know so that we can accommodate you."
- Display food safety warning: "*Consuming raw or undercooked meats, poultry, seafood shellfish or eggs may increase your risk of foodbourne illness, especially if you have certain medical conditions."
- Clear labeling for all items including dietary preferences

---

## Menu Structure

## 1. INDIVIDUAL MEALS

### 1.1 Signature Salads & Wraps
**Validation**: Minimum 10 person order

#### Salad Items (All can be converted to wraps)

**1. Chicken Caesar**
- Base: Romaine + Kale
- Protein: Roasted Chicken
- Toppings: Parmesan, Croutons
- Dressing: Creamy Caesar
- Tags: [FAN_FAVORITE]

**2. Thai Chicken Crunch**
- Base: Romaine + Red Cabbage
- Protein: Roasted Chicken
- Toppings: Carrots, Cucumbers, Cilantro, Wonton Strips
- Dressing: Thai Peanut
- Tags: [FAN_FAVORITE]

**3. Buffalo Chicken**
- Base: Romaine + Red Cabbage
- Protein: Braised Chicken Thigh
- Toppings: White Cheddar, Crispy Onions, Cucumbers, Carrots
- Dressing: Spicy Buffalo Ranch

**4. Tokyo Supergreens**
- Base: Supergreens Blend
- Protein Options: Organic Sesame Tofu OR Oven Roasted Chicken
- Toppings: Carrots, Edamame, Avocado, Shaved Broccoli, Almonds, Furikake Shake
- Dressing: Miso Ginger Vinaigrette
- Tags: [FAN_FAVORITE]

**5. Mezze Crunch**
- Base: Romaine, Kale + Red Cabbage
- Toppings: Feta, Hemp Hearts, Regenerative Organic Chickpeas, Grape Tomatoes, Cucumbers, Sliced Pepperoncini, Spicy Harissa Pita
- Dressing: Cucumber Tzatziki
- Tags: [FAN_FAVORITE]

**6. Crispy Chicken Poblano**
- Base: Romaine + Kale
- Protein: Crispy Chicken
- Toppings: Cotija, Avocado, Corn, Pickled Onions, Crunchy Tortillas
- Dressing: Smoky Poblano Ranch
- Tags: [FAN_FAVORITE]

**7. Plant Power**
- Base: Romaine + Kale
- Toppings: Chickpeas, Edamame, Roasted Beets, Pickled Onions, Tajin® Spiced Pumpkin Seeds, Hemp Hearts
- Dressing: Honey Mustard Vinaigrette
- Tags: [FAN_FAVORITE]

**8. Modern Greek Crunch**
- Base: Romaine
- Toppings: Feta, Spicy Harissa Pita, Chickpeas, Grape Tomatoes, Pickled Onions, Cucumbers
- Dressing: Cucumber Tzatziki
- Tags: [FAN_FAVORITE]

**9. Balsamic Chicken Avocado**
- Base: Romaine
- Protein: Roasted Chicken
- Toppings: Avocado, Cage-Free Jammy Egg*, Grape Tomatoes, Corn
- Dressing: Balsamic Vinaigrette
- Note: *Food safety warning applies

**10. Earth Bowl**
- Base: Arugula + Kale
- Toppings: Regenerative Organic Quinoa, Vegan Feta, Roasted Beets, Sweet Potatoes, Apples, Almonds
- Dressing: Honey Mustard Vinaigrette

#### Wrap-Only Items

**11. Honey Crispy Chicken Wrap**
- Base: Romaine, Spinach + Red Cabbage
- Protein: Crispy Chicken
- Toppings: Feta, Regenerative Organic Quinoa, Corn, Crispy Onions, Carrots
- Dressing: Honey Mustard Vinaigrette

**12. Spicy Chicken Caesar Wrap**
- Base: Romaine
- Protein: Roasted Chicken
- Toppings: Parmesan, Croutons
- Dressing: Smoky Poblano Ranch

### 1.2 Bundle Option
- **Name**: "Make It A Bundle"
- **Includes**: Chips + Freshly Baked Chocolate Chip Cookie
- **Applied to**: Any individual meal selection
- **UI Note**: Display as checkbox/toggle option during item configuration

---

## 2. BUILD YOUR OWN SALAD BAR

**Validation**: 
- Minimum 10 person order
- Additional toppings/dressings available for additional cost (pricing not specified)

### Configuration Rules
- **Greens**: Choose exactly 2
- **Proteins**: Choose exactly 1
- **Cheeses**: Choose exactly 1
- **Toppings**: Choose exactly 6
- **Dressings**: Choose exactly 3

### 2.1 Greens (Choose 2)
1. Arugula
2. Baby Spinach
3. Kale
4. Red Cabbage
5. Romaine
6. Supergreens Blend

### 2.2 Proteins (Choose 1)
1. Braised Chicken Thigh
2. Cage-Free Jammy Egg* (requires food safety warning)
3. Crispy Chicken
4. Impossible™ Chicken (Plant-Based)
5. Organic Sesame Tofu
6. Roasted Chicken

### 2.3 Cheeses (Choose 1)
1. Cotija
2. Feta
3. Vegan Feta
4. Hot Honey Goat Cheese
5. Parmesan
6. White Cheddar

### 2.4 Toppings (Choose 6)
1. Almonds
2. Apples
3. Avocado
4. Roasted Beets
5. Shaved Broccoli
6. Carrots
7. Regenerative Organic Chickpeas
8. Corn
9. Crispy Onions
10. Croutons
11. Crunchy Tortillas
12. Cucumbers
13. Dried Cranberries
14. Edamame
15. Grape Tomatoes
16. Pickled Onions
17. Pico de Gallo
18. Spicy Harissa Pita
19. Sweet Potatoes
20. Tajin® Spiced Pumpkin Seeds
21. Wonton Strips

**Note**: System should allow purchasing additional toppings beyond the 6 included (pricing TBD)

### 2.5 Dressings (Choose 3)
1. Balsamic Vinaigrette
2. Chipotle Vinaigrette
3. Cilantro Lime Vinaigrette
4. Lemon Basil Vinaigrette
5. Miso Ginger Vinaigrette
6. Honey Mustard Vinaigrette
7. Creamy Caesar
8. Thai Peanut
9. Cucumber Tzatziki
10. Buttermilk Ranch
11. Spicy Buffalo Ranch
12. Smoky Poblano Ranch
13. Balsamic Vinegar
14. Red Wine Vinegar
15. Extra Virgin Olive Oil
16. Fresh Lemon

**Note**: System should allow purchasing additional dressings beyond the 3 included (pricing TBD)

---

## 3. PLANT-BASED SMOOTHIES

**Individual items, no minimum specified**

### Smoothie Options

**1. Almond Berry Blast**
- Ingredients: Oat Milk, Banana, Almond Butter, Blueberries, Strawberries, Flax Seeds, Organic Agave Nectar

**2. PB Protein**
- Callout: 30g of Protein
- Ingredients: Oat Milk, Baby Spinach, Banana, Bob's Red Mill® Hemp Hearts, Vegan Protein, PB2™ Powdered Peanut Butter, Unsalted Pumpkin Seeds, Organic Agave Nectar

**3. Strawberry Banana**
- Ingredients: Oat Milk, Banana, Strawberries, Flax Seeds, Organic Agave Nectar

**4. Detox Cleanse**
- Ingredients: Baby Spinach, Lemon, Apple, Pineapple, Ginger

---

## 4. SNACKS & BEVERAGES

### 4.1 Snacks

**Skinny Dipped Almonds**
- Variants: Dark Chocolate OR Peanut Butter
- UI: Radio button selection

**Freshly Baked Chocolate Chip Cookies**
- Serving Options:
  - Individual (quantity selector)
  - Platter (minimum 10)

**Assorted Chips**
- No variant specification provided
- Quantity selector

**Soup**
- Variants: Chicken Noodle OR Seasonal Soup
- Sizes: 8 oz OR 16 oz
- UI: Variant dropdown + size selection

### 4.2 Beverages
1. Poppi
2. Open Water
3. LaCroix
4. Coke
5. Diet Coke

---

## Technical Requirements

### Data Model Considerations

#### Menu Item Structure
```
MenuItem {
  id: string
  name: string
  type: enum [SALAD, WRAP, SMOOTHIE, SNACK, BEVERAGE, SOUP, BUILD_YOUR_OWN]
  category: enum [INDIVIDUAL_MEAL, BYO_SALAD_BAR, SMOOTHIE, SNACK, BEVERAGE]
  basePrice: decimal (market-specific)
  minimumQuantity: integer (default: 1)
  
  // For signature items
  ingredients?: {
    greens: string[]
    protein?: string
    toppings: string[]
    dressing: string
  }
  
  // For configurable items
  configuration?: {
    greensCount?: integer
    proteinCount?: integer
    cheeseCount?: integer
    toppingsCount?: integer
    dressingsCount?: integer
  }
  
  // Product metadata
  tags: string[] // [FAN_FAVORITE, PLANT_BASED, etc]
  requiresWarning: boolean // food safety warning
  allergenInfo?: string[]
  
  // Variants (for items with options)
  hasVariants: boolean
  variants?: Variant[]
}

Variant {
  id: string
  name: string
  priceModifier: decimal
  sizes?: Size[]
}

Size {
  id: string
  name: string (e.g., "8 oz", "16 oz")
  priceModifier: decimal
}
```

#### Cart/Order Item
```
OrderItem {
  menuItemId: string
  quantity: integer
  
  // Bundle options
  includeBundle: boolean // adds chips + cookie
  
  // For BYO items
  selectedGreens?: string[] (length: 2)
  selectedProtein?: string (length: 1)
  selectedCheese?: string (length: 1)
  selectedToppings?: string[] (length: 6 + additional paid)
  selectedDressings?: string[] (length: 3 + additional paid)
  additionalToppings?: string[] (upcharge items)
  additionalDressings?: string[] (upcharge items)
  
  // For items with variants
  selectedVariant?: string
  selectedSize?: string
  
  // Conversion option
  convertToWrap: boolean (for eligible salads)
  
  specialInstructions?: string
  allergyNotes?: string
}
```

### Validation Rules

#### Minimum Quantity Enforcement
```javascript
// Individual meals
if (item.category === 'INDIVIDUAL_MEAL' && item.quantity < 10) {
  throw ValidationError("Individual meals require a 10 person minimum");
}

// Build Your Own
if (item.type === 'BUILD_YOUR_OWN' && item.quantity < 10) {
  throw ValidationError("Build Your Own Salad Bar requires a 10 person minimum");
}

// Cookie platters
if (item.name === 'Cookie Platter' && item.quantity < 10) {
  throw ValidationError("Cookie platters require a minimum of 10");
}
```

#### Configuration Validation (BYO)
```javascript
if (item.type === 'BUILD_YOUR_OWN') {
  if (item.selectedGreens.length !== 2) {
    throw ValidationError("Please select exactly 2 greens");
  }
  if (!item.selectedProtein || item.selectedProtein.length === 0) {
    throw ValidationError("Please select exactly 1 protein");
  }
  if (!item.selectedCheese || item.selectedCheese.length === 0) {
    throw ValidationError("Please select exactly 1 cheese");
  }
  if (item.selectedToppings.length < 6) {
    throw ValidationError("Please select at least 6 toppings (included)");
  }
  if (item.selectedDressings.length < 3) {
    throw ValidationError("Please select at least 3 dressings (included)");
  }
}
```

### UI/UX Requirements

#### Product Display
- **Fan Favorites**: Display blue circular badge with text "FAN FAVORITE"
- **Individual Meal Cards**: Show complete ingredient breakdown
- **Allergen Warnings**: Display prominently during checkout and on relevant items
- **Market Pricing**: Show "Contact us for pricing" message where pricing varies by market
- **Wrap Conversion**: Display "Turn any salad into a wrap! Contact us for pricing." on relevant items

#### Checkout Flow
1. Display minimum quantity warnings before allowing add-to-cart
2. Show bundle option toggle for individual meals
3. Collect allergy information at order level
4. Display comprehensive order summary with:
   - Item details (base/toppings/dressings for BYO)
   - Bundled items (chips, cookies)
   - Special requests
   - Total quantity breakdown
5. Require contact information (email, phone)

#### Configuration Builder (BYO)
- **Step 1**: Select Greens (visual selection grid, max 2)
- **Step 2**: Select Protein (visual selection grid, max 1)
- **Step 3**: Select Cheese (visual selection grid, max 1)
- **Step 4**: Select Toppings (visual selection grid, min 6, show "included" count vs "additional" cost)
- **Step 5**: Select Dressings (visual selection grid, min 3, show "included" count vs "additional" cost)
- **Progress Indicator**: Show completion status of each step
- **Summary Panel**: Live preview of selections as they're made

### Admin/Business Requirements

#### Pricing Management
- Support market-specific pricing tables
- Allow custom pricing for:
  - Base items
  - Wrap conversions
  - Bundle additions
  - Additional toppings/dressings (BYO)
  - Size variants (soups)
  - Flavor variants (almonds, soups)

#### Order Management
- Capture full order details including:
  - Special instructions
  - Allergy notes
  - Dietary preferences
  - Delivery time/date
  - Delivery location
- Enable email notifications to catering@justsalad.com
- Support order modifications via admin panel

#### Inventory Management
- Track availability of specialty items:
  - Seasonal soup variants
  - Limited availability ingredients
- Flag out-of-stock items in real-time

---

## Integration Requirements

### Payment Processing
- Not specified in menu - requires integration selection
- Support for catering-size transactions

### Notification System
- Order confirmation emails to customer
- Order notifications to catering@justsalad.com
- Phone fallback: (332) 267-0060

### Analytics Tracking
- Track most popular items (identify future "Fan Favorites")
- Monitor conversion rates on bundle upsells
- Track minimum quantity abandonment rates

---

## Open Questions / Not Specified in Menu

1. **Pricing Structure**: No prices provided - requires business definition
   - Base prices by market
   - Wrap conversion upcharge
   - Bundle pricing (chips + cookie)
   - Additional toppings/dressings pricing (BYO)
   - Size variant pricing (soups)

2. **Lead Times**: How far in advance must orders be placed?

3. **Delivery/Pickup**: System scope (delivery, pickup, both?)

4. **Payment Terms**: Pre-pay required? Invoice options for corporate accounts?

5. **Customization Limits**: Can signature salads be modified? (add/remove ingredients)

6. **Tokyo Supergreens**: Pricing differential for tofu vs chicken protein option?

7. **Seasonal Soup**: How is "seasonal" variant communicated/updated?

8. **Market Definition**: How is customer market determined? (ZIP code? Location selection?)

---

## Implementation Priorities

### Phase 1 (MVP)
- Individual meal ordering with minimum quantity enforcement
- Signature salads/wraps display
- Bundle upsell toggle
- Basic smoothies/snacks/beverages
- Simple cart/checkout
- Email notification to catering team

### Phase 2
- Build Your Own Salad Bar configurator
- Advanced validation rules
- Allergy/dietary preference capture
- Enhanced order management

### Phase 3
- Market-specific pricing engine
- Inventory management
- Admin panel for menu/pricing updates
- Analytics dashboard
- Order modification system

---

## Contact Information
- **Email**: catering@justsalad.com
- **Phone**: (332) 267-0060
- **Website**: justsalad.com/catering