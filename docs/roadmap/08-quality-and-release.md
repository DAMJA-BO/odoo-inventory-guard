# Phase 8 — quality and release

Verify each extension contributes its settings to the central Inventory Guard app. See the
[central configuration contract](../architecture/centralized-configuration.md).

## Automated validation

Each addon must pass Python/XML/manifest checks, translation coverage, frontend
tests where applicable and Odoo 20 tagged tests. Add an installation matrix for:

- Core alone.
- Core plus each extension independently.
- Full suite.
- Upgrade from the preceding development version.
- Multi-company users with restricted allowed companies.

Concurrency tests must use independent database requests/transactions. Sequential
test cursors do not prove last-unit protection.

## Odoo.sh pipeline

1. Point the development submodule to the reviewed extension commit.
2. Wait for install/upgrade and test completion.
3. Inspect server logs, browser console and asset loading.
4. Run the phase's English and Spanish manual checklist.
5. Record Odoo commit/version, database configuration and results.
6. Promote the exact submodule SHA to staging.
7. Restore a recent production-like backup in staging and repeat critical flows.
8. Promote to production only after user approval and rollback preparation.

## Release documentation

Maintain the root README, addon READMEs, changelog, architecture, translations,
per-setting pages, security model, migration notes and testing evidence. Every
addon README states dependencies, supported flows, exclusions and configuration.

## Release checklist

- Version numbers and manifests are consistent.
- English/Spanish catalogs match current source and interpolate safely.
- No customer data, credentials or Enterprise source is committed.
- Install/upgrade/uninstall behavior is documented and tested appropriately.
- Main contains only accepted work; development remains the next integration line.
- Canonical repository, company fork and deployment submodule point to intended SHAs.
- A rollback commit/tag and database backup procedure are recorded.

## Suite acceptance scenarios

Run a connected scenario from sales order to delivery, purchase receipt and vendor
return, internal transfer, scrap, inventory adjustment, POS sale/refund and MRP
consumption/unbuild. Include reservations, partials, lots/serials, two companies
and two simultaneous users competing for the last quantity.

## Exit criteria

The documented installation matrix passes, manual evidence is recorded, security
and concurrency reviews are complete and the exact release commits are reproducible.

