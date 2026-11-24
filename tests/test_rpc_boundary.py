# SPDX-License-Identifier: Apache-2.0
"""Execute the actual demand parser with only the Odoo import boundary adapted."""
import importlib.util
from pathlib import Path
import sys
import types
import unittest
from unittest.mock import patch


class ValidationError(Exception):
    pass


def load_guard():
    odoo = types.ModuleType("odoo")
    odoo._ = lambda text: text
    odoo.api = types.SimpleNamespace(model=lambda method: method)
    odoo.models = types.SimpleNamespace(AbstractModel=object)
    exceptions = types.ModuleType("odoo.exceptions")
    exceptions.ValidationError = ValidationError
    path = Path(__file__).resolve().parents[1] / "pos_inventory_guard/models/inventory_guard.py"
    spec = importlib.util.spec_from_file_location("guard_under_test", path)
    module = importlib.util.module_from_spec(spec)
    with patch.dict(sys.modules, {"odoo": odoo, "odoo.exceptions": exceptions}):
        spec.loader.exec_module(module)
    return module.PosInventoryGuard()


class DemandBoundaryTest(unittest.TestCase):
    def test_malformed_input_is_a_validation_error(self):
        guard = load_guard()
        for lines in (None, {}, "bad", [None], [1], [{"product_id": 0}],
                      [{"product_id": -1}], [{"product_id": True}],
                      [{"product_id": 1, "qty": True}],
                      [{"product_id": 1, "qty": 10 ** 1000}],
                      [{"product_id": 1, "qty": 1}] * 1001):
            with self.subTest(lines_type=type(lines)), self.assertRaises(ValidationError):
                guard._aggregate_demand(lines)

    def test_sales_accumulate_without_refund_credit(self):
        guard = load_guard()
        self.assertEqual(guard._aggregate_demand([
            {"product_id": 1, "qty": 2}, {"product_id": 1, "qty": 3},
            {"product_id": 1, "qty": -4},
        ]), {1: 5})


if __name__ == "__main__":
    unittest.main()
