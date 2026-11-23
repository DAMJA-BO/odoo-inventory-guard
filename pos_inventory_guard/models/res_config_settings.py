# SPDX-License-Identifier: Apache-2.0
"""Provide a native shortcut and keep legacy related settings compatible."""

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    def action_open_inventory_guard(self):
        self.ensure_one()
        self.check_access("read")
        return self.pos_config_id.action_open_inventory_guard()

    pos_block_negative_stock = fields.Boolean(
        related="pos_config_id.block_negative_stock",
        readonly=False,
        string="Block sales with insufficient stock",
    )

    pos_inventory_guard_show_badges = fields.Boolean(
        related="pos_config_id.inventory_guard_show_badges", readonly=False,
    )

    pos_inventory_guard_display_mode = fields.Selection(
        related="pos_config_id.inventory_guard_display_mode", readonly=False,
    )

    pos_inventory_guard_block_add = fields.Boolean(
        related="pos_config_id.inventory_guard_block_add", readonly=False,
    )

    pos_inventory_guard_limit_quantity = fields.Boolean(
        related="pos_config_id.inventory_guard_limit_quantity", readonly=False,
    )

    pos_inventory_guard_show_order = fields.Boolean(
        related="pos_config_id.inventory_guard_show_order", readonly=False,
    )

    pos_inventory_guard_available_filter = fields.Boolean(
        related="pos_config_id.inventory_guard_available_filter", readonly=False,
    )

    pos_inventory_guard_low_stock = fields.Boolean(
        related="pos_config_id.inventory_guard_low_stock", readonly=False,
    )

    pos_inventory_guard_low_threshold = fields.Float(
        related="pos_config_id.inventory_guard_low_threshold", readonly=False,
    )

    pos_inventory_guard_auto_refresh = fields.Boolean(
        related="pos_config_id.inventory_guard_auto_refresh", readonly=False,
    )

    pos_inventory_guard_refresh_seconds = fields.Integer(
        related="pos_config_id.inventory_guard_refresh_seconds", readonly=False,
    )

