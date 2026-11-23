# Highlight low stock

[Settings index](README.md) · [Configuration guide](../CONFIGURATION.md)

## Purpose

Mark positive availability at or below a configurable threshold as low stock.

## When to enable

Enable this when cashiers should distinguish low stock from normal availability.

## Settings

- Location: Point of Sale → Configuration → Settings → Stock Guard.
- Scope: the selected POS configuration.
- Technical field(s): `stock_guard_low_stock`, `stock_guard_low_threshold`.
- Default: Off; threshold 3.

Enable the switch and enter a finite, nonnegative threshold. Fractions are allowed. The number uses each product's default unit of measure.

Close active POS sessions, save the selected configuration and reopen the POS
before checking the result.

## Example

With threshold 3, availability 3 and 1 is yellow; 4 is green; 0 is red. With threshold 0, no positive quantity qualifies as low stock.

## Expected behavior

Low stock changes visible badge/order status. It does not prevent sales.

## Relationships with other settings

Enable badges and/or order-line indicators to see the warning. This switch alone does not trigger availability loading or show a warning. Display mode controls text versus colors.

## Connection and stale data

Warnings use the latest snapshot and may be outdated after a failed refresh.

## Warnings and limitations

The threshold is shared by products within this POS, not per product. A value of 3 means 3 units for one product and 3 kg for another. Multi-variant cards use their combined positive availability.

All quantities follow the [shared availability rules](../CONFIGURATION.md#availability-rules).
No visual snapshot reserves inventory.

## Performance

No independent polling is added by this switch.

## Verification example

Test threshold boundaries, fractional values, zero, invalid negative input and different POS configurations. Verify the switch alone creates no visible stock indicator.

These are expected behaviors derived from the implementation, not a record of
completed acceptance tests. See the [test checklist](../TESTING.md).

