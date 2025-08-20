import { Component, useRef, useState, xml } from "@odoo/owl";
import { _t } from "@web/core/l10n/translation";
import { usePos } from "@point_of_sale/app/store/pos_hook";
import { useService } from "@web/core/utils/hooks";
import { Dialog } from "@web/core/dialog/dialog";
import { Orderline } from "@point_of_sale/app/generic_components/orderline/orderline";

// IMPROVEMENT: This code is very similar to TextInputPopup.
//      Combining them would reduce the code.
export class SelectionReportType extends Component {
  static template = "bi_pos_closed_session_reports.SelectionReportType";
  static components = {
    Dialog,
  };
  static props = ["close"];
  /**
   * @param {Object} props
   * @param {string} props.startingValue
   */
  setup() {
    super.setup();
    this.pos = usePos();
    this.state = useState({ inputValue: this.props.startingValue });
    this.report = useService("report");
  }
  cancel() {
    this.props.close();
  }

  async confirm_report_type() {
    var value_type = "";
    var ele = document.getElementsByName("type");
    for (var i = 0; i < ele.length; i++) {
      if (ele[i].checked) {
        value_type = ele[i].value;
      }
    }
    if (value_type == "pdf") {
      await this.report.doAction(
        "bi_pos_closed_session_reports.action_report_session_z",
        [this.pos.session.id],
      );
    } else if (value_type == "receipt") {
      this.pos.showScreen("bireceipt");
    }
    this.props.close();
  }
}
