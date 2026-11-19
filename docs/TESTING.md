# Testing Odoo 20

## Local static checks

```bash
python scripts/check_project.py
node --input-type=module --check < pos_stock_guard/static/src/app/payment_screen_patch.js
```

These checks do not import Odoo or prove runtime compatibility.

## Odoo regression tests

On a disposable database with Odoo 20 and PostgreSQL:

```bash
odoo-bin -d stock_guard_test --addons-path=/path/to/odoo/addons,/path/to/repository \
  -i pos_stock_guard --test-enable --test-tags /pos_stock_guard --stop-after-init
```

Tests cover aggregation, finite input, available quantity, reservations, refunds,
untracked products, missing products and deferred inventory updates. Extend tests
for the deployment's payment methods and installed addons before release.

## Acceptance checklist

- [ ] Install and upgrade the addon; confirm the inherited settings view loads.
- [ ] Disabled toggle preserves normal checkout.
- [ ] Stock 0 blocks a tracked product; stock 1 accepts one unit and blocks two.
- [ ] Duplicate product lines cannot bypass the limit; fractional UoM rounds correctly.
- [ ] Reserved quantities are excluded; refunds and services behave as documented.
- [ ] Updating/deleting lines of a saved draft checks the final persisted demand.
- [ ] Replaying the same finalized UUID does not create another transfer.
- [ ] Deferred stock configuration and ship-later orders are rejected.
- [ ] Invalid lots/serials or failed transfers roll back server finalization.
- [ ] Two independent POS requests competing for the last unit cannot both succeed.
- [ ] Offline manual checkout fails closed; reconnecting permits retry.
- [ ] Test automatic electronic payment; confirm reconciliation/refund procedure on rejection.
- [ ] Test a cashier without inventory-manager access and two allowed companies.
- [ ] Unauthorized users/companies cannot use the advisory RPC.
- [ ] Test installed integrations, bundles, routes and returns using synthetic data.

Release only after recording the Odoo commit/version, database configuration and
results. No Odoo runtime acceptance run has been completed for this preview.
