# Phase 2 — `inventory_guard` core app

**Status: In progress — local implementation; no push authorized.**

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
English/Spanish catalogs and initial Odoo transaction tests are implemented locally.
No deployment or release acceptance is implied. Database tests, source revision
comparison and independent concurrency coverage remain pending. The existing POS
addon has not been changed to depend on the core (Phase 3).

## Goal

Create one authoritative, reusable policy engine for stock-consuming operations.
This addon becomes the Odoo application and configuration owner for the suite.

## Initial models and services

- `inventory.guard.policy`: company, sequence, active state, source-location
  scope, operation scope, action and optional product/category scope.
- `inventory.guard.mixin` or an abstract service: demand normalization, protected
  location resolution, availability calculation and shortage formatting.
- Security groups: Inventory Guard User, Manager and, when approved, Override.
- Company-aware settings bridge and menu/actions under Inventory configuration.

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

## Required technical spike

Before choosing an override, inspect Odoo 20's `stock.picking`, `stock.move`,
`stock.move.line`, `stock.quant`, scrap and inventory-adjustment flows. Document
the smallest server hook that covers completion without breaking reservation,
partial transfer, backorder or immediate-transfer behavior. Tests must prove the
hook rather than assuming every operation uses the same UI button.

## Configuration

Create **Inventory → Configuration → Inventory Guard** with:

- Global enable switch per company.
- Default action and protected location scope.
- Operation toggles for transfers, deliveries, vendor returns, scrap, inventory
  adjustments and manufacturing consumption.
- Rule priority and conflict explanation.
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

