/** @odoo-module */

import { patch } from "@web/core/utils/patch";
import { TicketScreen } from "@point_of_sale/app/screens/ticket_screen/ticket_screen";
import { usePos } from "@point_of_sale/app/store/pos_hook";
import { useService } from "@web/core/utils/hooks";
import { ErrorPopup } from "@point_of_sale/app/errors/popups/error_popup";
import { Order, Orderline, Payment } from "@point_of_sale/app/store/models";
import { ConfirmPopup } from "@point_of_sale/app/utils/confirm_popup/confirm_popup";
import { OfflineErrorPopup } from "@point_of_sale/app/errors/popups/offline_error_popup";
import { _t } from "@web/core/l10n/translation";

patch(TicketScreen.prototype, {
  setup() {
    super.setup();
  },
  _getOrderStates() {
    const states = new Map();
    states.set("ACTIVE_ORDERS", {
      text: _t("All active orders"),
    });
    states.set("ONGOING", {
      text: _t("Ongoing"),
      indented: true,
    });
    states.set("PAYMENT", {
      text: _t("Payment"),
      indented: true,
    });
    states.set("RECEIPT", {
      text: _t("Receipt"),
      indented: true,
    });
    states.set("BIRECEIPT", {
      text: _t("Session Receipt"),
      indented: true,
    });
    return states;
  },
  _getScreenToStatusMap() {
    return {
      ProductScreen: "ONGOING",
      PaymentScreen: "PAYMENT",
      ReceiptScreen: "RECEIPT",
      BiReceiptScreen: "BIRECEIPT",
    };
  },
});
