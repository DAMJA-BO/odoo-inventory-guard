# Odoo Inventory Guard

The suite includes the accepted POS addon and the shared `inventory_guard`
application. The core is disabled until a company policy is configured and
enabled. Clean installation, database regression, concurrent last-unit and
upgrade tests passed against the pinned Odoo 20 revision documented in
`docs/TESTING.md`; complete the deployment-specific manual checklist before release.

Configure company protection in **Inventory Guard → General / Operations** and
per-POS protection and cashier options in **Inventory Guard → Point of Sale**.
The POS addon depends on the core and uses its shared availability service. See
[core configuration and validation](docs/settings/core-policy.md).

See the [migration verification guide](docs/roadmap/PHASE-1-VERIFICATION.md)
before installing the renamed addon on Odoo.sh.

Prevent Odoo 20 Point of Sale checkout when unreserved stock is insufficient.

**Status: development preview. Automated Odoo 20 acceptance passed; manual POS UI and payment-flow acceptance remains.**

Maintained by [Ronald Torrez](https://github.com/ronaldtorrez).
Technical module: `pos_inventory_guard`. Target Odoo series: **20.0** only.

## Behavior

- Optional enforcement per POS configuration; disabled by default.
- Checks physical quantity minus reservations at the POS source location and its children.
- Adds positive quantities across duplicate product lines. Refunds do not offset sales.
- Skips products whose inventory is not tracked, including services.
- Checks manual checkout in the browser, then rechecks persisted lines on the server.
- Serializes participating server checkouts by product and rejects incomplete stock transfers.
- Replayed finalized orders bypass the additional check to avoid double consumption checks.

## Requirements and limits

Requires `inventory_guard`, `pos_stock` and their standard dependencies, Odoo.sh or self-hosted Odoo.
Odoo Online does not support this Python addon. Inventory must update after each
order. Manual checkout requires an online connection. The check is not a stock
reservation and does not guarantee that a payment terminal has not already charged
the customer when a later server check fails. Automatic terminal validation relies
on the server check, not the manual payment-screen patch.

Ship-later orders are rejected when enforcement is enabled. Lot/serial selection
is delegated to Odoo; aggregate availability does not validate an individual lot.
The server rejects a transfer that does not finish successfully. Product bundles,
alternative units of measure, consignment, custom routes and third-party payment
flows need separate acceptance testing. This addon is a POS checkout policy, not
a global prohibition against negative inventory from all stock operations.

## Installation

1. Add this repository to the Odoo addons path (or commit its module to Odoo.sh).
2. Update the Apps list and install **Odoo POS Inventory Guard**.
3. Close active POS sessions.
4. Configure inventory to update after each order.
5. Open **Inventory Guard → Point of Sale**, select the POS,
   and enable **Block sales with insufficient stock**.
6. Open a new session and refresh the POS assets.
7. Complete the [acceptance checklist](docs/TESTING.md) on a test database.

## Optional stock display and early checks

See the [configuration guide](docs/CONFIGURATION.md) and the
[per-setting reference](docs/settings/README.md) for examples, dependencies,
connection behavior, limitations and verification steps.

Every POS has independent settings in the central Inventory Guard app. All new
switches default to off; the existing checkout protection keeps its saved value.
Close the POS session before changing settings, save, then reopen the POS.

| Setting | Behavior |
| --- | --- |
| Show stock badges | Availability on product cards; untracked products have no badge. |
| Stock display mode | Quantity/text with colors, or colors only with accessible labels and tooltips. Applies to cards and order-line indicators. |
| Block adding out-of-stock products | Live server check of the selected variant before creating a line, including scans. |
| Prevent quantities above available stock | Check positive demand across duplicate lines on addition and quantity increases. Reductions and returns remain possible. |
| Show stock on order lines | Availability, shortage highlighting and a shortage count in the cart. |
| Enable Available only filter | Show a cashier-controlled catalog filter. Starts off; unknown and untracked products remain visible. |
| Highlight low stock | Optional warning threshold in product default UoM; default 3, customizable, nonnegative. |
| Automatically refresh stock | Optional product-screen polling; default 30 seconds, customizable, minimum 5. |

The product screen provides manual refresh, source location, last full update
time and an update-failure warning. Polling stops when leaving the product screen;
returning refreshes stock, including after a sale. Newly loaded products refresh too.
Requests use batches of at most 200 variants and do not overlap.

Cards for multiple variants show their combined positive availability, labeled
**Variants**. The selected variant is checked separately before addition. Quantities
are advisory physical stock minus reservations, not promises or reservations.
Editing quantities uses the last snapshot; addition checks and final checkout use
the server. Another cashier can consume stock between those checks.

Early checks and display switches can be selected independently. Enable the
existing final checkout protection for authoritative enforcement. A failed refresh
keeps the previous quantities visibly marked as potentially outdated; early
addition checks fail closed. Use manual refresh before increasing quantities when
the last update failed.

Example self-hosted installation:

```bash
odoo-bin -d inventory_guard_test --addons-path=/path/to/odoo/addons,/path/to/this/repository \
  -i pos_inventory_guard --stop-after-init
```

The old unpublished prototype `pos_no_negative_stock` is not an upgrade target.
Do not install both prototypes together. An installed old prototype requires a
separate migration plan; this repository does not include database migrations.

## Development

Future expansion into the modular **Odoo Inventory Guard** suite is tracked in
the [implementation roadmap](docs/roadmap/README.md). The roadmap defines the
repository migration, addon order, configuration, tests and release criteria.

The interface includes English and general Spanish catalogs. See
[translations](docs/TRANSLATIONS.md) for language activation and maintenance.

See [CONTRIBUTING.md](CONTRIBUTING.md), [architecture](docs/ARCHITECTURE.md)
and [testing](docs/TESTING.md). All code, comments and documentation use English;
user-facing strings remain translatable with Odoo's translation tools.

```bash
python scripts/check_project.py
node --input-type=module --check < pos_inventory_guard/static/src/app/payment_screen_patch.js
npm test
```

## License and attribution

Licensed under [Apache License 2.0](LICENSE). Personal and commercial use,
modification and distribution are permitted under its terms. Preserve applicable
copyright, license and [NOTICE](NOTICE) attribution when distributing the work.
The license does not require a visible promotional banner or payment to the author.

Apache 2.0 grants remain applicable to versions already received even if future
development becomes private. Keep company credentials and private customizations
out of public forks. A private deployment repository can contain a licensed copy.
