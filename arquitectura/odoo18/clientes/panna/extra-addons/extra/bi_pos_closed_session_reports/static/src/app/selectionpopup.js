import { Component, useState, xml, useRef } from "@odoo/owl";
import { usePos } from "@point_of_sale/app/store/pos_hook";
import { useService } from "@web/core/utils/hooks";
import { Dialog } from "@web/core/dialog/dialog";
import { Orderline } from "@point_of_sale/app/generic_components/orderline/orderline";

// IMPROVEMENT: This code is very similar to TextInputPopup.
//      Combining them would reduce the code.
export class SelectionSession extends Component {
  static template = "bi_pos_closed_session_reports.SelectionSession";
  static components = {
    Dialog,
  };
  static props = ["close", "sessions"];

  setup() {
    super.setup();

    this.pos = usePos();
    this.state = useState({ SelectedSession: "" });
    this.inputRef = useRef("input");
    this.dialog = useService("dialog");
    this.report = useService("report");
  }

  get pos_sessions() {
    let sessions = this.props.sessions;
    let pos_sessions = [];
    sessions.forEach((session) => {
      if (session) {
        pos_sessions.push(session);
      }
    });
    return pos_sessions;
  }

  cancel() {
    this.props.close();
  }

  async confirm_session() {
    var select_session = this.state.SelectedSession; //$('.select_session_id').val();
    console.log("confirm session called", select_session);
    if (!select_session) {
      alert("Please Select Session");
    } else {
      await this.report.doAction(
        "bi_pos_closed_session_reports.action_report_session_z",

        [select_session],
      );
      this.props.close();
    }
  }
}
