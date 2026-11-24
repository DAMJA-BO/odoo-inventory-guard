# Phase 4 — stock operations

Extend **Inventory Guard → Operations** for new stock-operation controls. See the
[central configuration contract](../architecture/centralized-configuration.md).

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

## Implementation steps

1. Build synthetic fixtures for every row in the matrix.
2. Verify standard reservation and detailed-operation workflows.
3. Support immediate transfers and partial quantities without using planned
   demand as completed demand.
4. Verify lot/serial, package and owner dimensions.
5. Add operation-specific translated shortage context where the generic message
   is insufficient.
6. Test barcode-driven Inventory flows and server/API validation paths.
7. Document policy decisions for adjustments and transit locations.

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

