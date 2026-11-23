# Centralized configuration

Inventory Guard is the configuration entry point for the suite. The core provides
Overview, General and Operations. An extension that ships settings adds a section
under `inventory_guard.inventory_guard_root`. The section is available only if
its extension is installed and the user has permission to access it.

Company activation, locations and protected operation types live on one
`inventory.guard.policy` per company. General and Operations open the same
record for the active company. If missing, the first manager opening either
screen creates it disabled. Point of Sale reads and edits settings on
`pos.config`. Its native settings views link directly to the selected record.

Use existing model permissions and company scope for lists, forms and shortcuts.
Use dedicated views so extension pages do not replace the host application's
default form. Future integrations may provide a native shortcut, with editable
settings owned by the central app. Update the setting reference, roadmap,
translations and acceptance checklist whenever a section changes.

## POS compatibility and enforcement

Upgrade both addons on an existing database. The original POS fields and values,
including `block_negative_stock`, are reused in place. Keeping the switch at
POS scope preserves mixed enabled and disabled configurations within one company.

The POS order hook checks persisted demand and successful immediate stock
completion. It delegates availability, shortage formatting and product locking
to the core. The company policy checks exact physical move balances for
protected operations. These checks address different stages of stock consumption.
Keep the POS order hook until Odoo 20 tests prove complete coverage of finalization,
failed transfers and replays through a replacement.
