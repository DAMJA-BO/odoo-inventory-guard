# SPDX-License-Identifier: Apache-2.0
"""Availability and transaction serialization shared by stock integrations."""

from odoo import _, api, models
from odoo.exceptions import ValidationError


class InventoryGuardAvailability(models.AbstractModel):
    _name = "inventory.guard.availability"
    _description = "Inventory Guard Availability"

    @api.model
    def _demand_products(self, demand):
        products = self.env["product.product"].browse(sorted(demand)).exists()
        if set(products.ids) != set(demand):
            raise ValidationError(_("One or more checkout products no longer exist."))
        products.check_access("read")
        return products.filtered("is_storable")

    @api.model
    def _lock_products(self, products):
        """Create product row versions so stale concurrent operations retry."""
        products.flush_recordset()
        # Sorted writes reduce deadlocks; never commit here. A no-op UPDATE
        # deliberately creates a row version without changing business data.
        for product_id in sorted(products.ids):
            self.env.cr.execute(
                "UPDATE product_product SET write_date = write_date WHERE id = %s",
                [product_id],
            )
        self.env["stock.quant"].invalidate_model(["quantity", "reserved_quantity"])

    @api.model
    def _free_quantity(self, product, location):
        """Return unreserved stock in the source subtree in the product UoM."""
        return self.env["stock.quant"]._get_available_quantity(
            product, location, strict=False, allow_negative=True,
        )

    @api.model
    def _shortage_message(self, products, location, demand, *, lock=False):
        """Compare aggregated demand and optionally serialize checkout."""
        if lock:
            self._lock_products(products)
        shortages = []
        for product in products:
            available = self._free_quantity(product, location)
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
