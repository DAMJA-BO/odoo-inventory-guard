# SPDX-License-Identifier: Apache-2.0
"""Acceptance tests for the public Inventory validation and counting workflows."""

from odoo import Command
from odoo.addons.base.tests.common import BaseCommon
from odoo.exceptions import UserError
from odoo.tests import tagged


@tagged("post_install", "-at_install")
class TestInventoryGuardStockOperations(BaseCommon):
    _test_user_groups = ("stock.group_stock_manager", "stock.group_stock_multi_locations")

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, lang="en_US"))
        cls.source, cls.destination, cls.transit, cls.loss, cls.scrap = cls.env["stock.location"].create([
            {"name": name, "usage": usage, "company_id": cls.company.id}
            for name, usage in (
                ("Guard source", "internal"), ("Guard destination", "internal"),
                ("Guard transit", "transit"), ("Guard inventory loss", "inventory"),
                ("Guard scrap", "inventory"),
            )
        ])
        cls.vendor = cls.env.ref("stock.stock_location_suppliers")
        cls.customer = cls.env.ref("stock.stock_location_customers")
        cls.product = cls.env["product.product"].create({
            "name": "Guard operation product", "is_storable": True, "property_stock_inventory": cls.loss.id,
        })
        cls.internal, cls.incoming, cls.outgoing = cls.env["stock.picking.type"].create([
            {
                "name": f"Guard {code}", "sequence_code": f"GUARD-{code}", "code": code,
                "company_id": cls.company.id, "warehouse_id": False,
                "default_location_src_id": source.id, "default_location_dest_id": destination.id,
                "reservation_method": "manual", "create_backorder": "ask", "use_existing_lots": True,
            }
            for code, source, destination in (
                ("internal", cls.source, cls.destination), ("incoming", cls.vendor, cls.source),
                ("outgoing", cls.source, cls.customer),
            )
        ])
        cls.incoming.return_picking_type_id = cls.outgoing
        cls.outgoing.return_picking_type_id = cls.incoming
        policies = cls.env["inventory.guard.policy"]
        cls.policy = policies.search([("company_id", "=", cls.company.id)]) or policies.create({})
        cls.policy.write({"enabled": True, "location_ids": [Command.clear()]})

    def _picking(self, operation_type, source, destination, demand):
        return self.env["stock.picking"].create({
            "picking_type_id": operation_type.id,
            "location_id": source.id, "location_dest_id": destination.id,
            "move_ids": [Command.create({
                "product_id": self.product.id, "uom_id": self.product.uom_id.id,
                "product_uom_qty": demand, "location_id": source.id, "location_dest_id": destination.id,
            })],
        })

    def _receive(self, quantity):
        picking = self._picking(self.incoming, self.vendor, self.source, quantity)
        # At this pin, validation of a draft picking fills the done quantity directly.
        self.assertFalse(picking.move_line_ids)
        self.assertIs(picking.button_validate(), True)
        self._assert_done(picking, quantity)
        return picking

    def _return_picking(self, original, quantity):
        # This revision replaced the return transient wizard with a picking form.
        action = original.action_return()
        self.assertEqual(action["res_model"], "stock.picking")
        returned = self.env["stock.picking"].browse(action["res_id"])
        self.assertEqual(returned.state, "draft")
        self.assertEqual(returned.return_id, original)
        self.assertEqual(returned.move_ids.origin_returned_move_id, original.move_ids)
        self.assertEqual(returned.location_id, original.location_dest_id)
        self.assertEqual(returned.location_dest_id, original.location_id)
        returned.action_return_all()
        self.assertEqual(returned.move_ids.product_uom_qty, original.move_ids.quantity)
        returned.move_ids.product_uom_qty = quantity
        return returned

    def _quants(self, location, **dimensions):
        return self.env["stock.quant"].search([
            ("product_id", "=", self.product.id), ("location_id", "=", location.id),
            *((field, "=", value) for field, value in dimensions.items()),
        ])

    def _assert_stock(self, location, physical, reserved=0, **dimensions):
        quants = self._quants(location, **dimensions)
        self.assertEqual(sum(quants.mapped("quantity")), physical, location.display_name)
        self.assertEqual(sum(quants.mapped("reserved_quantity")), reserved, location.display_name)

    def _assert_done(self, picking, quantity):
        self.assertEqual(picking.state, "done")
        self.assertEqual(picking.move_ids.mapped("state"), ["done"])
        self.assertEqual(picking.move_ids.quantity, quantity)
        self.assertEqual(sum(picking.move_line_ids.mapped("quantity")), quantity)

    def _guard_error(self):
        # An RPC failure rolls back the request, including pre-validation writes.
        return self.assertRaisesRegex(UserError, r"Inventory Guard blocked .*Guard source")

    def test_internal_transfer_rejects_overpick_then_moves_exact_stock(self):
        self._receive(2)
        picking = self._picking(self.internal, self.source, self.destination, 2)
        self.assertIs(picking.action_confirm(), True)
        self.assertIs(picking.action_assign(), True)
        self.assertEqual(picking.state, "assigned")
        self._assert_stock(self.source, 2, reserved=2)
        line = picking.move_line_ids
        self.assertEqual(line.quantity, 2)
        line.write({"quantity": 3, "picked": True})
        with self._guard_error(), self.env.cr.savepoint():
            picking.button_validate()
        self.assertEqual(picking.state, "assigned")
        self.assertEqual(line.quantity, 3)
        self._assert_stock(self.source, 2, reserved=3)
        self._assert_stock(self.destination, 0)
        line.quantity = 2
        self.assertIs(picking.button_validate(), True)
        self._assert_done(picking, 2)
        self._assert_stock(self.source, 0)
        self._assert_stock(self.destination, 2)

    def test_partial_delivery_backorder_rejects_shortage_then_completes(self):
        self._receive(2)
        picking = self._picking(self.outgoing, self.source, self.customer, 5)
        picking.action_confirm()
        picking.action_assign()
        self.assertEqual(picking.move_ids.state, "partially_available")
        self.assertEqual(picking.move_line_ids.quantity, 2)
        self._assert_stock(self.source, 2, reserved=2)
        action = picking.button_validate()
        self.assertEqual(action["res_model"], "stock.backorder.confirmation")
        self.assertEqual(picking.move_ids.state, "partially_available")
        self.assertFalse(picking.backorder_ids)
        self._assert_stock(self.source, 2, reserved=2)
        self._assert_stock(self.customer, 0)
        wizard = self.env[action["res_model"]].with_context(action["context"]).create({
            "backorder_confirmation_line_ids": [Command.create({"picking_id": picking.id, "to_backorder": True})],
        })
        self.assertEqual(wizard.pick_ids, picking)
        self.assertIs(wizard.process(), True)
        self._assert_done(picking, 2)
        self._assert_stock(self.source, 0)
        self._assert_stock(self.customer, 2)

        backorder = picking.backorder_ids
        self.assertEqual(len(backorder), 1)
        self.assertEqual(backorder.state, "confirmed")
        self.assertEqual(backorder.move_ids.product_uom_qty, 3)
        self.assertFalse(backorder.move_line_ids)
        with self.assertRaisesRegex(UserError, r"zero quantity transfer"), self.env.cr.savepoint():
            backorder.button_validate()
        backorder.move_ids.quantity = 3
        self.assertEqual(backorder.state, "assigned")
        with self._guard_error(), self.env.cr.savepoint():
            backorder.button_validate()
        self.assertEqual(backorder.state, "assigned")
        self.assertFalse(backorder.date_done)
        self.assertFalse(backorder.backorder_ids)
        self._assert_stock(self.source, 0, reserved=3)
        self._assert_stock(self.customer, 2)

        # Replace the manually entered quantity with a real reservation.
        backorder.move_ids.quantity = 0
        self._receive(3)
        backorder.action_assign()
        self.assertEqual(backorder.state, "assigned")
        self._assert_stock(self.source, 3, reserved=3)
        self.assertIs(backorder.button_validate(), True)
        self._assert_done(backorder, 3)
        self._assert_stock(self.source, 0)
        self._assert_stock(self.customer, 5)

    def test_receipt_and_vendor_return(self):
        receipt = self._receive(2)
        self._assert_stock(self.vendor, -2)
        self._assert_stock(self.source, 2)
        # Return the original receipt after one unit is no longer on hand.
        delivery = self._picking(self.outgoing, self.source, self.customer, 1)
        self.assertIs(delivery.button_validate(), True)
        returned = self._return_picking(receipt, 2)
        returned.action_confirm()
        # Return confirmation can reserve the available unit; manually record an
        # attempt to ship both so validation tests the shortage, not a backorder.
        returned.move_ids.quantity = 2
        returned.move_ids.picked = True
        state_before = returned.state
        with self._guard_error(), self.env.cr.savepoint():
            returned.button_validate()
        self.assertEqual(returned.state, state_before)
        self.assertEqual(returned.move_ids.quantity, 2)
        self.assertFalse(returned.backorder_ids)
        self._assert_stock(self.source, 1, reserved=2)
        self._assert_stock(self.vendor, -2)
        returned.move_ids.quantity = 1
        returned.move_ids.product_uom_qty = 1
        self.assertIs(returned.button_validate(), True)
        self._assert_done(returned, 1)
        self._assert_stock(self.source, 0)
        self._assert_stock(self.vendor, -1)

    def test_customer_return_credits_internal_stock(self):
        self._receive(2)
        delivery = self._picking(self.outgoing, self.source, self.customer, 2)
        self.assertIs(delivery.button_validate(), True)
        self._assert_done(delivery, 2)
        self._assert_stock(self.source, 0)
        self._assert_stock(self.customer, 2)
        returned = self._return_picking(delivery, 1)
        self.assertIs(returned.button_validate(), True)
        self._assert_done(returned, 1)
        self._assert_stock(self.source, 1)
        self._assert_stock(self.customer, 1)

    def test_internal_to_transit_is_protected_but_transit_source_is_excluded(self):
        self._receive(1)
        dispatch = self._picking(self.internal, self.source, self.transit, 2)
        with self._guard_error(), self.env.cr.savepoint():
            dispatch.button_validate()
        self.assertEqual(dispatch.state, "draft")
        self._assert_stock(self.source, 1)
        self._assert_stock(self.transit, 0)
        dispatch.move_ids.product_uom_qty = 1
        self.assertIs(dispatch.button_validate(), True)
        self._assert_done(dispatch, 1)
        self._assert_stock(self.source, 0)
        self._assert_stock(self.transit, 1)

        arrival = self._picking(self.internal, self.transit, self.destination, 2)
        self.assertIs(arrival.button_validate(), True)
        self._assert_done(arrival, 2)
        self._assert_stock(self.transit, -1)
        self._assert_stock(self.destination, 2)

    def test_scrap_warning_confirmation_is_blocked_by_guard(self):
        self._receive(2)
        scrap = self.env["stock.move"].create({
            "product_id": self.product.id, "uom_id": self.product.uom_id.id,
            "company_id": self.company.id, "is_scrap": True,
            "location_id": self.source.id, "location_dest_id": self.scrap.id,
            "product_uom_qty": 3,
        })
        scrap.quantity = 3
        # Entering the scrap quantity creates reserved move lines before validation.
        self.assertEqual(scrap.state, "assigned")
        reserved = sum(self._quants(self.source).mapped("reserved_quantity"))
        action = scrap.action_scrap()
        self.assertEqual(action["res_model"], "stock.warn.insufficient.qty.scrap")
        self.assertEqual(scrap.state, "assigned")
        self._assert_stock(self.source, 2, reserved=reserved)
        self._assert_stock(self.scrap, 0)
        wizard = self.env[action["res_model"]].with_context(action["context"]).create({})
        self.assertEqual(wizard.scrap_move_id, scrap)
        with self._guard_error(), self.env.cr.savepoint():
            wizard.action_done()
        self.assertEqual(scrap.state, "assigned")
        self.assertEqual(scrap.quantity, 3)
        self._assert_stock(self.source, 2, reserved=reserved)
        self._assert_stock(self.scrap, 0)
        scrap.write({"product_uom_qty": 2, "quantity": 2})
        scrap.action_scrap()
        self.assertEqual(scrap.state, "done")
        self.assertTrue(scrap.is_scrap)
        self.assertEqual(scrap.quantity, 2)
        self._assert_stock(self.source, 0)
        self._assert_stock(self.scrap, 2)

    def _inventory_moves(self):
        return self.env["stock.move"].search([("product_id", "=", self.product.id), ("is_inventory", "=", True)])

    def test_inventory_count_allows_decrease_to_zero_not_below(self):
        self._receive(2)
        quant = self._quants(self.source).with_context(inventory_mode=True)
        quant.inventory_quantity = -1
        with self._guard_error(), self.env.cr.savepoint():
            quant.action_apply_inventory()
        self.assertTrue(quant.inventory_quantity_set)
        self.assertEqual(quant.inventory_quantity, -1)
        self.assertFalse(self._inventory_moves())
        self._assert_stock(self.source, 2)
        self._assert_stock(self.loss, 0)

        quant.inventory_quantity = 0
        self.assertIsNone(quant.action_apply_inventory())
        move = self._inventory_moves()
        self.assertEqual((move.state, move.quantity, move.location_dest_id), ("done", 2, self.loss))
        self.assertFalse(quant.inventory_quantity_set)
        self._assert_stock(self.source, 0)
        self._assert_stock(self.loss, 2)

    def test_inventory_count_can_improve_a_legacy_negative_balance(self):
        # A historical negative balance is fixture data, not a validation bypass.
        self.env["stock.quant"]._update_available_quantity(self.product, self.source, -3)
        quant = self._quants(self.source).with_context(inventory_mode=True)
        quant.inventory_quantity = -2
        self.assertIsNone(quant.action_apply_inventory())
        move = self._inventory_moves()
        self.assertEqual((move.state, move.quantity, move.location_id), ("done", 1, self.loss))
        self.assertFalse(quant.inventory_quantity_set)
        self._assert_stock(self.source, -2)
        self._assert_stock(self.loss, -1)

        quant.inventory_quantity = -3
        with self._guard_error(), self.env.cr.savepoint():
            quant.action_apply_inventory()
        self.assertEqual(self._inventory_moves(), move)
        self.assertEqual(quant.inventory_quantity, -3)
        self._assert_stock(self.source, -2)
        self._assert_stock(self.loss, -1)

    def test_validation_distinguishes_missing_serial_from_source_shortage(self):
        # Configure the fixture as an administrator; validate pickings as the stock manager.
        self.product.sudo().tracking = "serial"
        existing, missing = self.env["stock.lot"].create([
            {"name": name, "product_id": self.product.id, "company_id": self.company.id}
            for name in ("Guard SN available", "Guard SN absent")
        ])
        receipt = self._picking(self.incoming, self.vendor, self.source, 1)
        receipt.move_ids.quantity = 1
        receipt.move_line_ids.lot_id = existing
        self.assertIs(receipt.button_validate(), True)
        self._assert_done(receipt, 1)

        picking = self._picking(self.outgoing, self.source, self.customer, 1)
        picking.action_confirm()
        picking.action_assign()
        line = picking.move_line_ids
        line.write({"lot_id": False, "picked": True})
        with self.assertRaisesRegex(UserError, r"supply a Lot/Serial number"), self.env.cr.savepoint():
            picking.button_validate()
        self.assertEqual(picking.state, "assigned")

        line.lot_id = missing
        with self._guard_error(), self.env.cr.savepoint():
            picking.button_validate()
        self.assertEqual(picking.state, "assigned")
        self._assert_stock(self.source, 1, lot_id=existing.id)
        self._assert_stock(self.source, 0, lot_id=missing.id)
        self._assert_stock(self.customer, 0)
        line.lot_id = existing
        self.assertIs(picking.button_validate(), True)
        self._assert_done(picking, 1)
        self.assertEqual(line.lot_id, existing)
        self._assert_stock(self.source, 0)
        self._assert_stock(self.customer, 1, lot_id=existing.id)

    def test_done_delivery_line_edit_restores_original_on_rejection(self):
        self._receive(2)
        picking = self._picking(self.outgoing, self.source, self.customer, 1)
        self.assertIs(picking.button_validate(), True)
        line = picking.move_line_ids
        # Catch without an outer savepoint: the addon must undo both quant changes
        # and the write on the done line, even when the caller catches the error.
        with self._guard_error():
            line.write({"quantity": 3})
        self._assert_done(picking, 1)
        self.assertEqual(line.quantity, 1)
        self._assert_stock(self.source, 1)
        self._assert_stock(self.customer, 1)

        line.write({"quantity": 2})
        self._assert_done(picking, 2)
        self._assert_stock(self.source, 0)
        self._assert_stock(self.customer, 2)
