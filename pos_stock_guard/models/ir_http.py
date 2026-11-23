# SPDX-License-Identifier: Apache-2.0
"""Expose the addon's JavaScript translations to the POS frontend."""

from odoo import models


class IrHttp(models.AbstractModel):
    _inherit = "ir.http"

    @classmethod
    def _get_translation_frontend_modules_name(cls):
        """Include Stock Guard alongside the standard frontend modules."""
        return super()._get_translation_frontend_modules_name() + ["pos_stock_guard"]
