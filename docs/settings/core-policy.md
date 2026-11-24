# Core inventory protection

Status: local development preview, awaiting Odoo 20 database acceptance.

## Installation and access

Install `inventory_guard` on a disposable Odoo 20 database. The POS addon
uses the core as a dependency. Open **Inventory Guard → General** for activation
and locations, or **Operations** for operation switches. **Overview** lists
policies for companies you can access. Inventory's native menu links to General.
Inventory users may read policies; Inventory managers may manage them, subject
to allowed-company record rules. No separate override permission exists.

## Company and activation

Select the intended company in Odoo. The first manager visit to General or
Operations creates that company's policy automatically if needed. The **Enable inventory protection** switch starts off. The source
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

The POS checkout switch remains per POS and uses the core's free-stock check.
The company policy checks actual physical move balances for covered operations,
including any POS transfer classified as a protected delivery. Its rules can
still apply with the POS checkout switch off. Neither setting controls badges.

## Verification required before release

Run with both modules selected: `inventory_guard,pos_inventory_guard`. Keep tests
enabled and verify both English and Spanish after installation/upgrade.

New transaction tests cover disabled behavior, zero/exact stock, duplicate-line
batch rollback, reservations, operation switches, positive correction and transit.
They require a running Odoo server and PostgreSQL and have not been run locally.
Before acceptance, add/run separate-cursor concurrent last-unit tests, lots,
packages, owners, multi-company permissions, done-line edits, partials and backorders,
and exercise native picking, scrap, return and inventory-adjustment entry points.
Compare the server hooks with the deployed Odoo 20 revision. See the
[hook investigation](../architecture/core-hook-spike.md).

Do not deploy this preview merely because syntax and existing POS frontend tests
pass. The roadmap phase remains in progress until database evidence is recorded.
