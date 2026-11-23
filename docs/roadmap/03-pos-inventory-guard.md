# Phase 3 — `pos_inventory_guard`

## Goal

Migrate the proven POS behavior to the shared core without losing cashier guidance
or creating two competing stock calculations.

## Responsibilities retained in the POS addon

- Product-card badges and quantity/color display modes.
- Early zero-stock and quantity checks.
- Order-line indicators and shortage summary.
- Available-only filter, low-stock threshold and refresh lifecycle.
- POS-specific settings per POS and frontend translations.
- Manual checkout feedback before payment validation.

## Responsibilities moved to the core

- Company/location policy resolution.
- Authoritative availability and shortage calculation.
- Generic concurrency and final stock-operation protection.
- Shared permission and exception semantics.

## Implementation steps

1. Make the renamed addon depend on `inventory_guard` and `pos_stock`.
2. Replace private server calculations with documented core services.
3. Map each POS configuration to the applicable company/location policy.
4. Retain the persisted-order checkout check until tests prove the generic final
   hook covers every POS finalization and replay path; then remove duplication.
5. Preserve current defaults and behavior for existing settings.
6. Update UI terminology to Inventory Guard while keeping concise cashier text.
7. Regenerate English and Spanish catalogs and update settings documentation.

## Compatibility tests

Repeat all current POS tests: duplicate lines, returns, services, barcodes,
weighted/package scans, combos, variants, stale snapshots, filtering, polling,
replays, failed transfers, electronic payment behavior and two cashiers competing
for the last unit. Add tests proving the core and POS do not double-count demand.

## Exit criteria

The cashier experience matches the accepted POS-only release, while final policy
and availability come from the shared core and no duplicate transfer is created.

