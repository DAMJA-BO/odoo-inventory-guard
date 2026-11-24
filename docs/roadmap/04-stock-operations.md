# Phase 4 — stock operations

**Status: Automated Odoo 20 acceptance passed; deployment checks pending.**

This phase validates the existing **Inventory Guard → Operations** controls. See
[automated acceptance evidence](../TESTING.md#automated-acceptance-evidence).

## Goal

Validate the core across every Inventory operation that can reduce protected stock.
This phase extends core behavior and tests; it does not introduce another addon.

## Operation matrix

| Operation | Protected source | Expected behavior |
| --- | --- | --- |
| Internal transfer | Internal location | Validate actual moved quantity; destination increase is allowed |
| Customer delivery | Internal location | Block insufficient completion; partial/backorder remains possible |
| Vendor return | Internal location | Block quantities exceeding protected source stock |
| Scrap | Internal location | Block excessive scrap and identify source shortage |
| Negative inventory adjustment | Internal location | Prevent a resulting negative quant, subject to the correction policy |
| Receipt | Supplier/virtual location | Do not block because protected stock increases |
| Customer return | Customer/virtual location | Do not block because protected stock increases |
| Internal → transit | Internal location | Protect the internal source under the transfers switch |
| Transit → internal | Transit location excluded | Leave the transit source to standard Odoo; allow the internal credit |

## Automated coverage

`TestInventoryGuardStockOperations` exercises native picking validation, partial
completion and backorders, receipts and returns, both transit legs, scrap wizard
confirmation, inventory counts, serial selection and rollback when editing a
completed delivery. Core regression tests separately cover own reservations,
fractional quantities and exact lot, package and owner dimensions.

## Pending deployment checks

Use the [suite checklist](../TESTING.md#suite-acceptance-checklist) for Inventory
Barcode and any installed integrations that invoke stock validation. Native
server workflow tests do not establish coverage of those clients or custom API
paths.

## Recorded policy decisions

Transit sources remain excluded. An internal-to-transit move still consumes a
protected internal source; a transit-to-internal move does not protect the transit
source. This is deliberately not a new transit setting.

A positive inventory correction may improve an already-negative balance, while a
further consumption that worsens the negative balance is blocked. There is no
manager override or audit exception in this phase; the audit/exception design is
reserved for Phase 7. Do not silently bypass every inventory adjustment.

## Exit criteria

All matrix operations behave predictably through UI and server paths, with no
regression to reservations, partial transfers, backorders or incoming stock.

