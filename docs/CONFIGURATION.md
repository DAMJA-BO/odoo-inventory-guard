# Stock Guard configuration for Odoo 20

[Project README](../README.md) · [Setting reference](settings/README.md)

## Configure one POS

1. Install the addon and close active sessions for the POS being configured.
2. Open Point of Sale → Configuration → Settings.
3. Select the intended POS and find the Stock Guard section.
4. Choose its settings using the [setting reference](settings/README.md).
5. Save, reopen the POS and refresh the browser assets if necessary.
6. Verify the behavior on a disposable test database.

Settings belong to each POS configuration. Configuring Bestone's POS does not
automatically configure another POS or company. The settings view makes the fields
read-only while a session is active.

For final checkout protection, inventory must update after each order. Verify
the operation type has an internal source location in the POS company, or a
permitted shared location. The addon checks access to the POS and its company.

## Availability rules

Stock means physical stock minus reservations at the POS operation type's source
location and its children. It is not a total across all companies or warehouses.
Quantities use each product's default unit of measure. The final comparison uses
Odoo's Product Unit precision.

Example: 10 physical units minus 4 reserved units means 6 available. A sale of 7
is insufficient even though physical stock is 10. Positive sale quantities for
the same variant are added across duplicate lines. Returns do not cancel demand
for new sales in the same validation.

Only inventory-tracked products are constrained. A service or other untracked
product has no stock badge once its tracking status is known. Requests can still
fail before tracking status is resolved when a server connection is unavailable.

## Snapshots and validation

Product badges, line indicators, the filter and quantity editing use advisory
snapshots. Quantities do not subtract the current cart: line demand is compared
separately against availability. A snapshot does not reserve stock.

Adding a product with an early check enabled fetches availability from the
server. Quantity increases use the latest snapshot. Final protection, when
enabled, checks persisted order lines on the server again. Another cashier can
sell between these steps, so an earlier success is not a reservation.

## Manual refresh and status

When a feature that needs snapshots is enabled, the product screen offers stock
refresh and status information. This includes badges, line indicators, early
checks, the filter or automatic refresh. Display mode or low-stock highlighting
alone does not enable snapshot loading.

Entering the product screen refreshes stock. Automatic refresh adds periodic
requests while that screen is open. A failed update retains older data and marks
it potentially outdated. A successful full refresh clears that warning. Targeted
addition checks do not claim that the entire loaded catalog is fresh.

## Common configuration questions

- **No low-stock warning:** enable badges or order-line indicators too, check the
  threshold, refresh stock and ensure availability is positive and within it.
- **Product visible with Available only:** unknown/untracked products stay visible;
  a template may also have another available variant.
- **One POS differs from another:** select and inspect each POS independently.
- **A quantity increase is refused after a connection failure:** restore the
  connection and perform a full refresh before retrying.
- **Display works but checkout still accepts insufficient stock:** verify final
  checkout protection is enabled on the actual POS, saved and loaded in a new session.
- **An early check passes but checkout fails:** availability may have changed;
  inspect the final shortage message and current source-location stock.

## Further reading

- [Every configurable setting and its examples](settings/README.md)
- [Technical architecture](ARCHITECTURE.md)
- [Testing and acceptance checklist](TESTING.md)

This documentation describes the current implementation. Passing a build does
not prove every cashier interaction or installed integration has been tested.

