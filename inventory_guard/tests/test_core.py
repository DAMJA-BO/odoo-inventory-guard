# SPDX-License-Identifier: Apache-2.0
"""Database acceptance tests; run on a disposable Odoo 20 instance."""
from unittest.mock import patch

from odoo.exceptions import UserError
from odoo.tests import tagged
from odoo.tests.common import TransactionCase, new_test_user


@tagged("post_install", "-at_install")
class TestInventoryGuardCore(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(su=True)
        cls.source = cls.env["stock.location"].create({
            "name": "Guard source", "usage": "internal", "company_id": cls.env.company.id,
        })
        cls.customer = cls.env.ref("stock.stock_location_customers")
        cls.product = cls.env["product.product"].create({"name": "Core test product", "is_storable": True})
        cls.policy = cls.env["inventory.guard.policy"].create({"name": "Test policy"})

    def _line(self, quantity):
        move = self.env["stock.move"].create({
            "reference": "Guard test", "product_id": self.product.id,
            "product_uom_qty": quantity, "uom_id": self.product.uom_id.id,
            "location_id": self.source.id, "location_dest_id": self.customer.id,
            "company_id": self.env.company.id,
        })
        return self.env["stock.move.line"].create({
            "move_id": move.id, "product_id": self.product.id,
            "uom_id": self.product.uom_id.id, "quantity": quantity,
            "location_id": self.source.id, "location_dest_id": self.customer.id,
            "company_id": self.env.company.id,
        })

    def _stock(self, quantity):
        self.env["stock.quant"]._update_available_quantity(self.product, self.source, quantity)

    def _physical(self):
        return sum(self.env["stock.quant"].search([
            ("product_id", "=", self.product.id), ("location_id", "=", self.source.id),
        ]).mapped("quantity"))

    def test_installed_policy_is_disabled(self):
        self.assertFalse(self.policy.enabled)
        self._line(1)._action_done()
        self.assertEqual(self._physical(), -1)

    def test_company_sections_share_one_policy(self):
        self.policy.unlink()
        manager = new_test_user(
            self.env, login="inventory_guard_core_manager", groups="stock.group_stock_manager",
            company_id=self.env.company.id,
        )
        policies = self.env["inventory.guard.policy"]
        general = self.env.ref("inventory_guard.policy_general_action").with_user(manager).run()
        operations = self.env.ref("inventory_guard.policy_operations_action").with_user(manager).run()
        self.assertEqual(general["res_id"], operations["res_id"])
        self.assertNotEqual(general["views"], operations["views"])
        self.assertFalse(policies.browse(general["res_id"]).enabled)

    def test_shortage_rolls_back_even_if_caller_catches(self):
        self.policy.enabled = True
        with self.assertRaises(UserError):
            self._line(1)._action_done()
        self.assertEqual(self._physical(), 0)

    def test_exact_stock_succeeds(self):
        self.policy.enabled = True
        self._stock(2)
        self._line(2)._action_done()
        self.assertEqual(self._physical(), 0)

    def test_later_shortage_rolls_back_entire_batch(self):
        self.policy.enabled = True
        self._stock(2)
        lines = self._line(1) | self._line(2)
        # Odoo may free/reduce another unpicked line's reservation while
        # completing the first line. Mark both as physically picked so this
        # scenario really attempts three units, rather than an adjusted two.
        lines.write({"picked": True})
        self.assertEqual(sum(lines.mapped("quantity_product_uom")), 3)
        with self.assertRaises(UserError):
            lines._action_done()
        self.assertEqual(self._physical(), 2)
        self.assertEqual(sum(lines.mapped("quantity_product_uom")), 3)

    def test_reserved_physical_stock_is_not_subtracted_twice(self):
        self.policy.enabled = True
        self._stock(2)
        self.env["stock.quant"]._update_reserved_quantity(self.product, self.source, 2)
        self._line(2)._action_done()
        self.assertEqual(self._physical(), 0)

    def test_disabled_operation_preserves_standard_behavior(self):
        self.policy.write({"enabled": True, "protect_deliveries": False})
        self._line(1)._action_done()
        self.assertEqual(self._physical(), -1)

    def test_positive_correction_is_allowed(self):
        self._stock(-2)
        self.policy.enabled = True
        self._line(1)._synchronize_quant(1, self.source)
        self.assertEqual(self._physical(), -1)

    def test_transit_is_excluded(self):
        self.policy.enabled = True
        self.source.usage = "transit"
        self._line(1)._action_done()
        self.assertEqual(self._physical(), -1)

    def test_location_scope_includes_children(self):
        parent = self.env["stock.location"].create({
            "name": "Protected parent", "usage": "view", "company_id": self.env.company.id,
        })
        root = self.source.copy({"name": "Protected root", "location_id": parent.id})
        self.source.location_id = root
        self.policy.write({"enabled": True, "location_ids": [(6, 0, root.ids)]})
        with self.assertRaises(UserError):
            self._line(1)._action_done()

    def test_unrelated_location_is_not_protected(self):
        other = self.source.copy({"name": "Other root"})
        self.policy.write({"enabled": True, "location_ids": [(6, 0, other.ids)]})
        self._line(1)._action_done()
        self.assertEqual(self._physical(), -1)

    def test_other_owner_cannot_finance_consumption(self):
        self.policy.enabled = True
        owner = self.env["res.partner"].create({"name": "Consignment owner"})
        self.env["stock.quant"]._update_available_quantity(self.product, self.source, 2, owner_id=owner)
        with self.assertRaises(UserError):
            self._line(1)._action_done()
        self.assertEqual(self._physical(), 2)

    def test_other_lot_cannot_finance_consumption(self):
        self.product.tracking = "lot"
        lots = self.env["stock.lot"].create([
            {"name": name, "product_id": self.product.id, "company_id": self.env.company.id}
            for name in ("Available lot", "Empty lot")
        ])
        self.env["stock.quant"]._update_available_quantity(self.product, self.source, 2, lot_id=lots[0])
        self.policy.enabled = True
        line = self._line(1)
        line.lot_id = lots[1]
        with self.assertRaises(UserError):
            line._action_done()
        self.assertEqual(self._physical(), 2)

    def test_company_policy_does_not_apply_to_another_company(self):
        other_company = self.env["res.company"].create({"name": "Other guard company"})
        other_source = self.source.copy({"company_id": other_company.id})
        self.policy.enabled = True
        self.assertFalse(self.env["inventory.guard.policy"]._for_source(
            other_company, other_source, "deliveries",
        ))

    def test_caller_context_cannot_disable_policy(self):
        self.policy.enabled = True
        with self.assertRaises(UserError):
            self._line(1).with_context(inventory_guard_skip=True, bypass_inventory_guard=True)._action_done()

    def test_internal_transfer_and_vendor_return_shortages(self):
        self.policy.enabled = True
        for usage in ("internal", "supplier", "production", "inventory"):
            with self.subTest(usage=usage), self.env.cr.savepoint():
                destination = self.env["stock.location"].create({
                    "name": "Guard destination", "usage": usage,
                    "company_id": self.env.company.id,
                })
                line = self._line(1)
                line.move_id.location_dest_id = destination
                line.location_dest_id = destination
                with self.assertRaises(UserError):
                    line._action_done()
                self.assertEqual(self._physical(), 0)

    def test_fractional_completion_preserves_remainder(self):
        self.policy.enabled = True
        self._stock(1)
        self._line(0.25)._action_done()
        self.assertAlmostEqual(self._physical(), 0.75)
        with self.assertRaises(UserError):
            self._line(0.76)._action_done()
        self.assertAlmostEqual(self._physical(), 0.75)

    def test_other_package_cannot_finance_consumption(self):
        package = self.env["stock.package"].create({"name": "Reserved package"})
        self.env["stock.quant"]._update_available_quantity(
            self.product, self.source, 2, package_id=package,
        )
        self.policy.enabled = True
        with self.assertRaises(UserError):
            self._line(1)._action_done()
        self.assertEqual(self._physical(), 2)

    def test_free_quantities_match_single_product_calculation(self):
        availability = self.env["inventory.guard.availability"]
        tracked = self.env["product.product"].create({
            "name": "Core tracked product", "is_storable": True, "tracking": "lot",
        })
        empty = self.env["product.product"].create({"name": "Core empty product", "is_storable": True})
        lot = self.env["stock.lot"].create({
            "name": "Batch lot", "product_id": tracked.id, "company_id": self.env.company.id,
        })
        child = self.source.copy({"name": "Guard child", "location_id": self.source.id})
        owner = self.env["res.partner"].create({"name": "Batch owner"})
        quants = self.env["stock.quant"]
        quants._update_available_quantity(self.product, self.source, 5)
        quants._update_available_quantity(self.product, child, 2, owner_id=owner)
        quants._update_available_quantity(tracked, child, 3, lot_id=lot)
        quants._update_reserved_quantity(self.product, self.source, 1)
        products = self.product | tracked | empty
        result = availability._free_quantities(products, self.source)
        self.assertEqual(set(result), set(products.ids))
        self.assertEqual(result[empty.id], 0)
        for product in products:
            self.assertAlmostEqual(
                result[product.id],
                quants._get_available_quantity(product, self.source, strict=False, allow_negative=True),
                msg=product.name,
            )
        self.assertAlmostEqual(result[self.product.id], 6)
        self.assertAlmostEqual(result[tracked.id], 3)

    def test_free_quantities_does_not_query_each_product(self):
        products = self.product | self.env["product.product"].create({
            "name": "Core second product", "is_storable": True,
        })
        self._stock(2)
        quant_model = type(self.env["stock.quant"])
        with patch.object(quant_model, "_get_available_quantity", side_effect=AssertionError("per product")):
            result = self.env["inventory.guard.availability"]._free_quantities(products, self.source)
        self.assertAlmostEqual(result[self.product.id], 2)
        self.assertEqual(result[products[1].id], 0)
