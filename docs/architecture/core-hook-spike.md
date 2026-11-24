# Core stock completion hook investigation

Status: the core hook is implemented and passed [automated Odoo 20 acceptance](../TESTING.md#automated-acceptance-evidence). The [Phase 2 manual checks](../TESTING.md#phase-2-core-acceptance) are partially verified. This investigation records how the hook was selected and what the automated evidence does not cover.

## Evidence and version boundary

Reviewed upstream Odoo `master` on 2026-11-23 through the GitHub connector:

- https://github.com/odoo/odoo/blob/master/addons/stock/models/stock_quant.py
- https://github.com/odoo/odoo/blob/master/addons/stock/models/stock_move_line.py

This is upstream development source, not proof that the deployed Odoo 20 build
uses identical code. Before enabling the hook, compare these methods against the
Odoo.sh source revision and run transaction tests on that revision.

## Findings

`stock.move.line._action_done()` processes actual `quantity_product_uom`, removes
zero lines, validates tracking, releases reservations, consumes the source and
increases the destination through `_synchronize_quant()`.

`_synchronize_quant()` calls `stock.quant._update_available_quantity()` with exact
product, location, lot, package and owner dimensions. It can temporarily create a
negative tracked quant and subsequently compensate it with untracked stock.
Rejecting every intermediate negative quant would interrupt this standard flow.

`_update_available_quantity()` also handles reservation-only updates. Its returned
availability includes reservations; it is not itself the physical quantity that
must remain nonnegative. Own reservations must not be subtracted twice.

The quant implementation can create another quant when a suitable quant cannot
be locked; it supports duplicate quants and later merges them. Locking a single
existing quant is therefore insufficient to prove concurrent last-unit safety,
especially when the exact dimensional quant does not exist yet.

Completed move-line edits and resets also synchronize quants. A check exclusively
on the picking validation button would miss these paths.

## Selected integration and early findings

Use a transaction boundary around the stock synchronization/completion flow,
evaluate the final exact-dimension physical balance after standard compensation,
and roll the entire operation back on a protected shortage. This needs an explicit
savepoint so a caller catching a UserError cannot retain partial stock writes.

Do not add an exception flag supplied through RPC context. Resolve enabled policy
from the source location's company, with explicit handling for shared locations.
An RPC caller must not choose another company to disable enforcement.

Lock ordering and transaction isolation need dedicated tests. Advisory locks alone
do not refresh a repeatable-read snapshot. The final implementation must force a
serialization conflict/retry or otherwise demonstrate fresh balance visibility
when two transactions compete for the last unit, including initially empty stock.

Operation classification must use persisted move metadata: inventory adjustments,
scrap, manufacturing consumption, deliveries, supplier returns and internal
transfers. Product/category exceptions and overrides are outside the current core scope.

Odoo 20 unified legacy `ir.rule` and `ir.model.access` records under `ir.access`.
Security declarations must use `ir.access`, its `operation`/`domain` fields and
the `ir.access.csv` format; older security files prevent database initialization.

The next Odoo.sh run reached transaction tests but their common fixture used the
removed `stock.move.name` field. Fixtures now use the writable `reference` field;
the reported five errors all occurred before stock protection was exercised.

The following run executed 31 tests and reported one failed batch-rollback
expectation. Odoo's `_action_done` may call `_free_reservation` after consuming
stock; that method can reduce other unpicked move lines. The rollback test now
marks both lines picked and asserts three actual units before validation and
after rollback. This preserves the intended excessive-completion scenario rather
than treating Odoo's legitimate adjustment of unpicked reservations as consumption.
The corrected regression later passed in the pinned CI suite.

## Verification scenarios

- Reserved exact-stock delivery succeeds without counting its reservation twice.
- Unreserved shortage fails and leaves no moves/quants partially changed, even
  when an outer caller catches the error.
- Lot compensation completes before evaluating final physical balances.
- Package, owner and lot dimensions cannot borrow unrelated stock.
- Partial quantities and backorders use actual completion quantities.
- Done-line edits and resets cannot bypass enabled protection.
- Independent transactions cannot both consume the last unit; test empty stock,
  duplicate quants, overlapping dimensions and reversed operation ordering.
- Source company and shared-location handling cannot be bypassed through context.
- Disabled configuration preserves standard behavior.

## Remaining investigation

The implemented hook uses `_synchronize_quant` after standard compensation, with
savepoints around `_action_done` batches and stock-affecting completed-line writes.
Persisted `stock.move.is_inventory`, `stock.move.is_scrap` and destination usage
classify operations. Product row version writes serialize participating mutations
even when no quant exists.

The pinned CI run exercised native stock workflows and one independent-connection
race for the last unit. One transaction completed, the other encountered a
serialization failure, and a fresh retry was blocked. That result does not cover
all concurrency permutations listed above or verify the exact deployed revision.
Inventory Barcode, custom integrations and manufacturing-specific callers require
separate acceptance.
