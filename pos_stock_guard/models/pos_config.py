# SPDX-License-Identifier: Apache-2.0
"""POS configuration and authenticated, advisory checkout endpoint."""

import math

from odoo import _, api, fields, models
from odoo.exceptions import AccessError, ValidationError


class PosConfig(models.Model):
    _inherit = "pos.config"

    block_negative_stock = fields.Boolean(
        string="Block sales with insufficient stock",
        help="Check unreserved stock at the POS source location before checkout.",
        default=False,
    )

    stock_guard_show_badges = fields.Boolean(string="Show stock badges")
    stock_guard_display_mode = fields.Selection(
        [("quantity", "Quantity, text and colors"), ("color", "Colors only")],
        default="quantity", required=True, string="Stock display mode",
    )
    stock_guard_block_add = fields.Boolean(string="Block adding out-of-stock products")
    stock_guard_limit_quantity = fields.Boolean(string="Prevent quantities above available stock")
    stock_guard_show_order = fields.Boolean(string="Show stock on order lines")
    stock_guard_available_filter = fields.Boolean(string="Enable Available only filter")
    stock_guard_low_stock = fields.Boolean(string="Highlight low stock")
    stock_guard_low_threshold = fields.Float(string="Low stock threshold", default=3)
    stock_guard_auto_refresh = fields.Boolean(string="Automatically refresh stock")
    stock_guard_refresh_seconds = fields.Integer(string="Refresh interval (seconds)", default=30)

    @api.constrains("stock_guard_low_threshold", "stock_guard_refresh_seconds")
    def _check_stock_guard_options(self):
        """Reject invalid settings even when written outside the settings view."""
        for config in self:
            if not math.isfinite(config.stock_guard_low_threshold) or config.stock_guard_low_threshold < 0:
                raise ValidationError(_("The low stock threshold must be finite and nonnegative."))
            if config.stock_guard_refresh_seconds < 5:
                raise ValidationError(_("The stock refresh interval must be at least 5 seconds."))

    @api.model
    def get_stock_guard_availability(self, config_id, product_ids):
        """Return advisory free quantities in product UoM for one POS location.

        Bounded batches avoid loading an entire warehouse or exposing quants.
        No sudo: the caller must have POS access and access to the POS company.
        This snapshot does not reserve inventory or replace checkout validation.
        """
        if not self.env.user.has_group("point_of_sale.group_pos_user"):
            raise AccessError(_("Only Point of Sale users can check checkout stock."))
        config = self.browse(config_id).exists()
        config.ensure_one()
        config.check_access("read")
        if config.company_id not in self.env.companies:
            raise AccessError(_("The POS belongs to an unauthorized company."))
        if (
            not isinstance(product_ids, list) or len(product_ids) > 200
            or any(type(pid) is not int or pid <= 0 for pid in product_ids)
        ):
            raise ValidationError(_("Supply at most 200 numeric product IDs."))
        location = config.picking_type_id.default_location_src_id
        if not location or location.usage != "internal":
            raise ValidationError(_("Configure an internal source location for the POS operation type."))
        if location.company_id and location.company_id != config.company_id:
            raise AccessError(_("The POS source location must belong to the POS company."))
        products = self.env["product.product"].with_company(config.company_id).browse(product_ids).exists()
        products.check_access("read")
        if any(product.company_id and product.company_id != config.company_id for product in products):
            raise AccessError(_("Products must belong to the POS company or be shared."))
        result = {}
        for product in products:
            # Use exactly the same availability calculation as final validation.
            quantity = self.env["stock.quant"].with_company(config.company_id)._get_available_quantity(
                product, location, strict=False, allow_negative=True,
            ) if product.is_storable else 0
            result[product.id] = {
                "tracked": product.is_storable,
                "available": quantity,
                "rounding": product.uom_id.rounding,
            }
        return {"products": result, "location": location.display_name}

    @api.model
    def check_pos_stock(self, config_id, lines):
        """Check draft quantities without reserving stock or acquiring locks.

        ``lines`` contains product_id and qty in each product's default UoM.
        This response is advisory: persisted order lines are checked separately.
        """
        if not self.env.user.has_group("point_of_sale.group_pos_user"):
            raise AccessError(_("Only Point of Sale users can check checkout stock."))
        config = self.browse(config_id).exists()
        if not config:
            return {"ok": False, "message": _("POS configuration not found.")}
        config.check_access("read")
        if config.company_id not in self.env.companies:
            raise AccessError(_("The POS belongs to an unauthorized company."))
        if not config.block_negative_stock:
            return {"ok": True, "message": ""}
        session = config.current_session_id
        if not session or session.state != "opened":
            return {"ok": False, "message": _("An open POS session is required.")}
        guard = self.env["pos.stock.guard"].with_company(config.company_id)
        demand = guard._aggregate_demand(lines)
        error = guard._shortage_message(session, demand)
        return {"ok": not bool(error), "message": error or ""}
