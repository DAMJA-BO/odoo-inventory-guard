# Testing Odoo 20

## Local static checks

```bash
python scripts/check_project.py
node --input-type=module --check < pos_inventory_guard/static/src/app/payment_screen_patch.js
```

These checks do not import Odoo or prove runtime compatibility.

Lint Python with ruff (`pip install ruff==0.17.6`, configured in `ruff.toml`) and
JavaScript with ESLint (`npm ci`, configured in `eslint.config.js`):

```bash
ruff check .
npm run lint
```

The `Static checks` workflow runs both before the other checks.

Run the dependency-free frontend policy and boundary tests with Node 22 or newer:

```bash
npm test
```

The boundary adapter executes the actual store and order-line patches with fake
Odoo services. It verifies duplicate demand, barcode/packaging quantities, returns,
combos, disabled controls, snapshot failures, filtering, isolated configurations,
and serialized bounded requests. It does not replace rendering or real POS tests.

## Odoo regression tests

The `Odoo acceptance` workflow pins Odoo to
`7349287698e25ca2bddddb94dcd72a2bb3f1b77b`, installs both addons against
PostgreSQL 16, runs database tests, and upgrades the renamed POS baseline.
Logs and Python coverage are retained as artifacts, and a `Coverage floor` step
fails the run below `COVERAGE_MIN` (currently 50, deliberately low: the real figure
has not been read from a run yet, so raise it once it is known). Require both the
`Static checks` and `Odoo acceptance` checks in branch protection before merging
release candidates; repository administrators must configure that GitHub setting,
it cannot be set from the repository. A configured workflow is not a passed
acceptance run.

Actions are pinned to commit SHAs (the version is in a trailing comment) and
Dependabot proposes weekly updates for them and for the npm dev tooling.

The mutation, duplication and complexity tools mentioned in the contributor
workflow (crapper, dryer, mutator) are not installed here, so no complexity,
duplication or mutation score has been measured.

On a disposable database with Odoo 20 and PostgreSQL:

```bash
odoo-bin -d inventory_guard_test --addons-path=/path/to/odoo/addons,/path/to/repository \
  -i inventory_guard,pos_inventory_guard --test-enable --test-tags /inventory_guard,/pos_inventory_guard --stop-after-init
```

Tests cover aggregation, finite input, available quantity, reservations, refunds,
untracked products, missing products and deferred inventory updates. Extend tests
for the deployment's payment methods and installed addons before release.

For upgrade coverage, record the values of two existing POS configurations before
upgrading both addons from the prior release. Include a POS with checkout enabled
and a POS with checkout disabled in the same company. Compare both records after
the upgrade, without uninstalling either addon.

## Acceptance checklist

- [ ] Install Spanish, upgrade the addon and verify settings and POS messages in Spanish.
- [ ] Switch back to English and verify dynamic quantities and shortage messages.
- [ ] Verify Inventory Guard is included in frontend translation modules.
- [ ] Install the core alone and open Overview, General and Operations.
- [ ] Open General and Operations for the first time; both use the same disabled policy.
- [ ] Change the active company and confirm independent policies and permissions.
- [ ] Open Inventory Guard → Point of Sale; compare two POS configurations.
- [ ] Open the native POS shortcut and confirm it selects the same POS.
- [ ] Verify manager-only sections, active-session read-only behavior and company isolation.
- [ ] Upgrade an existing database with saved POS values and compare every value.
- [ ] All new switches start off; existing checkout protection retains its value on upgrade.
- [ ] Cards display stock; verify colors-only mode, tooltips and untracked products.
- [ ] Multi-variant cards show combined availability; addition checks the chosen variant.
- [ ] Zero stock is rejected on click, barcode scan and weighted/package scans with early blocking.
- [ ] Quantity limits include duplicate lines and combo children; reductions and returns remain possible.
- [ ] Order indicators and the shortage count update when quantities or stock change.
- [ ] Available only starts off and can be toggled; unknown and untracked products remain visible.
- [ ] Enable/disable low-stock warnings and try custom fractional thresholds.
- [ ] Refresh manually and automatically; verify custom intervals and last-update time.
- [ ] Leave/reopen the product screen; polling stops/restarts without duplicate timers.
- [ ] Disconnect/reconnect; stale quantities are marked and early checks fail closed.
- [ ] Complete a sale and verify refreshed quantities on the product screen.

- [ ] Install and upgrade the addon; confirm the inherited settings view loads.
- [ ] With the POS toggle off, verify ordinary checkout outside protected stock operations.
- [ ] With POS checkout protection on and company policy off, verify zero-stock rejection.
- [ ] With company delivery protection on and POS checkout protection off, verify covered
  outgoing transfers still cannot reduce source stock below zero.
- [ ] Stock 0 blocks a tracked product; stock 1 accepts one unit and blocks two.
- [ ] Duplicate product lines cannot bypass the limit; fractional UoM rounds correctly.
- [ ] Reserved quantities are excluded; refunds and services behave as documented.
- [ ] Updating/deleting lines of a saved draft checks the final persisted demand.
- [ ] Replaying the same finalized UUID does not create another transfer.
- [ ] Deferred stock configuration and ship-later orders are rejected.
- [ ] Invalid lots/serials or failed transfers roll back server finalization.
- [ ] Two independent POS requests competing for the last unit cannot both succeed.
- [ ] Offline manual checkout fails closed; reconnecting permits retry.
- [ ] Test automatic electronic payment; confirm reconciliation/refund procedure on rejection.
- [ ] Test a cashier without inventory-manager access and two allowed companies.
- [ ] Unauthorized users/companies cannot use the advisory RPC.
- [ ] Test installed integrations, bundles, routes and returns using synthetic data.
- [ ] Run `TestInventoryGuardStockOperations` through the pinned Odoo/PostgreSQL
  workflow. It exercises native picking, backorder, return, scrap and inventory
  counting entry points and checks exact source/destination balances.
- [ ] Complete Inventory Barcode and deployment-specific POS/payment smoke tests;
  mocked POS tests do not prove those UI workflows.

Automated Odoo runtime acceptance passed on 2026-11-24 for addon commit
`2ee7399c184359fe7453ded8dde7d464feeac1c1` and the pinned Odoo revision above.
The run covered clean installation, database tests, independent last-unit
transactions and upgrade from the accepted POS baseline. Release only after
recording the deployment-specific manual checklist results as well.
