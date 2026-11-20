# Changelog

## 20.0.2.0.0 - Unreleased

- Add a dedicated Stock Guard section with independent settings per POS.
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

- Introduce Odoo POS Stock Guard (`pos_stock_guard`).
- Extract stock policy into a small abstract model.
- Validate persisted lines rather than manually interpreting x2many commands.
- Check authenticated POS access and allowed companies on the advisory endpoint.
- Serialize participating checkouts with product row writes and transaction retries.
- Reject deferred inventory, ship-later orders and incomplete stock transfers.
- Add English documentation, regression tests and Apache 2.0 attribution.

This replaces an unpublished prototype; no runtime compatibility claim is made
until the Odoo 20 acceptance suite has passed.
