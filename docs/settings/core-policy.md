# Core inventory protection

Status: local development preview, awaiting Odoo 20 database acceptance.

## Installation and access

Install `inventory_guard` on a disposable Odoo 20 database. This is a separate app;
the existing `pos_inventory_guard` remains independently installable for now.
Open **Inventory → Configuration → Inventory Guard**, or the Inventory Guard app.
Inventory users may read policies; Inventory managers may manage them, subject
to allowed-company record rules. No separate override permission exists.

## Company and activation

Create one policy for each company requiring protection. Installation creates no
enabled policy. The **Enable inventory protection** switch starts off. The source
location company selects the rule; shared locations use the persisted move-line
company. Changing the active company in the browser is not a policy bypass.

## Locations and operations

Empty **Protected source locations** means all internal source locations. Selecting
a location includes its internal descendants. Transit and virtual sources are
excluded. A location from another company cannot be selected.

Transfers, deliveries, vendor returns, scrap, adjustments and manufacturing each
have a switch, initially on within a policy. They take effect only after the global
enable switch is on. Disabling an operation restores standard Odoo behavior for
that operation, including its ability to create negative stock.

Example: with deliveries on and transfers off, an excessive customer delivery is
blocked; the same quantity transferred internally follows standard Odoo behavior.
Manufacturing classification uses a production destination; routing-specific
coverage must be validated in the later manufacturing phase.

## Quantities and reservations

Protection checks physical balance in the exact product/location/lot/package/owner
dimensions after Odoo synchronization and lot compensation. It does not subtract
the operation's reservation twice and does not store copied availability fields.
With two physical units, completing two is allowed and completing three is rejected.
Unrelated lots, packages or owners cannot cover a shortage in another dimension.

Incoming stock is permitted. Existing negatives may be improved by positive stock
corrections, even if the remaining balance is still negative. Further consumption
of negative stock is rejected. There are no product/category exceptions, warning
mode or manager bypass in this version.

## POS interaction

The existing POS checks remain configured per POS. The core can still reject a
stock operation even if the POS's early UI checks are disabled. Core protection
does not automatically add stock badges or replace the POS free-stock checks.

## Verification required before release

Run with both modules selected: `inventory_guard,pos_inventory_guard`. Keep tests
enabled and verify both English and Spanish after installation/upgrade.

New transaction tests cover disabled behavior, zero/exact stock, duplicate-line
batch rollback, reservations, operation switches, positive correction and transit.
They require a running Odoo server and PostgreSQL and have not been run locally.
Before acceptance, add/run separate-cursor concurrent last-unit tests, lots,
packages, owners, multi-company permissions, done-line edits, partials and backorders.
Compare the server hooks with the deployed Odoo 20 revision. See the
[hook investigation](../architecture/core-hook-spike.md).

Do not deploy this preview merely because syntax and existing POS frontend tests
pass. The roadmap phase remains in progress until database evidence is recorded.
