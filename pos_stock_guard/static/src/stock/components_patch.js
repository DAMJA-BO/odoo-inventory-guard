// SPDX-License-Identifier: Apache-2.0
import { onMounted, onWillUnmount } from "@odoo/owl";
import { patch } from "@web/core/utils/patch";
import { _t } from "@web/core/l10n/translation";
import { usePos } from "@point_of_sale/app/hooks/pos_hook";
import { ProductCard } from "@point_of_sale/app/components/product_card/product_card";
import { Orderline } from "@point_of_sale/app/components/orderline/orderline";
import { ProductScreen } from "@point_of_sale/app/screens/product_screen/product_screen";
import { stockRuntime, cardStock, needsStock } from "./runtime";
import { availabilityStatus, positiveDemand, exceedsAvailable } from "./policy";

const statusClasses = {
    unknown: "text-bg-secondary", empty: "text-bg-danger",
    low: "text-bg-warning", available: "text-bg-success",
};

function label(stock, config) {
    const status = availabilityStatus(stock, config);
    if (status === "unknown") return _t("Stock unknown");
    if (status === "untracked") return "";
    const quantity = String(stock.available);
    const message = status === "empty" ? _t("Out of stock") :
        status === "low" ? _t("Low stock: %s", quantity) : _t("Available: %s", quantity);
    return stock.variants ? _t("Variants — %s", message) : message;
}

patch(ProductCard.prototype, {
    setup(...args) {
        super.setup?.(...args);
        this.stockGuardPos = usePos();
    },
    get stockGuardBadge() {
        const config = this.stockGuardPos.config;
        if (!config.stock_guard_show_badges) return null;
        const state = stockRuntime(config);
        const stock = cardStock(this.props.product, state);
        if (stock && !stock.tracked) return null;
        const status = availabilityStatus(stock, config);
        return {
            label: label(stock, config),
            css: statusClasses[status],
            colorsOnly: config.stock_guard_display_mode === "color",
            stale: state.failed,
        };
    },
});

patch(Orderline.prototype, {
    get stockGuardIndicator() {
        const config = this.line.config;
        if (this.props.mode !== "display" || !config.stock_guard_show_order) return null;
        const state = stockRuntime(config);
        const stock = state.products[this.line.product_id.id];
        if (stock && !stock.tracked) return null;
        const requested = positiveDemand(this.line.order_id.lines, this.line.product_id.id);
        const shortage = stock && requested > 0 && exceedsAvailable(requested, stock);
        return {
            label: shortage
                ? _t("Requested: %s · Available: %s", requested, stock.available)
                : label(stock, config),
            css: shortage ? "text-bg-danger" : statusClasses[availabilityStatus(stock, config)],
            colorsOnly: config.stock_guard_display_mode === "color",
            stale: state.failed,
        };
    },
    get lineContainerClasses() {
        return {
            ...super.lineContainerClasses,
            "o_stock_guard_shortage": this.stockGuardIndicator?.css === "text-bg-danger",
        };
    },
});

patch(ProductScreen.prototype, {
    setup(...args) {
        super.setup(...args);
        let timer;
        let disposed = false;
        const refresh = async () => {
            await this.pos.refreshStockGuard();
            if (!disposed && this.pos.config.stock_guard_auto_refresh) {
                timer = setTimeout(refresh, this.pos.config.stock_guard_refresh_seconds * 1000);
            }
        };
        onMounted(() => {
            if (needsStock(this.pos.config)) void refresh();
        });
        onWillUnmount(() => {
            disposed = true;
            clearTimeout(timer);
        });
    },
    get stockGuardState() {
        return stockRuntime(this.pos.config);
    },
    get stockGuardVisible() {
        return needsStock(this.pos.config);
    },
    get stockGuardShortages() {
        if (!this.pos.config.stock_guard_show_order) return 0;
        const state = this.stockGuardState;
        const products = new Set(this.currentOrder?.lines.filter((line) => line.qty > 0)
            .map((line) => line.product_id.id));
        return [...products].filter((id) => exceedsAvailable(
            positiveDemand(this.currentOrder.lines, id), state.products[id])).length;
    },
    toggleStockGuardFilter() {
        this.stockGuardState.onlyAvailable = !this.stockGuardState.onlyAvailable;
    },
});
