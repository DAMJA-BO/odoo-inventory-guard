# Block sales with insufficient stock

[Settings index](README.md) · [Configuration guide](../CONFIGURATION.md)

## Purpose

Reject checkout when the total positive demand for a tracked product exceeds unreserved stock at the POS source location.

## When to enable

Enable this for the final server-side protection, even when early checks are enabled.

## Settings

- Location: Point of Sale → Configuration → Settings → Inventory Guard.
- Scope: the selected POS configuration.
- Technical field(s): `block_negative_stock`.
- Default: Off.

Boolean switch. Inventory must update after each order. Open a new session after saving.

Close active POS sessions, save the selected configuration and reopen the POS
before checking the result.

## Example

With 2 units available, an order selling 3 units is rejected. Two separate sale lines of 2 and 1 also exceed availability. A return line does not offset positive sale demand.

## Expected behavior

Manual validation first asks the server for a shortage message. Server finalization checks persisted order lines again. A rejected transaction does not complete the order.

## Relationships with other settings

Badges, filters and early checks operate independently. They do not enable this protection. Keep this on when using early checks because another cashier can consume stock after an earlier check.

## Connection and stale data

Manual checkout requires a server connection and fails closed when verification is unavailable.

## Warnings and limitations

Ship-later orders and inventory updates at session closing are unsupported with this protection. Aggregate availability does not validate a particular lot or serial number. External stock operations do not participate in the addon checkout lock. An electronic payment may already have been charged before server rejection; verify the payment method's reconciliation/refund procedure.

All quantities follow the [shared availability rules](../CONFIGURATION.md#availability-rules).
No visual snapshot reserves inventory.

## Performance

Final validation adds server work and serializes participating checkouts for shared products.

## Verification example

Verify stock 0 rejects a sale; stock 1 accepts one unit and rejects two. Test duplicate lines, refunds, reservations and two independent cashiers competing for the last unit.

These are expected behaviors derived from the implementation, not a record of
completed acceptance tests. See the [test checklist](../TESTING.md).

