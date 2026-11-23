# Prevent quantities above available stock

[Settings index](README.md) · [Configuration guide](../CONFIGURATION.md)

## Purpose

Reject product additions and increases whose total positive quantity exceeds available stock, including duplicate product lines.

## When to enable

Enable this to stop cashiers building quantities that an eventual checkout would reject.

## Settings

- Location: Point of Sale → Configuration → Settings → Stock Guard.
- Scope: the selected POS configuration.
- Technical field(s): `stock_guard_limit_quantity`.
- Default: Off.

Boolean switch. Comparisons use the Product Unit precision supplied by the server; there is no separate per-POS rounding setting.

Close active POS sessions, save the selected configuration and reopen the POS
before checking the result.

## Example

With 3 available and 2 already in the order, adding 2 more is rejected. Two separate lines still count together. Reducing an excessive quantity remains possible.

## Expected behavior

An alert or standard quantity error explains requested and available stock. Missing or failed stock data prevents an increase.

## Relationships with other settings

Product addition fetches live availability. Editing an existing line uses the latest snapshot. Automatic/manual refresh improves that snapshot. Final checkout protection remains independently necessary.

## Connection and stale data

Addition fails when live verification fails. Increases are rejected when the snapshot is missing or marked failed. A previous snapshot may still appear fresh until a request detects lost connectivity.

## Warnings and limitations

Refunds do not offset positive demand. Reductions and return orders bypass the increase restriction. Combo child demand is checked before changing the parent. Alternative UoM and third-party product flows need deployment-specific acceptance tests.

All quantities follow the [shared availability rules](../CONFIGURATION.md#availability-rules).
No visual snapshot reserves inventory.

## Performance

Addition uses server requests; normal quantity editing checks the in-memory snapshot.

## Verification example

Test duplicate lines, fractional quantities, combos, reductions, returns, unknown stock and a failed refresh. Verify another cashier's sale is detected on final checkout.

These are expected behaviors derived from the implementation, not a record of
completed acceptance tests. See the [test checklist](../TESTING.md).

