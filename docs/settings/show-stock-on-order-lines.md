# Show stock on order lines

[Settings index](README.md) · [Configuration guide](../CONFIGURATION.md)

## Purpose

Show stock status on order lines and a count of products whose positive demand exceeds available stock.

## When to enable

Enable this to help cashiers identify the exact items that need correction in a mixed order.

## Settings

- Location: Inventory Guard → Point of Sale → select a POS.
- Scope: the selected POS configuration.
- Technical field(s): `inventory_guard_show_order`.
- Default: Off.

Boolean switch. Stock display mode also controls the line indicator presentation.

Close active POS sessions, save the selected configuration and reopen the POS
before checking the result.

## Example

With 2 available and two sale lines totaling 3, the product has a shortage. The summary counts that product once, rather than counting two lines.

## Expected behavior

Shortages show requested versus available quantity in quantity mode, a red indicator and shortage styling. Unknown quantities are shown as unknown; untracked products have no indicator once identified.

## Relationships with other settings

Works without blocking switches. Combine with quantity limits for prevention, and refresh for updated information. Low-stock warnings affect status even when the order has no shortage.

## Connection and stale data

Failed updates retain previous data with an outdated marker. The display cannot guarantee current server stock.

## Warnings and limitations

The count covers products with positive sale demand and known insufficient stock. It does not mean all uncounted products are verified. A red empty-stock status can appear even where a line is not positive sale demand.

All quantities follow the [shared availability rules](../CONFIGURATION.md#availability-rules).
No visual snapshot reserves inventory.

## Performance

No separate polling is added beyond shared availability snapshots.

## Verification example

Test duplicate lines, multiple shortage products, unknown stock, returns and both display modes. Refresh after another stock change and check the count.

These are expected behaviors derived from the implementation, not a record of
completed acceptance tests. See the [test checklist](../TESTING.md).

