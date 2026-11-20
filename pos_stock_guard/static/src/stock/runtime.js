// SPDX-License-Identifier: Apache-2.0
import { proxy } from "@odoo/owl";

/** Session-only reactive snapshots. Never serialized into POS business records. */
const runtimes = new Map();
export function stockRuntime(config) {
    if (!runtimes.has(config.id)) {
        runtimes.set(config.id, proxy({
            products: {}, lastUpdated: "", location: "", failed: false,
            loading: false, onlyAvailable: false,
        }));
    }
    return runtimes.get(config.id);
}

export function needsStock(config) {
    return Boolean(config.stock_guard_show_badges || config.stock_guard_show_order ||
        config.stock_guard_block_add || config.stock_guard_limit_quantity ||
        config.stock_guard_available_filter || config.stock_guard_auto_refresh);
}

/** Cards represent templates; validation always checks the selected variant. */
export function cardStock(product, runtime) {
    const variants = product.product_tmpl_id ? [product] : product.product_variant_ids;
    if (!variants?.length) return undefined;
    const stocks = variants.map((variant) => runtime.products[variant.id]);
    if (stocks.some((stock) => !stock)) return undefined;
    if (stocks.every((stock) => !stock.tracked)) return { tracked: false, available: 0 };
    return {
        tracked: true,
        available: stocks.reduce((sum, stock) => sum + Math.max(0, stock.available), 0),
        variants: variants.length > 1,
    };
}
