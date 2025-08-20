/** @odoo-module */

import { patch } from "@web/core/utils/patch";
import { ReceiptScreen } from "@point_of_sale/app/screens/receipt_screen/receipt_screen";
import { usePos } from "@point_of_sale/app/store/pos_hook";
import { useService } from "@web/core/utils/hooks";
import { useRef, useState, onWillStart, Component } from "@odoo/owl";
import { _t } from "@web/core/l10n/translation";
import { registry } from "@web/core/registry";
import { BiOrderReceipt } from "@bi_pos_closed_session_reports/app/biorderreceipt";

class bireceipt extends ReceiptScreen {
  static template = "bi_pos_closed_session_reports.bireceipt";
  static components = { BiOrderReceipt };
  setup() {
    super.setup();
    this.session_id = this.pos.get_order().pos_session_id;
    this.biorderReceipt = useRef("order-receipt");
    this.orm = useService("orm");
    this.printer = useService("printer");
    this.pos = usePos();
  }
  async onSendEmailToCustomer() {
    var session_id = this.pos.get_order().pos_session_id;
    var input_email = document.getElementById("email").value;
    var mail_format = /^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$/;
    if (input_email.match(mail_format)) {
      await this.env.services.orm.call(
        "pos.session",
        "send_session_receipt_email",
        ["", input_email, session_id],
      );
      document.getElementById("email").value = "";
    } else {
      alert("You have entered an invalid email address!");
    }
  }

  get nextScreen() {
    return { name: "ProductScreen" };
  }
  orderDone() {
    this.pos.removeOrder(this.currentOrder);
    this._addNewOrder();
    const { name, props } = this.nextScreen;
    this.pos.showScreen(name, props);
  }

  // orderDone() {
  //     this.trigger('close-temp-screen');
  //     const { name, props } = this.nextScreen;
  //     this.showScreen(name, props);
  // }

  async printReceipt() {
    const currentOrder = this.currentOrder;
    const isPrinted = await this.printer.print(
      BiOrderReceipt,
      {
        data: this.pos.get_order().export_for_printing(),
        formatCurrency: this.env.utils.formatCurrency,
        order: this.get_receipt_data(),
      },
      { webPrintFallback: true },
    );
    // if (isPrinted) {
    //     this.currentOrder._printed = true;
    // }
  }

  get_receipt_data() {
    return {
      widget: this,
      pos: this.pos,
      date: new Date().toLocaleString(),
    };
  }
}
registry.category("pos_screens").add("bireceipt", bireceipt);
