# Phase 5 — sales and purchases

Register **Sales** and **Purchases** under Inventory Guard when their addons are installed. See the
[central configuration contract](../architecture/centralized-configuration.md).

## `sale_inventory_guard`

A sales order does not consume stock by itself. The delivery is protected by the
core. This addon provides earlier guidance without treating today's stock as a
promise for every future delivery.

Planned behavior:

- Show current availability by warehouse on sale order lines.
- Warn when confirmation creates demand beyond current availability.
- Keep confirmation warning configurable; final delivery protection remains
  authoritative.
- Explain reservations, forecast stock and backorder consequences separately.
- Refresh advice after warehouse, quantity, product or delivery date changes.

Tests cover quotations, confirmation, multiple warehouses, routes, dropshipping,
make-to-order, partial deliveries, backorders, returns and multi-company access.
Dropship moves whose protected internal source is never used must not be blocked.

## `purchase_inventory_guard`

Normal receipts increase inventory and need no negative-stock block. This addon
focuses on vendor returns and purchasing-specific guidance.

Planned behavior:

- Show the protected source and availability before validating a vendor return.
- Reuse the core final rule; do not create a separate purchase stock formula.
- Distinguish returns from receipt corrections and incoming operations.
- Preserve standard refunds, partial returns and lot/serial selection.

Tests cover receipts, purchase returns, partial returns, drop-ship routes, owner
stock, lots/serials and returns after stock has moved elsewhere.

## Implementation order

1. Release sales guidance after core deliveries are stable.
2. Release purchasing guidance after vendor-return core tests pass.
3. Keep both addons optional so companies install only the applications they use.
4. Document which messages are advisory and which final validation is authoritative.

## Exit criteria

Users see useful early information without blocking valid future procurement,
while deliveries and vendor returns remain protected by the shared core.

