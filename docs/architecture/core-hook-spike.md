# Core stock completion hook investigation

Status: local prototype implemented; database validation pending. Installing and
enabling the new addon activates its hooks. The accepted POS addon is unchanged.

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

## Candidate integration

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
transfers. Product/category exceptions and overrides remain pending scope decisions.

Odoo 20 unified legacy `ir.rule` and `ir.model.access` records under `ir.access`.
Security declarations must use `ir.access`, its `operation`/`domain` fields and
the `ir.access.csv` format; older security files prevent database initialization.

## Required tests before selecting the final override

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

Inspect `stock.picking`, inventory adjustment and manufacturing
callers on the deployed revision; then implement and execute Odoo transaction
tests. Pure Python or frontend tests cannot establish these database guarantees.

The local prototype uses `_synchronize_quant` after standard compensation, with a
savepoint around `_action_done` batches and completed-line writes. Persisted
`stock.move.is_inventory`, `stock.move.is_scrap` and destination usage classify
operations. Product row version writes serialize participating mutations even
when no quant exists. The transaction retry and deadlock assumptions still require
independent-connection tests on the deployed server before release.
