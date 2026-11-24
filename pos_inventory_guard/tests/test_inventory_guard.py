# SPDX-License-Identifier: Apache-2.0
"""Stock-policy regression tests requiring a disposable Odoo 20 database."""

from odoo.exceptions import AccessError, ValidationError
from odoo.tests import tagged
from odoo.tests.common import new_test_user
from odoo.addons.account.tests.common import AccountTestInvoicingCommon


@tagged("post_install", "-at_install")
class TestInventoryGuard(AccountTestInvoicingCommon):
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
            "name": "Inventory Guard Test",
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

    def test_pos_loader_keeps_standard_and_guard_fields(self):
        records = self.config._load_pos_data_read(self.config, self.config)
        self.assertIn("use_pricelist", records[0])
        self.assertTrue(records[0]["block_negative_stock"])

    def test_settings_field_updates_selected_pos(self):
        settings = self.env["res.config.settings"].sudo().create({
            "pos_config_id": self.config.id,
            "pos_block_negative_stock": False,
        })
        self.assertFalse(settings.pos_block_negative_stock)
        self.assertFalse(self.config.block_negative_stock)

    def test_native_shortcut_opens_selected_pos_in_central_form(self):
        manager = new_test_user(
            self.env, login="inventory_guard_settings_manager",
            groups="base.group_system,point_of_sale.group_pos_manager",
            company_id=self.config.company_id.id,
        )
        settings = self.env["res.config.settings"].with_user(manager).sudo().create({
            "pos_config_id": self.config.id,
        })
        action = settings.with_user(manager).action_open_inventory_guard()
        self.assertEqual(action["res_id"], self.config.id)
        view = self.env.ref("pos_inventory_guard.inventory_guard_pos_form")
        self.assertEqual(action["views"], [(view.id, "form")])

    def test_cashier_cannot_open_configuration(self):
        cashier = new_test_user(
            self.env, login="guard_cashier", groups="point_of_sale.group_pos_user",
            company_id=self.config.company_id.id,
        )
        with self.assertRaises(AccessError):
            self.config.with_user(cashier).action_open_inventory_guard()

    def test_optional_settings_are_scoped_to_selected_pos(self):
        other = self.config.copy({"name": "Other POS"})
        self.env["res.config.settings"].sudo().create({
            "pos_config_id": self.config.id,
            "pos_inventory_guard_show_badges": True,
            "pos_inventory_guard_display_mode": "color",
            "pos_inventory_guard_block_add": True,
            "pos_inventory_guard_limit_quantity": True,
            "pos_inventory_guard_show_order": True,
            "pos_inventory_guard_available_filter": True,
            "pos_inventory_guard_low_stock": True,
            "pos_inventory_guard_low_threshold": 7,
            "pos_inventory_guard_auto_refresh": True,
            "pos_inventory_guard_refresh_seconds": 45,
        })
        self.assertTrue(self.config.inventory_guard_show_badges)
        self.assertEqual(self.config.inventory_guard_display_mode, "color")
        self.assertEqual(self.config.inventory_guard_low_threshold, 7)
        self.assertEqual(self.config.inventory_guard_refresh_seconds, 45)
        self.assertFalse(other.inventory_guard_show_badges)
        self.assertFalse(other.inventory_guard_block_add)
        self.assertEqual(other.inventory_guard_refresh_seconds, 30)
        self.assertEqual(other.inventory_guard_low_threshold, 3)

    def test_invalid_settings_are_rejected(self):
        for values in (
            {"inventory_guard_low_threshold": -1},
            {"inventory_guard_refresh_seconds": 0},
            {"inventory_guard_refresh_seconds": 4},
        ):
            with self.assertRaises(ValidationError), self.env.cr.savepoint():
                self.config.write(values)

    def test_availability_snapshot_excludes_reservations_and_other_locations(self):
        manager = new_test_user(
            self.env, login="inventory_guard_pos_manager",
            groups="point_of_sale.group_pos_manager",
            company_id=self.env.company.id,
        )
        quant_model = self.env["stock.quant"].sudo()
        quant_model._update_available_quantity(self.product, self.location, 3)
        quant_model._update_reserved_quantity(self.product, self.location, 2)
        other_location = self.env["stock.location"].sudo().create({
            "name": "Outside POS source", "usage": "internal",
            "company_id": self.env.company.id,
        })
        quant_model._update_available_quantity(self.product, other_location, 20)
        result = self.env["pos.config"].with_user(manager).get_inventory_guard_availability(
            self.config.id, [self.product.id],
        )
        stock = result["products"][self.product.id]
        self.assertTrue(stock["tracked"])
        self.assertEqual(stock["available"], 1)
        self.assertEqual(
            stock["rounding"],
            10.0 ** -self.env["decimal.precision"].precision_get("Product Unit"),
        )
        self.assertTrue(self.guard._shortage_message(self.session, {self.product.id: 2}))
        with self.assertRaises(ValidationError):
            self.env["pos.config"].with_user(manager).get_inventory_guard_availability(
                self.config.id, [self.product.id] * 201,
            )

    def test_non_pos_user_cannot_read_stock_snapshot(self):
        user = new_test_user(self.env, login="inventory_guard_non_pos", groups="base.group_user")
        with self.assertRaises(AccessError):
            self.env["pos.config"].with_user(user).get_inventory_guard_availability(
                self.config.id, [self.product.id],
            )

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

    def test_frontend_translation_module_is_available(self):
        self.assertIn(
            "pos_inventory_guard",
            self.env["ir.http"]._get_translation_frontend_modules_name(),
        )
