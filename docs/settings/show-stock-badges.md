# Show stock badges

[Settings index](README.md) · [Configuration guide](../CONFIGURATION.md)

## Purpose

Show an availability badge on product cards for inventory-tracked products.

## When to enable

Enable this when cashiers need to see availability before choosing a product.

## Settings

- Location: Point of Sale → Configuration → Settings → Stock Guard.
- Scope: the selected POS configuration.
- Technical field(s): `stock_guard_show_badges`.
- Default: Off.

Boolean switch. Presentation follows Stock display mode.

Close active POS sessions, save the selected configuration and reopen the POS
before checking the result.

## Example

With 8 units available, quantity mode shows Available: 8. At zero, the badge shows Out of stock. A low-stock threshold of 3 makes 2 units a warning.

## Expected behavior

Available is green, low stock is yellow, out of stock is red and unknown is gray. Products known to be untracked have no badge.

## Relationships with other settings

Combine with Highlight low stock for warnings and Automatically refresh stock for periodic updates. Showing a badge does not enable any blocking.

## Connection and stale data

Previously loaded quantities remain visible after a failed update and are marked as potentially outdated.

## Warnings and limitations

Template cards combine positive availability across their variants. For example, variants with 5 and -2 show 5, not 3. The selected variant is checked separately by early blocking. The card is not a promise that every variant is available.

All quantities follow the [shared availability rules](../CONFIGURATION.md#availability-rules).
No visual snapshot reserves inventory.

## Performance

Requires availability snapshots for loaded products; large catalogs require more requests.

## Verification example

Compare a tracked product, a service, an unknown product and a multi-variant card. Check both display modes and a failed refresh.

These are expected behaviors derived from the implementation, not a record of
completed acceptance tests. See the [test checklist](../TESTING.md).

