# Phase 1 — repository and module migration

**Status: Complete — accepted on Odoo.sh on 2026-11-23.**

## Goal

Rename the project before production use, preserve Git history and produce a clean
Odoo 20 development installation under the new technical names.

## Preconditions

- Current tested POS version is on `main` in the canonical and company repositories.
- No production database has installed `pos_stock_guard`.
- Odoo.sh development data can be discarded or the old addon can be uninstalled.
- A tag or immutable commit SHA records the last POS-only version.

## Renames

| Current | Target |
| --- | --- |
| Repository `odoo-pos-stock-guard` | `odoo-inventory-guard` |
| Product “Odoo POS Stock Guard” | “Odoo Inventory Guard” |
| Addon `pos_stock_guard` | `pos_inventory_guard` |
| Display section “Stock Guard” | “Inventory Guard” with a POS subsection |
| Deployment path `addons/odoo-pos-stock-guard` | `addons/odoo-inventory-guard` |

## Execution steps

1. Tag the current `main` commit as the last POS-only rollback point.
2. Create a migration feature branch from `development`.
3. Rename the canonical GitHub repository, then the company fork.
4. Update local remotes, repository URLs, badges, website metadata, issue links,
   clone instructions and license/NOTICE references that contain old URLs.
5. Update `.gitmodules` and the deployment repository path/URL. Preserve the
   submodule commit until the renamed repository is reachable.
6. Move `pos_stock_guard/` to `pos_inventory_guard/` with Git history preserved.
7. Update Python imports, model descriptions, XML IDs, template names, SCSS
   classes, asset paths, tests, scripts, translation domains and documentation.
8. Rename visible product terminology while retaining clear POS-specific labels.
9. Regenerate POT, English and Spanish catalogs from the renamed addon.
10. Search the entire repository for `pos_stock_guard`, `POS Stock Guard` and old
    repository URLs; every remaining occurrence must be intentional and documented.
11. Use a fresh Odoo.sh development database, or uninstall the old addon before
    deploying the renamed one. Never leave both technical modules installed.
12. Install `pos_inventory_guard`, run tests and verify settings and checkout in
    both English and Spanish.
13. Merge the migration branch into `development`; keep `main` at the rollback
    version until the renamed build passes acceptance.

## Database policy

Because there is no production installation, the first migration uses a clean
installation and does not ship an OpenUpgrade-style database migration. If a
database with valuable configuration is discovered, stop and add an explicit
pre-migration script that maps module metadata, XML IDs and fields. Do not solve
that case by installing both modules.

## Tests

- Repository-wide old-name scan.
- Clean install and upgrade of the renamed addon.
- Manifest assets load without missing paths.
- Translation catalogs cover the renamed source terms.
- Existing 15 frontend boundary tests and backend tests pass under new imports.
- Odoo.sh opens POS settings and a POS session without asset errors.

## Exit criteria

The new repositories, submodule and addon names are operational on Odoo.sh,
the old addon is absent from the test database and the rollback tag is documented.

