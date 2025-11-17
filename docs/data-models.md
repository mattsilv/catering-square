# Data Models

## MenuItem

```typescript
interface MenuItem {
  id: string;
  squareId?: string; // Square catalog object ID
  name: string;
  type: 'SALAD' | 'WRAP' | 'SMOOTHIE' | 'SNACK' | 'BEVERAGE' | 'SOUP' | 'BUILD_YOUR_OWN';
  category: 'INDIVIDUAL_MEAL' | 'BYO_SALAD_BAR' | 'SMOOTHIE' | 'SNACK' | 'BEVERAGE';
  basePrice: number; // in cents
  minimumQuantity: number; // default: 1

  // Signature items
  ingredients?: {
    greens: string[];
    protein?: string;
    toppings: string[];
    dressing: string;
  };

  // BYO configurator rules
  configuration?: {
    greensCount: number;    // 2
    proteinCount: number;   // 1
    cheeseCount: number;    // 1
    toppingsCount: number;  // 6
    dressingsCount: number; // 3
  };

  tags: string[]; // ['FAN_FAVORITE', 'PLANT_BASED']
  requiresWarning: boolean; // food safety warning
  canConvertToWrap: boolean;
  hasVariants: boolean;
  variants?: Variant[];
}
```

## OrderItem

```typescript
interface OrderItem {
  menuItemId: string;
  quantity: number;

  // Bundle option
  includeBundle: boolean; // adds chips + cookie

  // BYO selections
  selectedGreens?: string[]; // length: 2
  selectedProtein?: string;
  selectedCheese?: string;
  selectedToppings?: string[]; // base: 6
  selectedDressings?: string[]; // base: 3
  additionalToppings?: string[]; // paid extras
  additionalDressings?: string[]; // paid extras

  // Item variants
  selectedVariant?: string;
  selectedSize?: string;

  // Customization
  convertToWrap: boolean;
  specialInstructions?: string;
  allergyNotes?: string;
}
```

## Validation Rules

### Minimum Quantities

```javascript
if (category === 'INDIVIDUAL_MEAL' && quantity < 10) {
  throw Error("Individual meals require 10 person minimum");
}

if (type === 'BUILD_YOUR_OWN' && quantity < 10) {
  throw Error("Build Your Own requires 10 person minimum");
}

if (name === 'Cookie Platter' && quantity < 10) {
  throw Error("Cookie platters require minimum of 10");
}
```

### BYO Configuration

```javascript
if (type === 'BUILD_YOUR_OWN') {
  assert(selectedGreens.length === 2, "Select exactly 2 greens");
  assert(selectedProtein, "Select exactly 1 protein");
  assert(selectedCheese, "Select exactly 1 cheese");
  assert(selectedToppings.length >= 6, "Select at least 6 toppings");
  assert(selectedDressings.length >= 3, "Select at least 3 dressings");
}
```

## Square Sync

Map Square catalog objects to MenuItem:
- `CatalogItem` → `MenuItem.squareId`
- `ItemVariation` → base price + variants
- `Modifier` → additional toppings/dressings
- Custom attributes → tags, minimums, config rules
