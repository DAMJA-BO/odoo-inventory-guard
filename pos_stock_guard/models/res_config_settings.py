# SPDX-License-Identifier: Apache-2.0
"""Expose Stock Guard in the Odoo 20 Point of Sale settings screen."""

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    pos_block_negative_stock = fields.Boolean(
        related="pos_config_id.block_negative_stock",
        readonly=False,
        string="Block sales with insufficient stock",
    )
