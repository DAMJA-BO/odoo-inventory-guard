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

## Company fork rename pending

The available Git credential can rename the personal repository but cannot
administer the company fork. In the DAMJA account, open the existing fork's
Settings → General → Repository name and rename `odoo-pos-stock-guard` to
`odoo-inventory-guard`. Preserve the fork; do not delete or recreate it.

Until that action is completed, deployment intentionally keeps the existing
`DAMJA-BO/odoo-pos-stock-guard` URL. Its code still follows the personal repository.
After the rename, change only the submodule URL in `.gitmodules` to
`git@github.com:DAMJA-BO/odoo-inventory-guard.git` and commit it. The new submodule
directory is already `addons/odoo-inventory-guard`.

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

## Results to record

- Odoo version/commit:
- Odoo.sh build URL and commit:
- English settings/POS:
- Spanish settings/POS:
- Zero stock and excessive quantity:
- Valid sale, return and service:
- Refresh/filter/indicators:
- Browser and server errors:
- Company fork rename completed:
- Accepted by/date:

Local syntax, translation coverage and frontend tests do not replace these Odoo
runtime checks. Phase 1 remains open until this evidence is recorded.
