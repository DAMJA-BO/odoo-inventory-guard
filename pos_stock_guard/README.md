# Odoo POS Stock Guard

Odoo 20 addon to reject POS checkout when available stock is insufficient.

Enable **Block sales with insufficient stock** on the POS configuration after
closing active sessions. Requires inventory updates after each order and an
online connection. Ship-later orders are unsupported. Test on a disposable
database before deployment; this is a development preview.

See the project README, architecture and test checklist in the parent repository.
Personal and commercial use are permitted under Apache License 2.0. Distribute
the accompanying LICENSE and NOTICE files with this addon.

Maintainer: Ronald Torrez — https://github.com/ronaldtorrez
