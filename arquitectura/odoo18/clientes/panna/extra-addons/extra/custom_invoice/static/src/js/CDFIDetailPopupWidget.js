import { InvoiceButton } from "@point_of_sale/app/screens/ticket_screen/invoice_button/invoice_button";
import { CDFIDetailPopupWidget } from "@custom_invoice/js/add_info_popup";
import { makeAwaitable } from "@point_of_sale/app/store/make_awaitable_dialog";
import { patch } from "@web/core/utils/patch";

patch(InvoiceButton.prototype, {
  async onWillInvoiceOrder(order, newPartner) {
    if (this.pos.company.country_id?.code !== "MX") {
      return true;
    }
    const payload = await makeAwaitable(this.dialog, CDFIDetailPopupWidget, {
      order,
      newPartner,
    });
    if (payload) {
      order.uso_cfdi = payload.uso_cfdi;
      await this.pos.data.ormWrite("pos.order", [order.id], {
        uso_cfdi: order.uso_cfdi,
      });
    }
    return Boolean(payload);
  },
});
