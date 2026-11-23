# SPDX-License-Identifier: Apache-2.0
"""Check final physical balances after standard lot compensation.

Reservations stay under Odoo control. Locking product rows deliberately writes a
row version so repeatable-read competitors must retry instead of reusing a stale
snapshot. Never commit or swallow serialization failures in these methods.
"""

from odoo import _, models
from odoo.exceptions import UserError


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    def _inventory_guard_operation(self):
        self.ensure_one()
        if self.move_id.is_inventory:
            return "adjustments"
        if self.move_id.is_scrap:
            return "scrap"
        return {"customer": "deliveries", "supplier": "vendor_returns",
                "production": "manufacturing"}.get(self.location_dest_id.usage, "transfers")

    def _inventory_guard_lock_products(self):
        """Serialize even empty source dimensions; row locks alone miss them."""
        self.env["product.product"].flush_model()
        for product_id in sorted(self.product_id.ids):
            self.env.cr.execute(
                "UPDATE product_product SET write_date = write_date WHERE id = %s", [product_id],
            )
        self.env["stock.quant"].invalidate_model(["quantity", "reserved_quantity"])

    def _inventory_guard_has_policy(self):
        return any(self.env["inventory.guard.policy"]._for_source(
            line.location_id.company_id or line.company_id, line.location_id,
            line._inventory_guard_operation(),
        ) for line in self)

    def _action_done(self):
        if not self._inventory_guard_has_policy():
            return super()._action_done()
        # Roll back the entire batch if a later line fails and an outer caller
        # catches UserError (for example a POS integration).
        with self.env.cr.savepoint():
            self._inventory_guard_lock_products()
            return super()._action_done()

    def write(self, vals):
        if not self.filtered(lambda line: line.state == "done"):
            return super().write(vals)
        with self.env.cr.savepoint():
            return super().write(vals)

    def _synchronize_quant(self, quantity, location, action="available", in_date=False, **quants_value):
        self.ensure_one()
        policy = self.env["inventory.guard.policy"]._for_source(
            location.company_id or self.company_id, location, self._inventory_guard_operation(),
        )
        if action != "available" or quantity >= 0 or not self.product_id.is_storable or not policy:
            return super()._synchronize_quant(quantity, location, action=action, in_date=in_date, **quants_value)
        with self.env.cr.savepoint():
            self._inventory_guard_lock_products()
            result = super()._synchronize_quant(quantity, location, action=action, in_date=in_date, **quants_value)
            lot = quants_value.get("lot", self.lot_id)
            package = quants_value.get("package", self.package_id)
            owner = quants_value.get("owner", self.owner_id)
            quants = self.env["stock.quant"].sudo().with_context(quants_cache=None)._gather(
                self.product_id, location, lot_id=lot, package_id=package, owner_id=owner, strict=True,
            )
            # _gather can include untracked quants during lot compensation.
            exact = quants.filtered(lambda q: q.lot_id.id == (lot.id if lot else False)
                                    and q.package_id.id == (package.id if package else False)
                                    and q.owner_id.id == (owner.id if owner else False))
            physical = sum(exact.mapped("quantity"))
            if self.product_id.uom_id.compare(physical, 0) < 0:
                raise UserError(_(
                    "Inventory Guard blocked %(operation)s: %(product)s at %(location)s. "
                    "Requested: %(requested)s; remaining physical stock: %(remaining)s. "
                    "Check the lot, package and owner or reduce the quantity.",
                    operation=self.move_id.display_name, product=self.product_id.display_name,
                    location=location.display_name, requested=-quantity, remaining=physical,
                ))
            return result
