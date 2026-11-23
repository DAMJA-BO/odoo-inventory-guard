# Stock display mode

[Settings index](README.md) · [Configuration guide](../CONFIGURATION.md)

## Purpose

Choose how stock badges and order-line indicators present availability.

## When to enable

Use quantity mode for explicit stock figures, or color mode for a compact visual status.

## Settings

- Location: Point of Sale → Configuration → Settings → Inventory Guard.
- Scope: the selected POS configuration.
- Technical field(s): `inventory_guard_display_mode`.
- Default: quantity.

Select quantity (Quantity, text and colors) or color (Colors only). Exactly one mode is selected.

Close active POS sessions, save the selected configuration and reopen the POS
before checking the result.

## Example

At 2 units with a low-stock threshold of 3, quantity mode shows Low stock: 2 with a warning color. Colors-only mode shows a colored marker with a tooltip and accessible label.

## Expected behavior

The selected mode applies to both product badges and order-line indicators.

## Relationships with other settings

Enable Show stock badges and/or Show stock on order lines to see this setting. Highlight low stock controls the yellow status. Blocking and filter behavior are unchanged by the display mode.

## Connection and stale data

The display uses the last snapshot; changing presentation does not improve its freshness.

## Warnings and limitations

Colors-only mode is a presentation preference, not a permission boundary for hiding stock data: labels and tooltips still contain stock information. Unknown availability must not be interpreted as zero.

All quantities follow the [shared availability rules](../CONFIGURATION.md#availability-rules).
No visual snapshot reserves inventory.

## Performance

Presentation adds no separate server polling.

## Verification example

Switch modes with badges and order indicators enabled. Verify tooltips, accessible labels, shortage status and unchanged blocking behavior.

These are expected behaviors derived from the implementation, not a record of
completed acceptance tests. See the [test checklist](../TESTING.md).

