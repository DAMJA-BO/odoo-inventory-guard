// SPDX-License-Identifier: Apache-2.0
import { patch } from "@web/core/utils/patch";
import { _t } from "@web/core/l10n/translation";
import { parseFloat } from "@web/views/fields/parsers";
import { PosOrderline } from "@point_of_sale/app/models/pos_order_line";
import { stockRuntime } from "./runtime";
import { exceedsAvailable } from "./policy";

patch(PosOrderline.prototype, {
    setQuantity(quantity, ...args) {
        const config = this.config;
        const state = stockRuntime(config);
        const requested = typeof quantity === "number" ? quantity : parseFloat(String(quantity || 0));
        // Reductions, returns, finalized records and internal merges remain valid.
        if (config.stock_guard_limit_quantity && !state.merging &&
            this.order_id?.state === "draft" && !this.order_id.preset_id?.is_return &&
            requested > Math.max(0, this.qty)) {
            // Validate combo children before changing the parent to avoid a
            // partially updated bundle when a child's quantity is rejected.
            const changes = new Map();
            const collect = (line, qty) => {
                changes.set(line, qty);
                for (const child of line.combo_line_ids || []) {
                    collect(child, (child.qty / line.qty || 1) * qty);
                }
            };
            collect(this, requested);
            const totals = new Map();
            for (const line of this.order_id.lines) {
                const qty = changes.has(line) ? changes.get(line) : line.qty;
                const id = line.product_id.id;
                totals.set(id, (totals.get(id) || 0) + Math.max(0, qty));
            }
            for (const line of changes.keys()) {
                const stock = state.products[line.product_id.id];
                const total = totals.get(line.product_id.id);
                if (!stock || state.failed || exceedsAvailable(total, stock)) {
                    return {
                        title: _t("Stock Guard"),
                        body: !stock || state.failed
                            ? _t("Availability is unknown. Refresh stock before increasing the quantity.")
                            : _t("%s: requested %s; available %s",
                                line.product_id.display_name, total, stock.available),
                    };
                }
            }
        }
        return super.setQuantity(quantity, ...args);
    },
});
