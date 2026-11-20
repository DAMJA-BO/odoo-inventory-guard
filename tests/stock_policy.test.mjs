// SPDX-License-Identifier: Apache-2.0
import assert from "node:assert/strict";
import test from "node:test";
import { positiveDemand, exceedsAvailable, availabilityStatus } from "../pos_stock_guard/static/src/stock/policy.js";

test("duplicate sales accumulate and refunds do not finance sales", () => {
    const lines = [2, 3, -4].map(qty => ({ product_id: { id: 1 }, qty }));
    assert.equal(positiveDemand(lines, 1), 5);
    assert.equal(positiveDemand(lines, 1, lines[0]), 3);
    assert.equal(positiveDemand(lines, 2), 0);
});
test("availability comparison respects UoM rounding and exact stock", () => {
    const stock = { tracked: true, available: 2, rounding: 0.01 };
    assert.equal(exceedsAvailable(2, stock), false);
    assert.equal(exceedsAvailable(2.01, stock), true);
    assert.equal(exceedsAvailable(2.00000001, stock), false);
    assert.equal(exceedsAvailable(0.3, { ...stock, available: 0.1 + 0.2 }), false);
    assert.equal(exceedsAvailable(1, { ...stock, available: -1 }), true);
    assert.equal(exceedsAvailable(99, { tracked: false }), false);
    assert.equal(exceedsAvailable(99, undefined), false);
});
test("low-stock option and custom threshold remain independent", () => {
    const config = { stock_guard_low_stock: true, stock_guard_low_threshold: 3 };
    const stock = { tracked: true, available: 2 };
    assert.equal(availabilityStatus(stock, config), "low");
    assert.equal(availabilityStatus(stock, { ...config, stock_guard_low_threshold: 1 }), "available");
    assert.equal(availabilityStatus(stock, { ...config, stock_guard_low_stock: false }), "available");
    assert.equal(availabilityStatus({ ...stock, available: 0 }, config), "empty");
    assert.equal(availabilityStatus(undefined, config), "unknown");
    assert.equal(availabilityStatus({ tracked: false }, config), "untracked");
});
