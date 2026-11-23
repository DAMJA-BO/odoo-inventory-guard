# SPDX-License-Identifier: Apache-2.0
"""Shared stock policy. No persistent model or additional access grants."""

import math
from collections import defaultdict

from odoo import _, api, models
from odoo.exceptions import ValidationError


class PosInventoryGuard(models.AbstractModel):
    _name = "pos.stock.guard"
    _description = "POS Available Stock Policy"

    @api.model
    def _aggregate_demand(self, lines):
        """Sum positive sales; returns never finance sales in the same order."""
        demand = defaultdict(float)
        for line in lines:
            product_id = line.get("product_id")
            try:
                quantity = float(line.get("qty", 0))
            except (TypeError, ValueError) as error:
                raise ValidationError(_("Invalid checkout quantity.")) from error
            if not math.isfinite(quantity):
                raise ValidationError(_("Checkout quantities must be finite."))
            if not isinstance(product_id, int) or isinstance(product_id, bool):
                raise ValidationError(_("A numeric product ID is required."))
            if quantity > 0:
                demand[product_id] += quantity
                if not math.isfinite(demand[product_id]):
                    raise ValidationError(_("Checkout quantity is too large."))
        return dict(demand)

    @api.model
    def _shortage_message(self, session, demand, lock=False):
        """Return an actionable error, or False when demand can be fulfilled.

        Availability is aggregate free stock in the source location subtree,
        in product UoM. Lot/package allocation is delegated to standard Odoo.
        Product row writes serialize participating checkouts even at zero stock.
        Under PostgreSQL repeatable read, a conflicting write forces Odoo's
        transaction retry instead of checking a stale transaction snapshot.
        """
        session.ensure_one()
        products = self.env["product.product"].browse(sorted(demand)).exists()
        if set(products.ids) != set(demand):
            raise ValidationError(_("One or more checkout products no longer exist."))
        products.check_access("read")
        products = products.filtered("is_storable")
        if not products:
            return False
        if session.update_stock_at_closing:
            return _("Inventory Guard requires inventory updates after each POS order.")
        location = session.config_id.picking_type_id.default_location_src_id
        if not location or location.usage != "internal":
            return _("Configure an internal source location for the POS operation type.")
        if location.company_id and location.company_id != session.company_id:
            return _("The POS source location must belong to the POS company.")
        if lock:
            products.flush_recordset()
            # Sorted writes reduce deadlocks; never commit here. A no-op UPDATE
            # deliberately creates a row version without changing business data.
            for product_id in sorted(products.ids):
                self.env.cr.execute(
                    "UPDATE product_product SET write_date = write_date WHERE id = %s",
                    [product_id],
                )
            self.env["stock.quant"].invalidate_model(["quantity", "reserved_quantity"])
        shortages = []
        for product in products:
            available = self.env["stock.quant"]._get_available_quantity(
                product, location, strict=False, allow_negative=True,
            )
            if product.uom_id.compare(available, demand[product.id]) < 0:
                shortages.append(_(
                    "%(product)s: requested %(requested)s; available %(available)s",
                    product=product.display_name,
                    requested=demand[product.id], available=available,
                ))
        if shortages:
            return _(
                "Insufficient stock at %(location)s:\n%(details)s",
                location=location.display_name, details="\n".join(shortages),
            )
        return False
