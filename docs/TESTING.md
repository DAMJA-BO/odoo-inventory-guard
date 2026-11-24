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

## Automated acceptance evidence

On 2026-11-24, addon commit `ece0440` passed [Odoo acceptance](https://github.com/ronaldtorrez/odoo-inventory-guard/actions/runs/45473072548): clean installation of both addons, database regressions (including `TestInventoryGuardStockOperations`), the coverage floor, independent stock-move transactions competing for the last unit, and installation of the core while upgrading the accepted POS baseline. The stock-move race is not a POS checkout race, and the upgrade run does not compare saved settings across existing POS configurations.

The Odoo.sh `development` build for deployment commit `eb81a1a` was reported successful. Neither this build nor that CI run validates later changes or replaces the deployment-specific manual checks below.

## Phase 2 core acceptance

**Automated acceptance: passed. Manual acceptance: pending.**

Use a disposable database or an isolated copy of Odoo.sh `development` with synthetic stock. Use separate Inventory manager and Inventory user accounts for the access checks; do not use a superuser. Do not change a live company's policy to test defaults.

- [ ] On a fresh database, install `inventory_guard` without POS. Open **Inventory Guard → Overview, General, and Operations** as a manager. General and Operations must open the same company policy, with protection disabled by default.
- [ ] As an Inventory user without manager permissions, verify that Overview is readable for allowed companies and that management menus and policy edits are unavailable.
- [ ] As a manager allowed in two test companies, enable protection in company A only. Switch to company B and verify its settings are independent. With a user allowed only in A, verify that B's policy is not visible or editable.
- [ ] In company A, enable delivery protection for a test internal source (or its parent). Put two units of a storable product without lot or serial tracking there and validate a delivery of exactly two. It must reach **Done**, leaving zero physical units at the source.
- [ ] Replenish the same source to two units. Enter three as the quantity to complete on a new delivery and validate. Expect an Inventory Guard shortage message, a delivery that is not **Done**, and unchanged physical stock at both source and destination. Compare quantities immediately before and after validation, not before entering the delivery quantities.

Record the test date, build and database, company and role, scenario result, and any message or stock evidence. Close manual Phase 2 acceptance only after all applicable core scenarios pass. Inventory Barcode, POS, payments and manufacturing integration are tracked separately.

## Suite acceptance checklist

- [ ] Install Spanish, upgrade the addon and verify settings and POS messages in Spanish.
- [ ] Switch back to English and verify dynamic quantities and shortage messages.
- [ ] On a build containing the bilingual descriptions, open General, Operations and
  Point of Sale in English and Spanish. Confirm the descriptions are visible without
  hovering and legible in light and dark themes. Disable low-stock warnings and
  automatic refresh separately: the corresponding label, field and description
  must disappear together. Confirm POS settings remain read-only with an active session.
- [ ] Verify Inventory Guard is included in frontend translation modules.
- [ ] Open Inventory Guard → Point of Sale; compare two POS configurations.
- [ ] Open the native POS shortcut and confirm it selects the same POS.
- [ ] Verify manager-only sections, active-session read-only behavior and company isolation.
- [ ] Upgrade an existing database with saved POS values and compare every value.
- [ ] On a fresh POS configuration, optional cashier feature switches start off.
  On upgrade, existing checkout protection retains its saved value.
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
- [ ] Complete Inventory Barcode and deployment-specific POS/payment smoke tests;
  mocked POS tests do not prove those UI workflows.

Release only after recording the applicable deployment-specific manual results.
