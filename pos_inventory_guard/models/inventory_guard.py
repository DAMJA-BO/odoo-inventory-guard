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
        if not isinstance(lines, list) or len(lines) > 1000:
            raise ValidationError(_("Invalid checkout quantity."))
        demand = defaultdict(float)
        for line in lines:
            if not isinstance(line, dict):
                raise ValidationError(_("Invalid checkout quantity."))
            product_id = line.get("product_id")
            if isinstance(line.get("qty"), bool):
                raise ValidationError(_("Invalid checkout quantity."))
            try:
                quantity = float(line.get("qty", 0))
            except (TypeError, ValueError, OverflowError) as error:
                raise ValidationError(_("Invalid checkout quantity.")) from error
            if not math.isfinite(quantity):
                raise ValidationError(_("Checkout quantities must be finite."))
            if type(product_id) is not int or product_id <= 0:
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
        availability = self.env["inventory.guard.availability"].with_company(session.company_id)
        products = availability._demand_products(demand)
        if not products:
            return False
        if session.update_stock_at_closing:
            return _("Inventory Guard requires inventory updates after each POS order.")
        location = session.config_id.picking_type_id.default_location_src_id
        if not location or location.usage != "internal":
            return _("Configure an internal source location for the POS operation type.")
        if location.company_id and location.company_id != session.company_id:
            return _("The POS source location must belong to the POS company.")
        return availability._shortage_message(products, location, demand, lock=lock)
