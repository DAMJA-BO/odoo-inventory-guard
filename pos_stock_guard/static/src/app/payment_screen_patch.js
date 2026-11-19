// SPDX-License-Identifier: Apache-2.0
import { _t } from "@web/core/l10n/translation";
import { patch } from "@web/core/utils/patch";
import { AlertDialog } from "@web/core/confirmation_dialog/confirmation_dialog";
import { PaymentScreen } from "@point_of_sale/app/screens/payment_screen/payment_screen";

/** Advisory manual-checkout check; the server always validates persisted lines. */
patch(PaymentScreen.prototype, {
    async onClickValidate(...args) {
        if (!this.pos.config.block_negative_stock) {
            return super.onClickValidate(...args);
        }
        if (this.stockGuardPending) {
            return;
        }
        this.stockGuardPending = true;
        try {
            let result;
            try {
                result = await this.pos.data.call("pos.config", "check_pos_stock", [
                    this.pos.config.id,
                    this.currentOrder.lines.map((line) => ({
                        product_id: line.product_id.id,
                        qty: line.qty,
                    })),
                ]);
            } catch {
                this.dialog.add(AlertDialog, {
                    title: _t("Stock verification unavailable"),
                    body: _t("Connect to the server before validating this sale."),
                });
                return;
            }
            if (!result.ok) {
                this.dialog.add(AlertDialog, {
                    title: _t("Stock Guard"),
                    body: result.message,
                });
                return;
            }
            return await super.onClickValidate(...args);
        } finally {
            this.stockGuardPending = false;
        }
    },
});
