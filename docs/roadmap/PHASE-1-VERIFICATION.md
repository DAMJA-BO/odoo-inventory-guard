# Phase 1 verification and rollout

## Rollback point

The accepted POS-only release is commit
`e930d92cd4185df04618c467c160a64fe3450059`, tagged
`pos-stock-guard-20.0.2.0.1`. Main remains at that release.

## Delivered changes

- Canonical repository: `ronaldtorrez/odoo-inventory-guard`.
- Addon: `pos_inventory_guard`; display name: Odoo POS Inventory Guard.
- Suite name: Odoo Inventory Guard.
- Assets, Python service names, fields, template names, scripts, CI, tests and
  English/Spanish catalogs use the new identity.
- Behavior and version remain the accepted POS behavior and `20.0.2.0.1`.
- The core inventory app is deferred to Phase 2.

## Company fork rename completed

The existing DAMJA fork was preserved and renamed to
`DAMJA-BO/odoo-inventory-guard`. The deployment submodule now uses
`git@github.com:DAMJA-BO/odoo-inventory-guard.git` at
`addons/odoo-inventory-guard`.

## Odoo.sh verification

1. Select the deployment branch `inventory-guard-migration` in Odoo.sh. Keep it
   under Development so Odoo.sh creates a disposable database. Do not move it to
   staging or production and do not restore the previous test database into it.
2. In the branch Settings, disable inherited build options if needed and set the
   specific module installation list to `pos_inventory_guard`. Keep module tests
   enabled. If the automatic first build used the old name, rebuild after saving.
3. Wait for the build tests. If they fail, preserve the first traceback before
   retrying. A queued build has not yet executed the module tests.
4. Connect, open Apps and confirm `pos_inventory_guard` is installed. The old
   `pos_stock_guard` must not be installed. Never install both together.
5. Open POS settings and verify the Inventory Guard section. Check two different
   POS configurations retain independent values.
6. Enable final protection, inventory updates after each order, badges, early
   addition blocking, quantity limits and order indicators. Save and open a new POS.
7. Use a tracked test product at the POS source with 0 available: adding it must
   be rejected when early blocking is enabled. With early blocking disabled,
   final checkout must still reject it. No completed order/transfer should result.
8. Set a different test product to 2 available. Selling 2 must succeed, while a
   request for 3 must be rejected. Include duplicate lines and a barcode scan.
9. Test returns, services, variants, manual refresh, optional filter, threshold,
   automatic refresh and both display modes using the existing settings guides.
10. Install Spanish, change user language, reload and reopen POS. Check settings,
    badges, toolbar and shortage messages. Repeat in English. Inventory Guard is
    the product name in both languages.
11. Inspect browser console and server logs for missing assets, old module/model
    references, translation errors or exceptions.
12. Record results and build URL below. Only then promote the tested deployment
    commit to the deployment repository's `development` branch.

## Acceptance results

- Odoo version: 20.0.
- Deployment repository: `DAMJA-BO/odoo-sh-bestone`.
- Tested deployment branch: `inventory-guard-migration`.
- Accepted deployment commit: `b096141554de550ec3414014de7e04db41262294`.
- Odoo.sh result: build and module test suite succeeded on a fresh development
  database.
- Installed addon: `pos_inventory_guard`; the former `pos_stock_guard` addon was
  confirmed absent.
- English settings/POS: settings and a POS session opened without errors.
- Spanish settings/POS: interface and translated Inventory Guard content were
  accepted.
- Stock behavior: the existing zero-stock checkout protection remained
  operational after the rename.
- Browser and server errors: none reported during acceptance.
- Company fork rename: completed without recreating the fork.
- Accepted by/date: project owner, 2026-11-23.

Phase 1 is complete. The accepted migration may remain on `development`; `main`
stays at the documented rollback release until a later release is approved.
