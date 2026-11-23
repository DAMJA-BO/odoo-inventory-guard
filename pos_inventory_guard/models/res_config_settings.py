# SPDX-License-Identifier: Apache-2.0
"""Expose Inventory Guard in the Odoo 20 Point of Sale settings screen."""

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

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

