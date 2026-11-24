// SPDX-License-Identifier: Apache-2.0
import { patch } from "@web/core/utils/patch";
import { _t } from "@web/core/l10n/translation";
import { AlertDialog } from "@web/core/confirmation_dialog/confirmation_dialog";
import { PosStore } from "@point_of_sale/app/services/pos_store";
import { stockRuntime, needsStock, cardStock } from "./runtime";
import { positiveDemand, exceedsAvailable } from "./policy";

patch(PosStore.prototype, {
    async refreshInventoryGuard(productIds) {
        if (!needsStock(this.config)) return true;
        const state = stockRuntime(this.config);
        const ids = [...new Set(productIds ||
            this.models["product.product"].getAll().map((product) => product.id))]
            .filter((id) => Number.isInteger(id) && id > 0);
        const request = async () => {
            state.loading = true;
            const updates = {};
            let location = state.location;
            try {
                for (let offset = 0; offset < ids.length; offset += 200) {
                    const result = await this.data.call("pos.config", "get_inventory_guard_availability",
                        [this.config.id, ids.slice(offset, offset + 200)]);
                    Object.assign(updates, result.products);
                    location = result.location;
                }
                state.products = { ...state.products, ...updates };
                state.location = location;
                // A targeted add check must not claim the whole catalog is fresh.
                if (!productIds) {
                    state.lastUpdated = new Date().toLocaleTimeString();
                    state.failed = false;
                }
                return true;
            } catch (error) {
                // Fail closed, but leave a trace for support instead of hiding the cause.
                console.error("Inventory Guard: stock refresh failed", error);
                state.failed = true;
                return false;
            } finally {
                state.loading = false;
            }
        };
        const pending = (this._inventoryGuardRequest || Promise.resolve()).then(request);
        this._inventoryGuardRequest = pending;
        try {
            return await pending;
        } finally {
            if (this._inventoryGuardRequest === pending) this._inventoryGuardRequest = null;
        }
    },

    async loadNewProducts(...args) {
        const result = await super.loadNewProducts(...args);
        await this.refreshInventoryGuard();
        return result;
    },

    filterExcludedProducts(products) {
        const state = stockRuntime(this.config);
        // Filter before Odoo's 100-card limit, including category-grouped catalogs.
        const candidates = this.config.inventory_guard_available_filter && state.onlyAvailable
            ? Array.from(products).filter((product) => {
                const stock = cardStock(product, state);
                // Unknown quantities must not silently hide products.
                return !stock || !stock.tracked || stock.available > 0;
            }) : products;
        return super.filterExcludedProducts(candidates);
    },

    async handleOrderLineConfiguration(order, values, ...args) {
        const result = await super.handleOrderLineConfiguration(order, values, ...args);
        if (result === false || (!this.config.inventory_guard_block_add &&
            !this.config.inventory_guard_limit_quantity)) return result;
        // Odoo applies barcode quantities in setOptions after this hook.
        // Resolve them now so a weighed/package scan cannot bypass the early check.
        const code = args[0];
        let quantity = values.qty;
        if (code && ["weight", "quantity", "discount"].includes(code.type)) {
            quantity = code.value;
        }
        const packaging = code && this.models["product.uom"].getBy("barcode", code.code);
        if (packaging) {
            quantity = packaging.uom_id.factor / values.product_id.uom_id.factor;
        }
        if (order.preset_id?.is_return) {
            quantity = -Math.abs(quantity);
        }
        const demands = [{ product: values.product_id, qty: quantity }];
        for (const command of values.combo_line_ids || []) {
            if (command[0] === "create") {
                demands.push({ product: command[1].product_id, qty: command[1].qty });
            }
        }
        const ids = demands.map(({ product }) => product?.id).filter(Boolean);
        if (!await this.refreshInventoryGuard(ids)) {
            this.dialog.add(AlertDialog, {
                title: _t("Stock verification unavailable"),
                body: _t("Connect to the server before adding this product."),
            });
            return false;
        }
        const state = stockRuntime(this.config);
        const additional = {};
        for (const { product, qty } of demands) {
            if (!product || qty <= 0) continue;
            const stock = state.products[product.id];
            if (!stock) {
                this.dialog.add(AlertDialog, {
                    title: _t("Inventory Guard"),
                    body: _t("Availability is unknown. Refresh stock and try again."),
                });
                return false;
            }
            additional[product.id] = (additional[product.id] || 0) + qty;
            const total = positiveDemand(order.lines, product.id) + additional[product.id];
            if (stock.tracked && (
                (this.config.inventory_guard_block_add && stock.available <= 0) ||
                (this.config.inventory_guard_limit_quantity && exceedsAvailable(total, stock))
            )) {
                this.dialog.add(AlertDialog, {
                    title: _t("Inventory Guard"),
                    body: _t("%s: requested %s; available %s",
                        product.display_name || product.name, total, stock.available),
                });
                return false;
            }
        }
        return result;
    },

    tryMergeOrderline(...args) {
        // The incoming line already belongs to the order. Do not count it twice
        // while Odoo merges it; the complete demand was checked before creation.
        const state = stockRuntime(this.config);
        state.merging = true;
        try {
            return super.tryMergeOrderline(...args);
        } finally {
            state.merging = false;
        }
    },
});
