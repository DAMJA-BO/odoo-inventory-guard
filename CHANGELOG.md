# Changelog

## Inventory core - Unreleased (local preview)

- Add the standalone `inventory_guard` app and one disabled-by-default policy per company.
- Add internal-location scope and independent operation switches, managed by Inventory managers.
- Validate exact-dimensional physical balances after standard lot compensation.
- Serialize participating product updates and roll back failed move-line batches.
- Add English/Spanish catalogs and Odoo transaction test cases (execution pending).
- Keep the accepted POS integration unchanged until Phase 3.
- Use Odoo 20 unified `ir.access` permissions and company restriction domains.
- Create stock-move test fixtures with Odoo 20 `reference` instead of the removed `name` field.

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
