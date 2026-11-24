# Phase 2 — `inventory_guard` core app

**Status: Implemented — automated Odoo 20 acceptance passed; manual acceptance partially verified.**

See [Phase 2 acceptance evidence and manual checklist](../TESTING.md#phase-2-core-acceptance). A successful Odoo.sh build is not manual acceptance.

The [hook investigation](../architecture/core-hook-spike.md) records upstream
findings, version limitations and the transaction tests required before enabling
an authoritative core hook.

## Confirmed decisions and local delivery

- Block only; no warning mode or override permission.
- Internal locations only; transit excluded.
- One policy per company, optionally scoped to location subtrees.
- No product/category exceptions or rule priority conflicts in the initial version.
- Positive corrections may improve existing negatives; further consumption may not.
- Reuse Inventory User/Manager groups initially instead of introducing redundant
  permissions; company record rules apply to policy management.

The standalone app, policy configuration, completion/synchronization hooks,
English/Spanish catalogs and Odoo transaction tests are implemented. The POS
addon depends on the core as part of Phase 3.

## Goal

Create one authoritative, reusable policy engine for stock-consuming operations.
This addon becomes the Odoo application and configuration owner for the suite.

## Implemented models and services

- `inventory.guard.policy`: one policy per company, with activation, source-location
  scope and operation switches.
- `inventory.guard.availability` and stock move-line hooks: shared stock and
  product-locking helpers, with exact physical-balance checks on completion.
- Existing Inventory User and Manager groups, with company record rules.
- Company-aware settings in the central Inventory Guard app.

Avoid adding stored availability fields. Odoo quants, reservations and move lines
remain the source of truth.

## Policy semantics for the first release

- Protect stock leaving internal source locations.
- Evaluate the quantity actually being completed, not the unprocessed demand.
- Account for reservations owned by the operation under validation.
- Group demand by product and, when applicable, lot/serial, package and owner.
- Ignore incoming moves from supplier/production/inventory virtual locations.
- Prevent a protected quant result below zero using Odoo's product UoM precision.
- Return actionable shortages with operation, source location, requested and
  available quantities.
- Lock participating records in deterministic order and rely on Odoo transaction
  retry behavior for concurrent validation.

## Selected stock hooks

The core checks physical balances in `stock.move.line._synchronize_quant` after
standard Odoo synchronization and lot compensation. Savepoints around
`_action_done` and stock-affecting edits to completed lines preserve rollback.
See the [hook investigation](../architecture/core-hook-spike.md) and the
[Phase 4 workflow coverage](04-stock-operations.md#automated-coverage).

## Configuration

Use **Inventory Guard → General / Operations** for:

- Global enable switch per company.
- Protected source-location scope. The action is always to block.
- Operation toggles for transfers, deliveries, vendor returns, scrap, inventory
  adjustments and manufacturing consumption.
- Manager security assignment and clear indication of active company.

The first version should prefer a small deterministic rule set. Product/category
exceptions can be deferred if they make rule precedence ambiguous.

## Implementation steps

1. Write the Odoo 20 hook spike and transaction tests.
2. Define models, access controls, record rules and company isolation.
3. Implement pure demand and policy-resolution services.
4. Implement exact-dimension availability and concurrency protection.
5. Integrate the chosen final stock-operation hook.
6. Add settings, policy views, menus and translated messages.
7. Add migration-safe defaults: installed but disabled until configured.
8. Document settings, architecture and extension API.

## Tests

Cover exact stock, insufficient stock, reservations, own reservations, duplicate
moves, fractional UoM, lots/serials, packages, owners, multi-company access,
location hierarchy, concurrent last-unit operations, partial validation and
backorders. Verify disabled policy preserves standard Odoo behavior.

## Exit criteria

Generic protected operations cannot complete with negative source stock, while
valid reserved, partial and incoming operations continue to work as standard Odoo.

