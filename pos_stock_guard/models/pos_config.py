# SPDX-License-Identifier: Apache-2.0
"""POS configuration and authenticated, advisory checkout endpoint."""

from odoo import _, api, fields, models
from odoo.exceptions import AccessError


class PosConfig(models.Model):
    _inherit = "pos.config"

    block_negative_stock = fields.Boolean(
        string="Block sales with insufficient stock",
        help="Check unreserved stock at the POS source location before checkout.",
        default=False,
    )

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
