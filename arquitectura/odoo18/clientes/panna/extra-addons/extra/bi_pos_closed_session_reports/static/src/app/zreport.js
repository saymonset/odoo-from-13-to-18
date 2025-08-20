import { patch } from "@web/core/utils/patch";
import { ControlButtons } from "@point_of_sale/app/screens/product_screen/control_buttons/control_buttons";
import { usePos } from "@point_of_sale/app/store/pos_hook";
import { useService } from "@web/core/utils/hooks";
import { SelectionSession } from "@bi_pos_closed_session_reports/app/selectionpopup";
import { SelectionReportType } from "@bi_pos_closed_session_reports/app/sessionreportpopup";

patch(ControlButtons.prototype, {
  setup() {
    super.setup();
    this.pos = usePos();
    this.report = useService("report");
  },

  async clickPostedSessionReport() {
    var self = this;
    let sessions = await this.env.services.orm.call(
      "pos.session",
      "search_read",
      [[]],
    );
    this.env.services.pos.sessions_list = sessions;
    // if(this.env.services.pos.config.z_report_selection == 'both'){
    this.dialog.add(SelectionSession, { sessions: sessions });
  },

  async clickPrintSessionReport() {
    let sessions = await this.env.services.orm.call(
      "pos.session",
      "search_read",
      [[]],
    );
    this.env.services.pos.sessions_list = sessions;
    if (this.env.services.pos.config.z_report_selection == "both") {
      this.dialog.add(SelectionReportType, {});
    } else if (this.pos.config.z_report_selection == "pdf") {
      await this.report.doAction(
        "bi_pos_closed_session_reports.action_report_session_z",

        [this.pos.session.id],
      );
    } else if (this.env.services.pos.config.z_report_selection == "receipt") {
      this.pos.showScreen("bireceipt");
    }
  },
});
