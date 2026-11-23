# Enable Available only filter

[Settings index](README.md) · [Configuration guide](../CONFIGURATION.md)

## Purpose

Expose a temporary catalog filter that the cashier can toggle to show products with positive known availability.

## When to enable

Enable this when cashiers want an optional way to browse available stock.

## Settings

- Location: Point of Sale → Configuration → Settings → Stock Guard.
- Scope: the selected POS configuration.
- Technical field(s): `stock_guard_available_filter`.
- Default: Off.

Boolean setting permits the button. The cashier's runtime filter starts off and is not saved as a permanent POS preference.

Close active POS sessions, save the selected configuration and reopen the POS
before checking the result.

## Example

Enable the setting, open the POS, then turn on Available only. A known zero-stock product disappears from the catalog; turning the button off shows it again.

## Expected behavior

Filtering changes the catalog, not existing order lines. Unknown and untracked products remain visible.

## Relationships with other settings

Uses snapshots shared with badges and refresh. A template stays visible if its variants have combined positive availability. Selected-variant validation is independent.

## Connection and stale data

The filter continues using the last snapshot after failure, so catalog visibility can be outdated.

## Warnings and limitations

This is not a stock guarantee or permanent product-hiding rule. A visible template may include an unavailable variant. Refreshing can change which products appear while the filter is active.

All quantities follow the [shared availability rules](../CONFIGURATION.md#availability-rules).
No visual snapshot reserves inventory.

## Performance

Filtering is local; fetching availability has the shared snapshot cost.

## Verification example

Toggle on/off with positive, zero, negative, unknown and untracked stock. Verify existing order lines remain and multi-variant templates behave as documented.

These are expected behaviors derived from the implementation, not a record of
completed acceptance tests. See the [test checklist](../TESTING.md).

