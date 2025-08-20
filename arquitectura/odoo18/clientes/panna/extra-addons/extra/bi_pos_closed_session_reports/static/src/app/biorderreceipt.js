/** @odoo-module **/

import { _t } from "@web/core/l10n/translation";
import { registry } from "@web/core/registry";
import { useState, onWillStart, Component } from "@odoo/owl";
import { usePos } from "@point_of_sale/app/store/pos_hook";
import { useService } from "@web/core/utils/hooks";

export class BiOrderReceipt extends Component {
  static template = "bi_pos_closed_session_reports.BiOrderReceipt";

  setup() {
    this.pos = usePos();
    this.session_id = this.pos.get_order().session_id.id;
    this.orm = useService("orm");
    this.my_method();

    this.current_datetime();
    this.get_pricelist();
    this.get_payment_data();
    this.state = useState({
      session_data: [],
      current_datetime: "",
      pricelist: "",
      pricelist_qty: "",
      payment_data: "",
    });
  }

  async my_method() {
    var self = this;
    var data = await this.env.services.orm
      .call("pos.session", "pos_side_get_session_amount_data", [
        [],
        this.session_id,
      ])
      .then(async function (output) {
        console.log("\n\n oooooooooooo", output);
        if (output) {
          if (self.state.session_data.length == 0) {
            self.state.session_data.push(output);
            return self.state.session_data;
          }
        }
      });
  }
  async get_pricelist() {
    var self = this;
    var data1 = await this.env.services.orm
      .call("pos.session", "pos_side_get_pricelist", [[], this.session_id])
      .then(async function (output) {
        if (output) {
          if (self.state.pricelist.length == "") {
            self.state.pricelist = output;
            return self.state.pricelist;
          }
        }
      });
  }

  async current_datetime() {
    var self = this;
    var data1 = await this.env.services.orm
      .call("pos.session", "get_current_datetime", [[]])
      .then(async function (output) {
        if (output) {
          if (self.state.current_datetime == "") {
            self.state.current_datetime = output;
            return self.state.current_datetime;
          }
        }
      });
  }

  async get_payment_data() {
    var self = this;
    var data3 = await this.env.services.orm
      .call("pos.session", "pos_side_get_payment_data", [[], this.session_id])
      .then(async function (output) {
        if (output) {
          if (self.state.payment_data.length == "") {
            self.state.payment_data = output;
            return self.state.payment_data;
          }
        }
      });
  }
}

// registry.category("pos_screens").add("BiOrderReceipt", BiOrderReceipt);
