/** @odoo-module */

import { _t } from "@web/core/l10n/translation";
import { useService } from "@web/core/utils/hooks";
import { onMounted, Component } from "@odoo/owl";
import { usePos } from "@point_of_sale/app/store/pos_hook";
import { Dialog } from "@web/core/dialog/dialog";

export class ToppingPopup extends Component {
  static template = "bi_pos_product_toppings.ToppingPopup";
  static props = {
    close: Function,
    toppings: Array,
  };
  static components = { Dialog };
  setup() {
    super.setup();
    this.pos = usePos();
  }

  get imageUrl() {
    const product = this.product;
    return `/web/image?model=product.product&field=image_128&id=${product.id}&write_date=${product.write_date}&unique=1`;
  }
  get pricelist() {
    const current_order = this.pos.get_order();
    if (current_order) {
      return current_order.pricelist;
    }
    return this.pos.default_pricelist;
  }
  get price() {
    const formattedUnitPrice = this.env.utils.formatCurrency(
      this.product.get_price(this.pricelist, 1),
      "Product Price",
    );
    if (this.product.to_weight) {
      return `${formattedUnitPrice}/${
        this.pos.units_by_id[this.product.uom_id[0]].name
      }`;
    } else {
      return formattedUnitPrice;
    }
  }
  get toppingProducts() {
    return this.props.toppings;
  }

  add_product_toppings(ev) {
    let product = ev;
    let order = this.pos.get_order();
    let orderline = order.get_selected_orderline();
    let old_recs = orderline.get_line_topping_ids();
    old_recs.push(product);

    let prod_list = [];
    let prod_dict = {};
    let t_total = 0;
    old_recs.forEach(function (prod) {
      let product = prod;
      if (product) {
        t_total += product.lst_price;
        if (prod.id in prod_dict) {
          let old_qty = prod_dict[prod.id]["qty"] + 1;

          prod_dict[prod.id] = {
            id: product.id,
            name: product.display_name,
            // 'uom' : product.uom_id.id,
            qty: old_qty,
            rate: product.lst_price,
            total: product.lst_price * old_qty,
          };
        } else {
          prod_dict[prod.id] = {
            id: product.id,
            name: product.display_name,
            // 'uom' : product.uom_id.id,
            qty: 1,
            rate: product.lst_price,
            total: product.lst_price,
          };
        }
      }
    });

    prod_list = Object.values(prod_dict);
    orderline.set_line_topping_ids(old_recs);
    orderline.set_top_data(prod_list);
    let details = orderline.getToppingDetails();
    let total_arr = details.map((item) => item.total);
    let sum = total_arr.reduce((a, b) => a + b, 0);
    orderline.price_type = "manual";
    orderline.set_unit_price(orderline.price_unit + product.lst_price);
    orderline.price_manually_set = true;
  }
}
