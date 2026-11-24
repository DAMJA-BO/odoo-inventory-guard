# SPDX-License-Identifier: Apache-2.0
"""Authoritative validation using persisted Odoo 20 order lines."""

from odoo import _, api, models
from odoo.exceptions import UserError


class PosOrder(models.Model):
    _inherit = "pos.order"

    @api.model
    def _process_order(self, order, existing_order):
        """Remember replay state before Odoo creates/updates the order record."""
        should_validate = (
            order.get("state") != "draft"
            and not (existing_order and existing_order.state in ("paid", "done", "cancel"))
        )
        scoped = self.with_context(inventory_guard_validate=should_validate)
        if existing_order:
            existing_order = existing_order.with_context(
                inventory_guard_validate=should_validate,
            )
        return super(PosOrder, scoped)._process_order(order, existing_order)

    def _process_saved_order(self, draft):
        """Check before payment finalization and immediate stock consumption.

        Let Odoo interpret create/update/unlink commands first. Finalized order
        replays are ignored so an already consumed quantity is not checked twice.
        Locks remain held until the enclosing Odoo transaction ends.
        """
        self.ensure_one()
        guarded = (
            self.config_id.block_negative_stock
            and not draft
            and self.env.context.get("inventory_guard_validate", False)
            and self.state != "cancel"
        )
        demand = {}
        if guarded:
            guard = self.env["pos.stock.guard"].with_company(self.company_id)
            demand = guard._aggregate_demand([
                {"product_id": line.product_id.id, "qty": line.qty}
                for line in self.lines
            ])
            if self.shipping_date and demand:
                raise UserError(_("Inventory Guard does not support ship-later orders."))
            error = guard._shortage_message(self.session_id, demand, lock=True)
            if error:
                raise UserError(error)
        result = super()._process_saved_order(draft)
        if demand:
            stock_lines = self.lines.filtered(
                lambda line: line.qty > 0 and line.product_id.is_storable
            )
            if stock_lines and (
                not self.picking_ids or any(p.state != "done" for p in self.picking_ids)
            ):
                # Standard Odoo can keep a failed picking without raising. Roll
                # back checkout so subsequent sales cannot reuse that quantity.
                raise UserError(_(
                    "Inventory Guard could not complete the stock transfer. "
                    "Check lots, serial numbers and stock configuration, then retry."
                ))
        return result
