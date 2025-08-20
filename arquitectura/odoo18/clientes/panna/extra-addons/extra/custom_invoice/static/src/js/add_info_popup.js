import { Dialog } from "@web/core/dialog/dialog";
import { usePos } from "@point_of_sale/app/store/pos_hook";
import { Component, useState } from "@odoo/owl";

export class CDFIDetailPopupWidget extends Component {
  static template = "custom_invoice.CDFIDetailPopupWidget";
  static components = { Dialog };
  static props = {
    order: Object,
    getPayload: Function,
    close: Function,
    newPartner: { optional: true },
  };

  setup() {
    this.pos = usePos();
    const order = this.props.order;
    const partner = order.get_partner() || this.props.newPartner;
    this.state = useState({
      uso_cfdi: "G03",
    });
  }
  confirm() {
    this.props.getPayload(this.state);
    this.props.close();
  }
}
