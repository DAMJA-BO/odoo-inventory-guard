// SPDX-License-Identifier: Apache-2.0
/** Execute the actual addon patches against a small Odoo boundary adapter.
 * Real Odoo installation/rendering is tested separately on Odoo.sh.
 */
import assert from "node:assert/strict";
import test, { mock } from "node:test";
import fs from "node:fs/promises";
import vm from "node:vm";
import path from "node:path";
import { fileURLToPath } from "node:url";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../pos_inventory_guard/static/src/stock");
const context = vm.createContext({ console, setTimeout, clearTimeout, Date });
const cache = new Map();
const patches = (target, extension) => {
    const parent = Object.create(Object.getPrototypeOf(target), Object.getOwnPropertyDescriptors(target));
    Object.setPrototypeOf(extension, parent);
    Object.defineProperties(target, Object.getOwnPropertyDescriptors(extension));
};
class Store {
    async handleOrderLineConfiguration() { return {}; }
    filterExcludedProducts(products) { return Array.from(products).slice(0, 100); }
    tryMergeOrderline(callback) { return callback(); }
    async loadNewProducts() { return {}; }
}
class Line {
    setQuantity(quantity) { this.qty = quantity; return true; }
}
let currentPos;
const mounted = [];
const unmounted = [];
class Card {}
class OrderlineComponent {
    get line() { return this.props.line; }
    get lineContainerClasses() { return { selected: true }; }
}
class Screen {
    setup() { this.pos = currentPos; }
    get currentOrder() { return this.pos.getOrder(); }
}
const translation = (text, ...args) => text.replace(/%s/g, () => String(args.shift()));
const stubs = {
    "@odoo/owl": {
        proxy: value => value,
        onMounted: callback => mounted.push(callback),
        onWillUnmount: callback => unmounted.push(callback),
    },
    "@web/core/utils/patch": { patch: patches },
    "@web/core/l10n/translation": { _t: translation },
    "@web/core/confirmation_dialog/confirmation_dialog": { AlertDialog: class {} },
    "@web/views/fields/parsers": { parseFloat: Number },
    "@point_of_sale/app/services/pos_store": { PosStore: Store },
    "@point_of_sale/app/models/pos_order_line": { PosOrderline: Line },
    "@point_of_sale/app/hooks/pos_hook": { usePos: () => currentPos },
    "@point_of_sale/app/components/product_card/product_card": { ProductCard: Card },
    "@point_of_sale/app/components/orderline/orderline": { Orderline: OrderlineComponent },
    "@point_of_sale/app/screens/product_screen/product_screen": { ProductScreen: Screen },
};
async function load(specifier, parent) {
    const id = specifier.startsWith("@") ? specifier :
        path.resolve(parent ? path.dirname(parent) : root, specifier.endsWith(".js") ? specifier : specifier + ".js");
    if (cache.has(id)) return cache.get(id);
    let module;
    if (stubs[id]) {
        module = new vm.SyntheticModule(Object.keys(stubs[id]), function () {
            for (const [key, value] of Object.entries(stubs[id])) this.setExport(key, value);
        }, { context, identifier: id });
    } else {
        module = new vm.SourceTextModule(await fs.readFile(id, "utf8"), { context, identifier: id });
    }
    cache.set(id, module);
    await module.link((child, referring) => load(child, referring.identifier));
    return module;
}
for (const name of ["store_patch", "order_line_patch", "components_patch"]) {
    await (await load("./" + name)).evaluate();
}
const runtime = cache.get(path.join(root, "runtime.js")).namespace.stockRuntime;
let configId = 0;
function fixture(options = {}, availability = 2) {
    const config = { id: ++configId, inventory_guard_block_add: true, ...options };
    const product = { id: 1, display_name: "Test", uom_id: { factor: 1 } };
    const order = { state: "draft", lines: [] };
    const store = new Store();
    store.config = config;
    store.models = {
        "product.product": { getAll: () => [product] },
        "product.uom": { getBy: () => undefined },
    };
    store.alerts = [];
    store.dialog = { add: (_, props) => store.alerts.push(props) };
    store.data = { call: async () => ({
        products: { 1: { tracked: true, available: availability, rounding: 0.01 } },
        location: "WH/Stock",
    }) };
    const line = new Line();
    Object.assign(line, { product_id: product, qty: 1, order_id: order, config, combo_line_ids: [] });
    order.lines.push(line);
    return { config, product, order, store, line };
}

test("adding zero stock is stopped before line creation; disabled options do not call RPC", async () => {
    const f = fixture({}, 0);
    assert.equal(await f.store.handleOrderLineConfiguration(f.order, { product_id: f.product, qty: 1 }), false);
    assert.equal(f.store.alerts.length, 1);
    f.config.inventory_guard_block_add = false;
    f.store.data.call = () => { throw Error("must not call"); };
    assert.notEqual(await f.store.handleOrderLineConfiguration(f.order, { product_id: f.product, qty: 1 }), false);
});
test("quantity check aggregates duplicate lines and barcode quantities", async () => {
    const f = fixture({ inventory_guard_limit_quantity: true }, 2);
    assert.notEqual(await f.store.handleOrderLineConfiguration(f.order, { product_id: f.product, qty: 1 }), false);
    assert.equal(await f.store.handleOrderLineConfiguration(f.order, { product_id: f.product, qty: 2 }), false);
    assert.equal(await f.store.handleOrderLineConfiguration(f.order, { product_id: f.product, qty: 1 },
        { type: "quantity", value: 3 }), false);
    f.store.models["product.uom"].getBy = () => ({ uom_id: { factor: 5 } });
    assert.equal(await f.store.handleOrderLineConfiguration(f.order, { product_id: f.product, qty: 1 },
        { type: "product", code: "PACK" }), false);
});
test("refunds remain possible and service stock is not limited", async () => {
    const f = fixture({ inventory_guard_limit_quantity: true }, 0);
    assert.notEqual(await f.store.handleOrderLineConfiguration(f.order, { product_id: f.product, qty: -1 }), false);
    f.order.preset_id = { is_return: true };
    assert.notEqual(await f.store.handleOrderLineConfiguration(f.order,
        { product_id: f.product, qty: -1 }, { type: "quantity", value: 5 }), false);
    f.order.preset_id = undefined;
    f.store.data.call = async () => ({ products: { 1: { tracked: false, available: 0 } } });
    assert.notEqual(await f.store.handleOrderLineConfiguration(f.order, { product_id: f.product, qty: 50 }), false);
});
test("quantity edits refuse excess, allow reduction and preserve isolated POS settings", async () => {
    const f = fixture({ inventory_guard_limit_quantity: true }, 2);
    await f.store.refreshInventoryGuard();
    assert.equal(f.line.setQuantity(2), true);
    assert.equal(typeof f.line.setQuantity(3), "object");
    assert.equal(f.line.qty, 2);
    assert.equal(f.line.setQuantity(1), true);
    const other = fixture({ inventory_guard_limit_quantity: false }, 0);
    assert.equal(other.line.setQuantity(10), true);
    assert.equal(f.line.qty, 1);
});
test("internal merges do not double-count the incoming line", async () => {
    const f = fixture({ inventory_guard_limit_quantity: true }, 2);
    await f.store.refreshInventoryGuard();
    f.order.lines.push({ product_id: f.product, qty: 1 });
    assert.equal(f.store.tryMergeOrderline(() => f.line.setQuantity(2)), true);
    assert.equal(runtime(f.config).merging, false);
});
test("network errors fail early checks closed and mark snapshots stale", async () => {
    const f = fixture();
    await f.store.refreshInventoryGuard();
    f.store.data.call = async () => { throw Error("offline"); };
    assert.equal(await f.store.handleOrderLineConfiguration(f.order, { product_id: f.product, qty: 1 }), false);
    assert.equal(runtime(f.config).failed, true);
    assert.equal(runtime(f.config).products[1].available, 2);
});
test("refresh failures are logged instead of swallowed", async () => {
    const f = fixture();
    const logged = mock.method(console, "error", () => {});
    try {
        f.store.data.call = async () => { throw Error("offline"); };
        assert.equal(await f.store.refreshInventoryGuard(), false);
        assert.equal(logged.mock.callCount(), 1);
        assert.match(String(logged.mock.calls[0].arguments.join(" ")), /offline/);
    } finally {
        logged.mock.restore();
    }
});
test("available filter is temporary; unknown and untracked products remain visible", async () => {
    const f = fixture({ inventory_guard_available_filter: true }, 0);
    await f.store.refreshInventoryGuard();
    const products = [
        { id: 11, product_variant_ids: [f.product] },
        { id: 12, product_variant_ids: [{ id: 2 }] },
    ];
    assert.equal(f.store.filterExcludedProducts(products).length, 2);
    runtime(f.config).onlyAvailable = true;
    assert.equal(f.store.filterExcludedProducts(products).length, 1);
    runtime(f.config).onlyAvailable = false;
    assert.equal(f.store.filterExcludedProducts(products).length, 2);
});
test("combo child shortage blocks addition and parent quantity edits", async () => {
    const f = fixture({ inventory_guard_limit_quantity: true }, 2);
    const service = { id: 2, display_name: "Combo" };
    f.store.data.call = async () => ({ products: {
        1: { tracked: true, available: 2, rounding: 0.01 },
        2: { tracked: false, available: 0 },
    } });
    assert.equal(await f.store.handleOrderLineConfiguration(f.order, {
        product_id: service, qty: 1,
        combo_line_ids: [["create", { product_id: f.product, qty: 3 }]],
    }), false);
    const parent = new Line();
    Object.assign(parent, { product_id: service, qty: 1, order_id: f.order, config: f.config,
        combo_line_ids: [f.line] });
    f.order.lines.push(parent);
    assert.equal(typeof parent.setQuantity(3), "object");
    assert.equal(parent.qty, 1);
    assert.equal(f.line.qty, 1);
});
test("snapshot refreshes use bounded batches and are serialized", async () => {
    const f = fixture();
    let active = 0;
    let maximum = 0;
    let batches = [];
    f.store.data.call = async (_, __, args) => {
        maximum = Math.max(maximum, ++active);
        batches.push(args[1].length);
        await new Promise(resolve => setTimeout(resolve, 2));
        active--;
        return { products: {}, location: "WH/Stock" };
    };
    await Promise.all([
        f.store.refreshInventoryGuard(Array.from({ length: 450 }, (_, i) => i + 1)),
        f.store.refreshInventoryGuard([1]),
        f.store.refreshInventoryGuard([2]),
    ]);
    assert.equal(maximum, 1);
    assert.deepEqual(batches, [200, 200, 50, 1, 1]);
});

test("card presentation supports optional text/colors and aggregate variants", async () => {
    const f = fixture({ inventory_guard_show_badges: true, inventory_guard_display_mode: "quantity" });
    currentPos = f.store;
    await f.store.refreshInventoryGuard();
    const card = new Card();
    card.props = { product: { product_variant_ids: [f.product] } };
    card.setup();
    assert.equal(card.inventoryGuardBadge.colorsOnly, false);
    assert.equal(card.inventoryGuardBadge.label, "Available: 2");
    f.config.inventory_guard_display_mode = "color";
    assert.equal(card.inventoryGuardBadge.colorsOnly, true);
    runtime(f.config).products[2] = { tracked: true, available: 3 };
    card.props.product.product_variant_ids.push({ id: 2 });
    assert.equal(card.inventoryGuardBadge.label, "Variants — Available: 5");
    runtime(f.config).failed = true;
    assert.equal(card.inventoryGuardBadge.stale, true);
    f.config.inventory_guard_show_badges = false;
    assert.equal(card.inventoryGuardBadge, null);
});

test("order indicator and shortage summary use total positive demand", async () => {
    const f = fixture({ inventory_guard_show_order: true }, 0);
    currentPos = f.store;
    f.store.getOrder = () => f.order;
    await f.store.refreshInventoryGuard();
    const component = new OrderlineComponent();
    component.props = { line: f.line, mode: "display" };
    assert.equal(component.inventoryGuardIndicator.css, "text-bg-danger");
    assert.equal(component.lineContainerClasses.o_inventory_guard_shortage, true);
    assert.equal(component.lineContainerClasses.selected, true);
    const screen = new Screen();
    screen.pos = f.store;
    assert.equal(screen.inventoryGuardShortages, 1);
    f.line.qty = -1;
    assert.equal(screen.inventoryGuardShortages, 0);
    component.props.mode = "receipt";
    assert.equal(component.inventoryGuardIndicator, null);
});

test("custom polling interval is scheduled after refresh and cleared on unmount", async () => {
    const f = fixture({ inventory_guard_auto_refresh: true, inventory_guard_refresh_seconds: 45 });
    currentPos = f.store;
    mounted.length = 0;
    unmounted.length = 0;
    const timers = [];
    const cleared = [];
    context.setTimeout = (callback, delay) => { timers.push({ callback, delay }); return 123; };
    context.clearTimeout = id => cleared.push(id);
    try {
        const screen = new Screen();
        screen.setup();
        mounted[0]();
        await new Promise(resolve => setImmediate(resolve));
        assert.equal(timers.length, 1);
        assert.equal(timers[0].delay, 45000);
        unmounted[0]();
        assert.deepEqual(cleared, [123]);
        await timers[0].callback();
        assert.equal(timers.length, 1);
    } finally {
        context.setTimeout = setTimeout;
        context.clearTimeout = clearTimeout;
    }
});
