# Odoo Inventory Guard roadmap

This roadmap turns the current POS addon into a modular Odoo 20 inventory
protection suite. It is the source of truth for scope, order and completion.
Update the relevant file whenever implementation decisions or behavior change.

## Target identity

- Product: **Odoo Inventory Guard**.
- Canonical repository: `ronaldtorrez/odoo-inventory-guard`.
- Company fork: `DAMJA-BO/odoo-inventory-guard`.
- Deployment repository: `DAMJA-BO/odoo-sh-bestone`.
- Supported series: Odoo 20 only.
- Source language: English; shipped interface languages: English and Spanish.
- License: Apache License 2.0.

The repository and addon names above are active. Phase 1 preserved the previous
POS-only release as a rollback point before applying the new identity.

## Addon architecture

| Addon | Purpose | Depends on | Planned order |
| --- | --- | --- | --- |
| `inventory_guard` | Main app, policy engine, configuration and final stock-operation protection | `stock` | 1 |
| `pos_inventory_guard` | POS visibility, early checks and checkout integration | `inventory_guard`, `pos_stock` | 2 |
| `sale_inventory_guard` | Sales availability warnings and delivery guidance | `inventory_guard`, `sale_stock` | 4 |
| `purchase_inventory_guard` | Vendor-return guidance and purchasing-specific messages | `inventory_guard`, `purchase_stock` | 5 |
| `mrp_inventory_guard` | Component-consumption and manufacturing guidance | `inventory_guard`, `mrp` | 6 |
| `inventory_guard_audit` | Optional exception and override history/reporting | `inventory_guard` | 7 |

Transfers, scrap, negative inventory adjustments and stock-originating vendor
returns belong to the main `inventory_guard` app. Extensions add earlier and
more useful feedback; they must not duplicate the authoritative stock rule.

## Delivery sequence

| Phase | Document | Status | Exit condition |
| --- | --- | --- | --- |
| 0 | Current POS release | Complete | Version `20.0.2.0.1` promoted to `main` |
| 1 | [Repository and module migration](01-migration-and-renaming.md) | Complete | New identity builds on a clean Odoo.sh development database |
| 2 | [Core app and policy engine](02-inventory-guard-core.md) | Implemented, acceptance pending | Generic stock operations cannot create protected negative stock |
| 3 | [POS migration](03-pos-inventory-guard.md) | In progress | Central POS settings and shared server checks pass Odoo.sh acceptance |
| 4 | [Stock operations](04-stock-operations.md) | Planned | Transfers, scrap, adjustments and returns pass acceptance tests |
| 5 | [Sales and purchases](05-sales-and-purchases.md) | Planned | Business users receive application-specific guidance |
| 6 | [Manufacturing](06-manufacturing.md) | Planned | Consumption and partial manufacturing scenarios are protected |
| 7 | [Audit and exceptions](07-audit-and-exceptions.md) | Planned | Authorized exceptions are explicit and traceable |
| 8 | [Quality and release](08-quality-and-release.md) | Planned | Full suite is release-ready and documented |

Only one phase should be marked In progress at a time unless dependencies make
parallel work safe. A phase is Complete only after its automated and Odoo.sh
acceptance checks are recorded.

## Product rules shared by all addons

1. The final protection runs on the server and cannot trust a browser context
   flag to bypass policy.
2. Policies are company-aware and location-aware. Quantities from unrelated
   companies or warehouses never satisfy demand.
3. Advisory displays never claim to reserve inventory.
4. The final operation accounts for the operation's own reservation; it must
   not compare reserved moves naively against free stock.
5. Internal source locations are protected by default. Virtual locations are
   excluded. Transit locations require an explicit policy decision.
6. Services and other untracked products are outside stock enforcement.
7. Lots, serial numbers, packages and owners are respected where Odoo tracks
   availability at those dimensions.
8. Concurrent operations over the last units cannot both succeed.
9. Every user-facing message remains translatable and every behavior change
   updates `docs/`, tests and the changelog.
10. A module extension may improve warnings but cannot weaken core validation.

## Configuration destination

`inventory_guard` will be an installable Odoo application with configuration at
**Inventory Guard → Overview / General / Operations**. Installed extensions add
their own sections to this app while storing values on the appropriate business
records. Native settings may link to the central screen. See the
[central configuration contract](../architecture/centralized-configuration.md).

## Branch and release workflow

- `main` contains accepted releases only.
- `development` integrates the next tested version.
- Use a short feature branch for each roadmap phase when work spans multiple
  commits; merge it into `development` after review.
- Odoo.sh development follows the deployment repository's `development` branch.
- Promote the tested submodule commit to staging/production only after the phase
  checklist passes. Documentation-only commits do not require an Odoo.sh build.
- Version every addon independently with the `20.0.x.y.z` convention.

## Decisions required before core implementation

Record final answers in the phase document before writing the policy engine:

- Whether transit locations are protected by default.
- Whether the first core release supports Block only or Block and Warn modes.
- Whether managers can override immediately or only after the audit addon exists.
- Whether policy scope starts company-wide or supports product/category rules in
  the first release.
- Whether inventory adjustments may correct already-negative historical stock.

## Definition of done for every phase

- Code, comments and technical documentation are in English.
- English and Spanish interface catalogs cover every visible source term.
- Static checks and relevant unit/boundary tests pass.
- Odoo 20 installation and upgrade tests pass on a disposable database.
- Multi-company access, concurrency and permission behavior are tested where relevant.
- Manual acceptance evidence is recorded; expected behavior is not presented as
  a completed result before the test occurs.
- `README.md`, `CHANGELOG.md`, architecture, settings and testing documentation
  reflect the final behavior.

