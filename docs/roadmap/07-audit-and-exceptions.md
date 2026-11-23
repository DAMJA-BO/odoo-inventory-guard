# Phase 7 — `inventory_guard_audit`

Register **Audit** under Inventory Guard when this addon is installed. See the
[central configuration contract](../architecture/centralized-configuration.md).

## Goal

Allow controlled exceptions without creating a silent bypass and provide useful
history for operations that were actually authorized and completed.

## Permissions

- Ordinary users cannot override protection.
- Managers configure policies but do not automatically bypass them.
- An explicit Override group may authorize an exception when policy permits it.
- Every override requires a reason and identifies user, company and operation.
- Client-provided context alone never authorizes bypass; the server verifies group
  membership and the applicable policy.

## Audit records

Store successful warnings/overrides with policy, operation/model, company, source
location, product dimensions, requested/available quantities, reason, user and
timestamp. Apply retention and access rules per company.

A blocked transaction rolls back its database writes. Do not open an independent
database transaction inside business logic merely to retain a blocked-attempt row.
Initially, blocked attempts may use structured server logs; durable rejected-attempt
analytics requires a separately designed, failure-safe event mechanism.

## Interface and reporting

- Override dialog with policy explanation and mandatory reason.
- Read-only audit list/pivot restricted by company and group.
- Links back to completed picking, POS order or manufacturing order where available.
- Filters for operation, product, location, user, policy and date.

## Tests

Verify ordinary users, managers and override users; required reasons; company
record rules; forged RPC/context values; rollback behavior; successful override
records; retention; translations and removal of user access during an open flow.

## Exit criteria

No bypass is silent, successful exceptions are traceable and audit access cannot
expose another company's inventory or users.

