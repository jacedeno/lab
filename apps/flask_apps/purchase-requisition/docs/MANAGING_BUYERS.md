# Managing Buyers

The list of buyers is now managed in `app/config/buyers.yaml`. Changes take effect immediately without requiring a redeploy.

## Adding a new buyer

Edit `app/config/buyers.yaml` and add a new entry:

```yaml
  - email: new.buyer@capitolaggregates.com
    name: New Buyer Name
    department: Procurement
```

## Removing a buyer

Find the buyer's entry in `app/config/buyers.yaml` and delete it.

## Editing buyer information

Modify the email, name, or department for any buyer in `app/config/buyers.yaml`.

## Format requirements

- **email**: Must be a valid email address with @capitolaggregates.com domain
- **name**: Full name of the buyer (optional but recommended)
- **department**: Department name (optional but recommended)

All changes are case-insensitive for email matching.

## Notes

- Email addresses are automatically lowercased for consistent matching
- Changes are loaded automatically on the next request (no redeploy needed)
- The YAML file must be valid; incorrect syntax will log a warning and fall back to an empty buyer list
