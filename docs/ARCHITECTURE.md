# Architecture

## Optional stock UI

The settings bridge exposes per-POS fields through Odoo 20's
`res.config.settings`, using the standard `pos_` related-field convention.
The standalone Stock Guard block is attached to the native POS settings app.

- `stock/policy.js`: pure demand, UoM comparison and display-state calculations.
- `stock/runtime.js`: reactive in-memory snapshots, isolated by POS configuration.
- `stock/store_patch.js`: bounded snapshot RPC, catalog filter and pre-creation checks.
- `stock/order_line_patch.js`: synchronous quantity checks, including combo children.
- `stock/components_patch.js`: card/line presentation and product-screen polling lifecycle.
- `stock/stock_guard.xml` and `stock_guard.scss`: inherited UI templates and styling.

The public snapshot RPC checks POS group membership, configuration read access,
allowed company and product access. It uses the same free-stock calculation as
the final validator. Snapshots are advisory, not reservations. Failed refreshes
are visible; all authoritative transaction checks remain server-side.

## Request flow

The payment-screen patch invokes `pos.config.check_pos_stock` before manual
validation. This authenticated RPC returns a user-friendly shortage message and
never reserves stock. It cannot replace the authoritative check.

`pos.order._process_order` records whether the incoming order is a new finalization
or a replay. Odoo then creates/updates its lines and invokes `_process_saved_order`.
That hook aggregates persisted lines, checks availability, delegates to standard
finalization and verifies that the immediate stock transfer finished. A failure
raises `UserError`, rolling back the enclosing database transaction.

The context flag is overwritten by the entry hook rather than trusted from the
incoming context. Direct custom finalization paths that bypass `_process_order`
must explicitly integrate the policy; this is not a constraint on every write
to `pos.order` or every stock move.

## Concurrency

The authoritative check writes each product row in sorted ID order. The no-op
write creates a PostgreSQL row version, serializing participating checkouts and
causing stale repeatable-read transactions to retry through standard Odoo request
handling. A SELECT lock alone would not refresh a repeatable-read snapshot.
Never catch a serialization error here and never manually commit.

This coarse lock spans companies and warehouses sharing a product. It trades
throughput for a small, reviewable implementation. Inventory operations outside
this addon do not participate in this product lock. Acceptance tests must include
concurrent checkouts over separate requests, not only sequential test cursors.

## Extension points

- `pos.stock.guard._aggregate_demand`: input validation and positive demand.
- `pos.stock.guard._shortage_message`: supported stock policy and availability.
- `pos.config.check_pos_stock`: authenticated advisory endpoint.
- `pos.order._process_saved_order`: authoritative checkout integration.

Do not rename the technical module after deployment without migrations. The
Odoo 20 hooks are internal APIs; inspect upstream diffs before upgrading Odoo.
