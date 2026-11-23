# SPDX-License-Identifier: Apache-2.0
"""One explicit, disabled-by-default protection policy per company."""

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class InventoryGuardPolicy(models.Model):
    _name = "inventory.guard.policy"
    _description = "Inventory Guard Policy"
    _check_company_auto = True

    name = fields.Char(required=True, default="Inventory Guard")
    company_id = fields.Many2one("res.company", required=True, default=lambda self: self.env.company)
    enabled = fields.Boolean(string="Enable inventory protection", default=False)
    location_ids = fields.Many2many(
        "stock.location", string="Protected source locations", check_company=True,
        domain="[('usage', '=', 'internal'), ('company_id', 'in', [False, company_id])]",
        help="Leave empty to protect all internal locations. Selected locations include their children.",
    )
    protect_transfers = fields.Boolean(string="Internal transfers", default=True)
    protect_deliveries = fields.Boolean(string="Customer deliveries", default=True)
    protect_vendor_returns = fields.Boolean(string="Vendor returns", default=True)
    protect_scrap = fields.Boolean(string="Scrap", default=True)
    protect_adjustments = fields.Boolean(string="Inventory adjustments", default=True)
    protect_manufacturing = fields.Boolean(string="Manufacturing consumption", default=True)

    _company_unique = models.Constraint("UNIQUE(company_id)", "Only one Inventory Guard policy is allowed per company.")

    @api.constrains("location_ids", "company_id")
    def _check_locations(self):
        for policy in self:
            if any(loc.usage != "internal" or (loc.company_id and loc.company_id != policy.company_id)
                   for loc in policy.location_ids):
                raise ValidationError(_("Protected locations must be internal and belong to the policy company."))

    @api.model
    def _for_source(self, company, location, operation):
        """Resolve persisted policy, independent of RPC context and caller ACLs.

        Shared locations are scoped using the persisted move-line company.
        No public action returns the elevated policy record to an RPC caller.
        """
        if location.usage != "internal":
            return self.browse()
        policy = self.sudo().search([("company_id", "=", company.id), ("enabled", "=", True)], limit=1)
        if not policy or not policy["protect_" + operation]:
            return self.browse()
        if policy.location_ids and not any(location._child_of(root) for root in policy.location_ids):
            return self.browse()
        return policy
