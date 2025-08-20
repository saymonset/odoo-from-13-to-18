/** @odoo-module */

import { patch } from "@web/core/utils/patch";
import { ControlButtons } from "@point_of_sale/app/screens/product_screen/control_buttons/control_buttons";
import { SelectCreateDialog } from "@web/views/view_dialogs/select_create_dialog";
import { ToppingPopup } from "@bi_pos_product_toppings/js/ToppingPopup";
import { AlertDialog } from "@web/core/confirmation_dialog/confirmation_dialog";
import { _t } from "@web/core/l10n/translation";

patch(ControlButtons.prototype, {
  clickToppings() {
    let self = this;
    var order = this.pos.get_order();
    var orderlines = order.get_orderlines();
    if (orderlines.length === 0) {
      this.pos.dialog.add(AlertDialog, {
        title: _t("Empty Order"),
        body: _t(
          "There must be at least one product in your order before applying order type.",
        ),
      });
      return;
    } else {
      var prod_list = [];

      let selected_orderline = order.get_selected_orderline();
      if (
        selected_orderline &&
        selected_orderline.product_id &&
        selected_orderline.product_id.topping_ids.length > 0
      ) {
        let arr = selected_orderline.product_id.topping_ids;
        // let aa = arr.filter((item,index) => arr.indexOf(item) === index);
        arr.forEach(function (prod) {
          var top_prod = self.pos.models["product.product"].getBy(
            "id",
            prod.id,
          );
          if (top_prod) {
            prod_list.push(top_prod);
          }
        });
      }

      this.pos.dialog.add(ToppingPopup, { toppings: prod_list });
    }
  },
});
