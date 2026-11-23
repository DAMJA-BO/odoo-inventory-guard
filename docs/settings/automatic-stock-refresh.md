# Automatically refresh stock

[Settings index](README.md) · [Configuration guide](../CONFIGURATION.md)

## Purpose

Periodically refresh advisory availability while the product screen is open.

## When to enable

Enable this when other cashiers or inventory operations can change stock during an open order.

## Settings

- Location: Inventory Guard → Point of Sale → select a POS.
- Scope: the selected POS configuration.
- Technical field(s): `inventory_guard_auto_refresh`, `inventory_guard_refresh_seconds`.
- Default: Off; interval 30 seconds.

Enable the switch and enter an integer interval of at least 5 seconds. Default is 30 seconds. There is no explicit maximum imposed by this addon.

Close active POS sessions, save the selected configuration and reopen the POS
before checking the result.

## Example

With interval 30, the next automatic refresh is scheduled 30 seconds after the preceding refresh finishes. A slow request therefore makes the time between starts longer than 30 seconds.

## Expected behavior

The toolbar provides manual refresh, source location, last full update time and a failure warning. Polling stops when leaving the product screen and restarts on return.

## Relationships with other settings

Updates badges, line indicators, filters and quantity snapshots. With other stock features enabled, entering the product screen still triggers an initial refresh even if periodic refresh is off. New product loading also refreshes data.

## Connection and stale data

A failed update retains old quantities and marks them potentially outdated. While the screen remains open and automatic refresh is enabled, subsequent scheduled attempts can recover. A targeted addition check does not clear a whole-catalog failure warning.

## Warnings and limitations

This is polling, not an instant stock notification. Full refresh covers loaded products, not every product in the database. It does not reserve stock or replace final validation. A partial failed batch does not publish its staged updates.

All quantities follow the [shared availability rules](../CONFIGURATION.md#availability-rules).
No visual snapshot reserves inventory.

## Performance

Requests are serialized in batches of at most 200 variants. Lower intervals, larger catalogs and more POS terminals increase server load. Start at 30 seconds and adjust from observed behavior.

## Verification example

Verify a custom interval, manual refresh, failed connection/recovery and leaving/reopening the screen. Check that polling does not duplicate and targeted checks do not update the full-refresh timestamp.

These are expected behaviors derived from the implementation, not a record of
completed acceptance tests. See the [test checklist](../TESTING.md).

