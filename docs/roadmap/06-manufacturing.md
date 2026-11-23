# Phase 6 — `mrp_inventory_guard`

## Goal

Protect raw-material and finished-product consumption while preserving standard
Odoo manufacturing, partial production and backflush behavior.

## Covered flows

- Manufacturing-order component consumption.
- Additional and manually adjusted consumption.
- Partial production and remaining quantities.
- Backflush and work-order completion.
- By-products and scrap generated from manufacturing.
- Unbuild orders, where finished products are consumed.
- Lot/serial-tracked components and finished products.

## Design

The core protects final stock moves. The MRP addon adds a component-shortage view
before completion, grouped by source location and exact component. Finished goods
and by-products usually increase stock and are not constrained; an unbuild consumes
the finished product and therefore is constrained.

## Implementation steps

1. Map every Odoo 20 MRP completion path and generated stock move.
2. Add advisory component availability using core services.
3. Validate actual consumed quantities at finalization.
4. Preserve flexible-consumption behavior without allowing protected negative stock.
5. Handle partial production and backorders without checking the entire original BOM
   as if it were consumed immediately.
6. Add translated messages identifying product, lot and source location.
7. Test work orders, backflush, scrap, by-products and unbuild independently.

## Tests

Cover exact/insufficient components, reservations, alternate components where
installed, partial production, flexible consumption, lot/serial tracking, extra
consumption, simultaneous manufacturing orders and rollback after a failed check.

## Exit criteria

Manufacturing cannot consume protected stock below zero, and valid partial,
backflush, by-product, scrap and unbuild operations retain standard Odoo behavior.

