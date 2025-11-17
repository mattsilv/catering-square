# Square Integration

## Setup

1. **Create Square Application** at https://developer.squareup.com
2. **Get credentials**: Application ID, Access Token
3. **Set environment variables**:
   ```bash
   SQUARE_ACCESS_TOKEN=your_access_token
   SQUARE_LOCATION_ID=your_location_id
   SQUARE_ENVIRONMENT=sandbox # or production
   ```

## APIs Used

### Catalog API
Sync menu items from Square POS to online ordering system.

**Key endpoints**:
- `GET /v2/catalog/list` - Fetch all catalog items
- `GET /v2/catalog/object/{id}` - Get specific item details
- `POST /v2/catalog/search` - Search catalog by type/name

**Sync strategy**:
- Poll catalog every 15 minutes for updates
- Store Square `version` field to detect changes
- Map `CatalogItem` → `MenuItem` (see [data-models.md](data-models.md))

### Payments API
Process catering order payments.

**Flow**:
1. Frontend: Square Web Payments SDK generates payment token
2. Backend: `POST /v2/payments` with token + order details
3. Store payment ID with order for refund/tracking

**Key fields**:
```json
{
  "source_id": "payment_token_from_frontend",
  "amount_money": {
    "amount": 10000, // cents
    "currency": "USD"
  },
  "location_id": "SQUARE_LOCATION_ID",
  "idempotency_key": "unique_order_id"
}
```

## Custom Attributes

Use Square custom attributes to store catering-specific metadata:

```json
{
  "custom_attribute_values": {
    "minimum_quantity": "10",
    "can_convert_to_wrap": "true",
    "is_fan_favorite": "true",
    "byo_config": "{\"greens\": 2, \"protein\": 1}"
  }
}
```

## Webhooks (Optional)

Subscribe to catalog updates to sync in real-time:
- `catalog.version.updated` - Catalog changed
- `inventory.count.updated` - Stock levels changed

## Error Handling

- **Rate limits**: 10 requests/second per location
- **Idempotency**: Use order ID as idempotency key for payments
- **Retries**: Exponential backoff for 5xx errors
- **Timeouts**: 30s for catalog sync, 10s for payments

## Testing

Use Square Sandbox for development:
- Different credentials than production
- Test card: `4111 1111 1111 1111` (any CVV/ZIP)
- Catalog changes don't affect production

## Resources

- [Square API Docs](https://developer.squareup.com/docs)
- [Web Payments SDK](https://developer.squareup.com/docs/web-payments/overview)
- [Catalog API Guide](https://developer.squareup.com/docs/catalog-api/what-it-does)
