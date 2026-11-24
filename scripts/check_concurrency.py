# SPDX-License-Identifier: Apache-2.0
"""Run through odoo-bin shell on an explicitly disposable acceptance database.

Creates committed synthetic fixtures. Never run against a user database.
"""
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier

from psycopg2.errors import SerializationFailure

from odoo import api
from odoo.exceptions import UserError


def check(env):
    company = env.company
    product = env["product.product"].create({"name": "Concurrent guard test", "is_storable": True})
    source = env["stock.location"].create({
        "name": "Concurrent guard source", "usage": "internal", "company_id": company.id,
    })
    customer = env.ref("stock.stock_location_customers")
    policy = env["inventory.guard.policy"].search([("company_id", "=", company.id)], limit=1)
    if not policy:
        policy = env["inventory.guard.policy"].create({"company_id": company.id})
    policy.write({"enabled": True, "protect_deliveries": True, "location_ids": [(5, 0, 0)]})
    env["stock.quant"]._update_available_quantity(product, source, 1)
    ids = product.id, source.id, customer.id, company.id
    env.cr.commit()  # Test fixtures must be visible to independent transactions.
    barrier = Barrier(2)

    def consume(wait):
        with env.registry.cursor() as cr:
            worker = api.Environment(cr, env.uid, {"allowed_company_ids": [ids[3]]}, su=True)
            stock_product = worker["product.product"].browse(ids[0])
            location = worker["stock.location"].browse(ids[1])
            # Both workers read the same last-unit snapshot before either writes.
            available = worker["inventory.guard.availability"]._free_quantity(stock_product, location)
            if wait:
                assert available == 1, available
                barrier.wait(timeout=30)
            move = worker["stock.move"].create({
                "reference": "Concurrent guard consumption", "product_id": ids[0],
                "product_uom_qty": 1, "uom_id": stock_product.uom_id.id,
                "location_id": ids[1], "location_dest_id": ids[2], "company_id": ids[3],
            })
            line = worker["stock.move.line"].create({
                "move_id": move.id, "product_id": ids[0], "quantity": 1, "picked": True,
                "uom_id": stock_product.uom_id.id, "location_id": ids[1],
                "location_dest_id": ids[2], "company_id": ids[3],
            })
            try:
                line._action_done()
                cr.commit()
                return "completed"
            except SerializationFailure:
                cr.rollback()
                return "retry"
            except UserError:
                cr.rollback()
                return "blocked"

    with ThreadPoolExecutor(max_workers=2) as pool:
        futures = [pool.submit(consume, True) for _ in range(2)]
        outcomes = sorted(future.result(timeout=60) for future in futures)
    assert outcomes == ["completed", "retry"], outcomes
    assert consume(False) == "blocked", "Fresh retry must reject the consumed last unit"
    # The shell cursor still owns its original repeatable-read snapshot. Verify
    # the committed result from a fresh transaction, like Odoo's request retry.
    with env.registry.cursor() as cr:
        observer = api.Environment(cr, env.uid, {"allowed_company_ids": [ids[3]]}, su=True)
        available = observer["inventory.guard.availability"]._free_quantity(
            observer["product.product"].browse(ids[0]),
            observer["stock.location"].browse(ids[1]),
        )
        assert available == 0, available
    print("Concurrent last-unit consumption and fresh retry passed")


if "env" in globals():
    check(env)
