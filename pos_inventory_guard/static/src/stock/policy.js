// SPDX-License-Identifier: Apache-2.0
/** Pure stock calculations shared by the POS UI and dependency-free tests. */
export function positiveDemand(lines, productId, excludedLine) {
    return lines.reduce((total, line) =>
        line !== excludedLine && line.product_id?.id === productId
            ? total + Math.max(0, line.qty) : total, 0);
}

export function exceedsAvailable(quantity, stock) {
    if (!stock?.tracked) {
        return false;
    }
    const step = stock.rounding || 0.000001;
    const rounded = (value) =>
        Math.sign(value) * Math.round((Math.abs(value) + Number.EPSILON) / step);
    return rounded(quantity) > rounded(stock.available);
}

export function availabilityStatus(stock, config) {
    if (!stock) return "unknown";
    if (!stock.tracked) return "untracked";
    if (stock.available <= 0) return "empty";
    if (config.inventory_guard_low_stock &&
        stock.available <= config.inventory_guard_low_threshold) return "low";
    return "available";
}
