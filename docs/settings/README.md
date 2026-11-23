# Stock Guard settings

Each POS has independent settings. Select the POS in its settings before editing.
All switches default to off. The display mode defaults to quantity/text/colors,
the low-stock threshold to 3, and the refresh interval to 30 seconds. An upgrade
preserves the saved final-checkout protection value.

Start with the [configuration guide](../CONFIGURATION.md), then read each setting:

| Setting | Guide | Role |
| --- | --- | --- |
| Block sales with insufficient stock | [Details](block-insufficient-stock.md) | Final checkout protection |
| Show stock badges | [Details](show-stock-badges.md) | Presentation or advisory data |
| Stock display mode | [Details](stock-display-mode.md) | Presentation or advisory data |
| Block adding out-of-stock products | [Details](block-out-of-stock-products.md) | Early prevention |
| Prevent quantities above available stock | [Details](limit-quantity-to-available-stock.md) | Early prevention |
| Show stock on order lines | [Details](show-stock-on-order-lines.md) | Presentation or advisory data |
| Enable Available only filter | [Details](available-only-filter.md) | Presentation or advisory data |
| Highlight low stock | [Details](low-stock-warning.md) | Presentation or advisory data |
| Automatically refresh stock | [Details](automatic-stock-refresh.md) | Presentation or advisory data |

## Setting relationships

| Combination | Expected interaction |
| --- | --- |
| Badges + display mode | Mode controls badge text or color presentation. |
| Order indicators + display mode | Same mode applies to order indicators. |
| Low stock + badges/order indicators | Threshold changes their warning state; low stock alone has no visible output. |
| Block adding + quantity limit | Zero-stock selection and excessive positive quantities are checked early. Quantity limits alone also reject positive demand exceeding zero availability. |
| Early checks + final protection | Early checks reduce corrections; final protection checks persisted demand again. |
| Filter + refresh | Refresh can change catalog visibility while the cashier filter is active. |
| Automatic refresh + quantity limit | Editing quantities uses the refreshed snapshot; addition uses a live check. |
| Visual features without final protection | Informative UI and optional early checks remain; authoritative addon checkout protection is disabled. |

The addon does not declare these switches mutually exclusive. Dependencies above
describe useful effects, not automatic activation: turning on one setting does not
turn on the others. Custom payment flows, alternative UoM, routes and third-party
addons require their own acceptance tests; no universal compatibility claim is made.

## Suggested starting configuration

For a POS that must prevent insufficient-stock checkout, enable final protection.
For cashier guidance, add badges, quantity/text/colors, early addition checks,
quantity limits and order indicators. Enable a low-stock warning if useful for
the products sold. Start periodic refresh at 30 seconds. Offer the filter only
if cashiers want it.

This is a starting point for testing, not a guarantee for every deployment.
Use the [acceptance checklist](../TESTING.md) before production.

