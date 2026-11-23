# Block adding out-of-stock products

[Settings index](README.md) · [Configuration guide](../CONFIGURATION.md)

## Purpose

Check the selected product variant against the server before creating an order line and reject tracked products with availability at or below zero.

## When to enable

Enable this to catch unavailable selections early, including supported barcode scans.

## Settings

- Location: Point of Sale → Configuration → Settings → Stock Guard.
- Scope: the selected POS configuration.
- Technical field(s): `stock_guard_block_add`.
- Default: Off.

Boolean switch. For limits above zero, also enable Prevent quantities above available stock.

Close active POS sessions, save the selected configuration and reopen the POS
before checking the result.

## Example

With 0 available, selecting or scanning the product shows a Stock Guard alert and does not add the line. With 1 available, this setting alone can still allow a request for 2.

## Expected behavior

The cashier receives an alert identifying the requested and available quantity when stock prevents addition.

## Relationships with other settings

Works independently of badges. Combine with quantity limits to reject requests above positive stock. Keep final checkout protection enabled for authoritative validation.

## Connection and stale data

A failed live lookup blocks addition. The lookup occurs before processing positive demand, so a connection failure can also interrupt additions involving services or returns.

## Warnings and limitations

An early check does not reserve stock. Another cashier may consume it afterwards. Increasing an existing line is handled by the separate quantity-limit setting. Variant/combo configuration may occur before the stock alert.

All quantities follow the [shared availability rules](../CONFIGURATION.md#availability-rules).
No visual snapshot reserves inventory.

## Performance

Adds a server lookup to product addition; network latency can affect cashier speed.

## Verification example

Try a product with zero and positive stock, selected variants, quantity/package barcodes and returns. Confirm no line is created when verification fails.

These are expected behaviors derived from the implementation, not a record of
completed acceptance tests. See the [test checklist](../TESTING.md).

