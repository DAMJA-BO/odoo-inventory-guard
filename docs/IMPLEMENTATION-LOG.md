# Review implementation log

## RPC boundary and permissions

- Reproduced malformed checkout payloads with the actual Python parser and an
  import-only Odoo adapter: five failures and five errors before the fix.
- Validate list/object shape, 1,000-line bound, positive IDs, boolean quantities
  and float overflow; retain translated messages and positive-demand semantics.
- Execute the settings action as the manager without sudo; add cashier denial.
- Passed local Python boundary tests, static checks, translations and 15 Node tests.

## Environment

- No local Odoo, PostgreSQL, Docker, crapper, dryer or mutator executable found.
- Resolved official Odoo 20 revision for reproducible acceptance CI.
- Preserve the pre-existing untracked `.agents/` directory. No cleanup target
  was identified as safe and necessary. No push is authorized.

## Database acceptance infrastructure

- Pin Odoo 20 at `7349287698e25ca2bddddb94dcd72a2bb3f1b77b`; add clean
  installation, baseline upgrade, coverage artifacts and PostgreSQL 16 CI.
- Add independent committed transactions racing on the last unit; assert a
  serialization failure followed by rejection on a fresh transaction.
- Add persisted POS duplicate/update/deferred-stock cases and core destination,
  fractional and package cases. The remote Odoo database suite passed.
- Remaining acceptance work: actual POS request race, replay and failed picking,
  payment terminal, ship-later, upgrade value preservation, real scrap/adjustment
  entry points, backorders, serials, MRP and multi-company move completion.
- Branch protection still requires repository settings.

## First remote acceptance run

- Clean installation and all Odoo database regression tests passed.
- The last-unit race produced one completion and one serialization failure; a
  fresh retry was blocked as designed.
- Correct the evidence read to use a fresh cursor because the shell cursor keeps
  its original PostgreSQL repeatable-read snapshot.

## Accepted remote run and deployment

- The corrected workflow passed clean install, database regressions, concurrent
  last-unit behavior and upgrade from the accepted POS baseline on 2026-11-24.
- Publish the commits to `RonaldTorrez`, synchronize the `DAMJA-BO` fork and
  advance the Odoo.sh deployment submodule. The user confirmed its build passed.

## Performance pass (batched availability)

- Add `inventory.guard.availability._free_quantities`: one sudo `_read_group`
  over the `child_of` source subtree replaces one `_get_available_quantity` call
  per product. It is the same sum of quantity minus reserved quantity, verified
  against the pinned Odoo source; `_free_quantity` remains as a wrapper.
- Deduplicate policy lookups per (company, source, operation) in
  `_inventory_guard_has_policy` and test cheap conditions before the policy
  search in `_synchronize_quant`.
- Open the `stock.move.line.write` savepoint only for keys Odoo syncs quants for.
- Not changed: the POS client still refreshes the whole catalog in 200-product
  batches. Restricting it to storable products needs `is_storable` on the
  `product.product` POS record, which Odoo 20 only loads on the template; the
  server cost per batch is now one query, so the client was left alone.
- The global product-row lock is the documented trade-off in `ARCHITECTURE.md`.
- Odoo database tests for these changes run in CI only.
