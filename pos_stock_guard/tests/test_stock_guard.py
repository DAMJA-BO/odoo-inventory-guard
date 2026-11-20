# SPDX-License-Identifier: Apache-2.0
"""Stock-policy regression tests requiring a disposable Odoo 20 database."""

from odoo.exceptions import ValidationError
from odoo.tests import tagged
from odoo.addons.account.tests.common import AccountTestInvoicingCommon


@tagged("post_install", "-at_install")
class TestStockGuard(AccountTestInvoicingCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # AccountTestInvoicingCommon does not grant Point of Sale manager
        # access. Use elevated privileges only for technical test fixtures so
        # these policy tests do not depend on the runner user's access groups.
        cls.guard = cls.env["pos.stock.guard"].sudo()
        cls.warehouse = cls.env["stock.warehouse"].sudo().search([
            ("company_id", "=", cls.env.company.id),
        ], limit=1)
        cls.config = cls.env["pos.config"].sudo().create({
            "name": "Stock Guard Test",
            "picking_type_id": cls.warehouse.pos_type_id.id,
            "block_negative_stock": True,
        })
        cls.session = cls.env["pos.session"].sudo().create({
            "config_id": cls.config.id,
            "update_stock_at_closing": False,
        })
        cls.product = cls.env["product.product"].sudo().create({
            "name": "Guarded Test Product", "is_storable": True,
        })
        cls.location = cls.config.picking_type_id.default_location_src_id

    def test_duplicate_lines_and_refunds(self):
        result = self.guard._aggregate_demand([
            {"product_id": self.product.id, "qty": 2},
            {"product_id": self.product.id, "qty": 3},
            {"product_id": self.product.id, "qty": -4},
        ])
        self.assertEqual(result, {self.product.id: 5})

    def test_invalid_quantity(self):
        for quantity in (float("nan"), float("inf"), "not-a-number"):
            with self.assertRaises(ValidationError):
                self.guard._aggregate_demand([
                    {"product_id": self.product.id, "qty": quantity},
                ])

    def test_zero_stock_is_blocked(self):
        self.assertTrue(self.guard._shortage_message(
            self.session, {self.product.id: 1},
        ))

    def test_exact_available_quantity(self):
        self.env["stock.quant"].sudo()._update_available_quantity(
            self.product, self.location, 2,
        )
        self.assertFalse(self.guard._shortage_message(
            self.session, {self.product.id: 2}, lock=True,
        ))
        self.assertTrue(self.guard._shortage_message(
            self.session, {self.product.id: 3},
        ))

    def test_reservations_are_excluded(self):
        quant_model = self.env["stock.quant"].sudo()
        quant_model._update_available_quantity(self.product, self.location, 3)
        quant_model._update_reserved_quantity(self.product, self.location, 2)
        self.assertTrue(self.guard._shortage_message(
            self.session, {self.product.id: 2},
        ))

    def test_deferred_inventory_is_rejected(self):
        self.session.update_stock_at_closing = True
        self.assertTrue(self.guard._shortage_message(
            self.session, {self.product.id: 1},
        ))

    def test_service_and_refund_only_orders(self):
        service = self.env["product.product"].sudo().create({
            "name": "Test Service", "type": "service",
        })
        self.assertFalse(self.guard._shortage_message(self.session, {service.id: 1}))
        self.assertFalse(self.guard._shortage_message(self.session, {}))

    def test_missing_product_is_rejected(self):
        with self.assertRaises(ValidationError):
            self.guard._shortage_message(self.session, {-1: 1})
