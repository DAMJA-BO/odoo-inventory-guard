# Changelog

## Versions

| Addon | Manifest version | Notes |
|---|---|---|
| `pos_inventory_guard` | `20.0.3.0.0` | Last tagged release: `pos-stock-guard-20.0.2.0.1` |
| `inventory_guard` | `20.0.2.0.0` | New addon, not released before this suite |

The addons are versioned independently. Sections marked *Unreleased* below are
not tagged yet; the entries above `20.0.2.0.1` belong to the manifests listed here.

## Review hardening — Unreleased

- Validate malformed checkout payloads, positive product IDs and bounded demand.
- Exercise settings navigation without superuser privileges and deny cashier access.
- Add pinned Odoo/PostgreSQL installation and upgrade CI with coverage artifacts.
- Add independent transaction concurrency and persisted-order regression scenarios.
- Expand core tests for destinations, fractional quantities and package isolation.
- Database acceptance remains pending; see `docs/IMPLEMENTATION-LOG.md`.
- Compute free stock for a whole POS snapshot or shortage check with one quant query.
- Resolve the stock policy once per source and operation, and skip the done-line
  savepoint for writes that cannot change quants.
- Report a missing POS as a user error in the availability snapshot, and skip
  products of other companies instead of rejecting the whole batch.
- Lint Python (ruff) and JavaScript (ESLint) in CI, and add a coverage floor to
  the Odoo acceptance workflow.
- Pin GitHub Actions to commit SHAs, add Dependabot for actions and npm, and
  cancel superseded runs of the same ref.
- Log stock refresh failures in the POS client; initialize order demand before use.
- Document that POS lines use the product unit and that the POS switch is
  independent of the core policy.
- Add Phase 4 workflow acceptance coverage for native picking, backorders,
  returns, scrap, inventory counts, transit legs and done-line rollback.

## Centralized configuration — Unreleased

- Add Overview, General, Operations and per-POS configuration to Inventory Guard.
- Replace editable native POS settings with a shortcut to the selected POS.
- Preserve saved POS values and move availability and product locking into the core.
- Add an explicit POS dependency on the core and update English and Spanish catalogs.
- Add navigation regression tests and a clean-install and upgrade checklist.
- Mark the active-session notice as an accessible status message for Odoo 20 views.

## Inventory core - Unreleased (local preview)

- Add the standalone `inventory_guard` app and one disabled-by-default policy per company.
- Add internal-location scope and independent operation switches, managed by Inventory managers.
- Validate exact-dimensional physical balances after standard lot compensation.
- Serialize participating product updates and roll back failed move-line batches.
- Add English/Spanish catalogs and Odoo transaction test cases; automated Odoo 20 execution passed.
- Keep the accepted POS integration unchanged until Phase 3.
- Use Odoo 20 unified `ir.access` permissions and company restriction domains.
- Create stock-move test fixtures with Odoo 20 `reference` instead of the removed `name` field.
- Mark batch-rollback fixtures as picked so Odoo cannot reduce a future unpicked reservation during completion.

## Identity migration - Unreleased

- Rename the suite repository to Odoo Inventory Guard and its POS addon to
  `pos_inventory_guard`, including models, settings, assets and translation domains.
- Retain the POS behavior and module version during the clean-install rename.
- Document the rollback point, clean-database verification and pending fork rename.

## 20.0.2.0.1 - Unreleased

- Add English and general Spanish catalogs for settings and POS messages.
- Expose Inventory Guard translations through the Odoo 20 frontend translation hook.
- Add translation coverage and placeholder checks to CI.
- Document language activation, translation maintenance and per-setting behavior.

## 20.0.2.0.0 - Unreleased

- Add a dedicated Inventory Guard section with independent settings per POS.
- Add optional stock badges, colors-only mode, order-line indicators and shortage counts.
- Add optional early addition checks and quantity limits, including barcode quantities.
- Add a temporary Available only filter and configurable low-stock threshold.
- Add manual refresh and optional polling (30 seconds by default, minimum 5 seconds).
- Display source location, last catalog update and failed-refresh status.
- Preserve existing checkout enforcement and keep all new switches off by default.
- Add frontend boundary tests and backend settings/snapshot regression tests.

## 20.0.1.0.2 - Unreleased

- Display the stock-blocking option in the Odoo 20 Point of Sale settings page.
- Add a regression test for saving the option on the selected POS configuration.
- Keep the option read-only while that POS has an active session.

## 20.0.1.0.1 - Unreleased

- Preserve all standard Odoo 20 POS configuration fields during data loading.
- Add regression coverage for the standard `use_pricelist` loader field.
- Create test fixtures with explicit elevated privileges.

## 20.0.1.0.0 - Unreleased

- Introduce Odoo POS Inventory Guard (`pos_inventory_guard`).
- Extract stock policy into a small abstract model.
- Validate persisted lines rather than manually interpreting x2many commands.
- Check authenticated POS access and allowed companies on the advisory endpoint.
- Serialize participating checkouts with product row writes and transaction retries.
- Reject deferred inventory, ship-later orders and incomplete stock transfers.
- Add English documentation, regression tests and Apache 2.0 attribution.

This replaces an unpublished prototype; no runtime compatibility claim is made
until the Odoo 20 acceptance suite has passed.
