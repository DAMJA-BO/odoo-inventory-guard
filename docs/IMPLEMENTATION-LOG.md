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
  payment terminal, ship-later, upgrade value preservation, MRP and multi-company
  move completion. Phase 4 adds `TestInventoryGuardStockOperations` for native
  picking, backorder, return, scrap, inventory-count, transit and done-line paths;
  its Odoo execution remains pending until the branch CI run.
- Branch protection still requires repository settings.

## Phase 4 acceptance fixes

- The first Phase 4 CI run reported one failure and one error across 57 tests.
- Scrap quantity entry leaves the move assigned before the warning. Check that
  rejecting confirmation preserves the original quantity and source reservation.
- Configure serial tracking with elevated access only on the test fixture. Run
  receipt and delivery validation as the Inventory manager.

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

## Correctness and robustness pass

- `get_inventory_guard_availability`: a nonexistent `config_id` now raises
  `UserError` (was a bare `ValueError` from `ensure_one`); products of another
  company are omitted from the result instead of failing the 200-product batch
  with `AccessError`. The client treats omitted products as unknown. Read access
  to the products is still enforced.
- `_process_saved_order`: `demand` is initialized before the `if guarded:` block.
- `refreshInventoryGuard` logs the failure with `console.error` before failing
  closed.
- Alternative UoM: no code change. Odoo's POS line UoM is related to the product
  UoM at the pinned revision, so `qty` is already in product units. Documented.
- `block_negative_stock` independence from the core `enabled` flag: kept as
  designed and documented in `CONFIGURATION.md`; it is a decision for the owner.
- Removed the now-unused "Products must belong..." translation entries.
- Odoo database tests for these changes run in CI only.

## CI and quality pass

- `Static checks` now runs `ruff check .` (pinned 0.17.6) and `npm run lint`
  (ESLint 9, recommended rules) before the existing checks. Rule set: pyflakes,
  pycodestyle and bugbear; import sorting is off because Odoo orders imports its
  own way. Per-file ignores cover `__init__.py` re-exports, bare manifests and
  `scripts/check_concurrency.py`, which receives `env` from `odoo-bin shell`.
  The only code change was wrapping two long lines in
  `scripts/translation_terms.py` (`check_translations.py` still passes).
- All actions are pinned to commit SHAs with the version in a comment. Both
  workflows use a `concurrency` group per workflow and ref with
  `cancel-in-progress`, so a newer push stops the older run.
- `.github/dependabot.yml` proposes weekly updates for actions and npm tooling.
- `odoo.yml` gains a `Coverage floor` step (`COVERAGE_MIN`, 50). The value is a
  guess: coverage output is only visible after a CI run. Read the first run and
  raise it.
- Not done: requiring the checks in branch protection (a GitHub setting) and
  running crapper, dryer and mutator (not installed, nothing measured).
