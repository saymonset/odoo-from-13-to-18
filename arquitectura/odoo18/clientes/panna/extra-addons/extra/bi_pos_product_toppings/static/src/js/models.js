/** @odoo-module */

import { PosStore } from "@point_of_sale/app/store/pos_store";
import { patch } from "@web/core/utils/patch";
import { PosOrder } from "@point_of_sale/app/models/pos_order";
import { PosOrderline } from "@point_of_sale/app/models/pos_order_line";
import { Orderline } from "@point_of_sale/app/generic_components/orderline/orderline";

patch(PosStore.prototype, {
  // @Override
  // async _processData(loadedData) {
  //     await super._processData(loadedData);
  //     let self = this;
  // 	self.prod_toppings = loadedData['topping.groups'] || [];
  // 	self.toppings_by_id = loadedData['toppings_by_id'] || [];
  // 	self.topping_group_by_id = loadedData['topping_group_by_id'] || [];
  // },

  async addLineToCurrentOrder(vals, opts = {}, configure = true) {
    await super.addLineToCurrentOrder(vals, opts, configure);
    if (this.config.activate_toppings && this.config.add_topping_default) {
      this.get_order()._addDefaultToppings();
    }
  },
});

patch(PosOrder.prototype, {
  setup() {
    super.setup(...arguments);
  },

  add_product(product, options) {
    super.add_product(...arguments);
  },

  deleteLine(ev) {
    let orderline = this.get_selected_orderline();
    if (orderline) {
      let toppings = orderline.get_line_topping_ids();

      let prod_list = [];
      let prod_dict = {};
      let t_total = 0;
      toppings.forEach(function (prod) {
        if (prod.id != ev.id) {
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
        }
      });

      prod_list = Object.values(prod_dict);
      orderline.set_top_data(prod_list);
      let y = toppings.filter(function (value) {
        return value.id !== ev.id;
      });
      // orderline.set_top_data(lst);
      orderline.set_line_topping_ids(y);
      let details = orderline.getToppingDetails();
      let ltotal = ev.total;
      orderline.price_type = "manual";
      orderline.set_unit_price(orderline.price_unit - ltotal);
      orderline.price_manually_set = true;
    } else {
      alert("Please Select orderline first!!");
    }
  },

  _addDefaultToppings() {
    if (this.config.activate_toppings && this.config.add_topping_default) {
      let orderline = this.get_selected_orderline();
      let prod = orderline.product_id;
      let old_rate = orderline.price_unit;

      let arr = prod.topping_ids;
      let aa = arr.filter((item, index) => arr.indexOf(item) === index);
      let prod_list = [];
      let prod_dict = {};
      let t_total = 0;
      arr.forEach(function (prod) {
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
      orderline.set_top_data(prod_list);

      orderline.set_line_topping_ids(aa);
      let details = orderline.getToppingDetails();
      let total_arr = details.map((item) => item.total);
      let sum = total_arr.reduce((a, b) => a + b, 0) + old_rate;
      // orderline.set_unit_price(sum);
      orderline.price_type = "manual";
      orderline.set_unit_price(sum);
      orderline.price_manually_set = true;
    }
  },
});

patch(PosOrderline.prototype, {
  setup() {
    super.setup(...arguments);
    this.line_toppings = this.line_toppings || [];
    this.line_topping_ids = this.line_topping_ids || [];
    this.toppings_total = this.toppings_total || 0;
    this.top_data = this.get_top_data() || [];
    this.toppingdata = this.toppingdata || [];
  },

  getDisplayData() {
    let obj;
    if (typeof this.get_top_data() == "string") {
      obj = JSON.parse(this.get_top_data());
    } else {
      obj = JSON.parse(JSON.stringify(this.get_top_data()));
    }
    return {
      ...super.getDisplayData(),
      toppingsData: obj,
      // line_topping_ids: this.get_line_topping_ids() || [],
      // top_data: this.get_top_data() || [],
    };
  },

  set_top_data(top_data) {
    this.top_data = top_data;
  },

  get_top_data() {
    return this.top_data;
  },

  set_line_toppings(line_toppings) {
    this.line_toppings = line_toppings;
  },

  clone() {
    const orderline = super.clone(...arguments);
    orderline.line_topping_ids = this.line_topping_ids || [];
    return orderline;
  },
  get_line_toppings() {
    return this.line_toppings;
  },

  set_line_topping_ids(line_topping_ids) {
    this.line_topping_ids = line_topping_ids;
  },

  get_line_topping_ids() {
    return this.line_topping_ids;
  },

  set_toppings_total(toppings_total) {
    this.toppings_total = toppings_total;
  },

  get_toppings_total() {
    return this.toppings_total;
  },

  export_for_printing() {
    const json = super.export_for_printing(...arguments);
    json.toppingdata = this.toppingdata || [];
    json.line_topping_ids = this.line_topping_ids || [];
    json.toppings_total = this.toppings_total || 0;
    return json;
  },

  deleteLine(ev) {
    let order = this.get_order();
    let orderline = this.props.line;
    let toppings = orderline.get_line_topping_ids();
    let y = jQuery.grep(toppings, function (value) {
      return value != ev.detail.id;
    });
    orderline.set_line_topping_ids(y);
    let details = orderline.getToppingDetails();
    let ltotal = ev.detail.total;
    orderline.price_type = "manual";
    orderline.set_unit_price(orderline.price - ltotal);
    orderline.price_manually_set = true;
  },

  get_toppingsData() {
    // let order = this.order_id;
    let line = this;
    let data = line.getToppingDetails();
    return data;
  },

  getToppingDetails() {
    let self = this;
    let topping_ids = this.line_topping_ids;
    let prod_list = [];
    let prod_dict = {};
    let t_total = 0;
    topping_ids.forEach(function (prod) {
      let product = prod;
      if (product) {
        t_total += product.lst_price;
        if (prod in prod_dict) {
          let old_qty = prod_dict[prod]["qty"] + 1;

          prod_dict[prod] = {
            id: product.id,
            name: product.display_name,
            // 'uom' : product.uom_id.id,
            qty: old_qty,
            rate: product.lst_price,
            total: product.lst_price * old_qty,
          };
        } else {
          prod_dict[prod] = {
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
    self.set_toppings_total(t_total);
    prod_list = Object.keys(prod_dict).map((key) => prod_dict[key]);

    // prod_list = $.map(prod_dict, function(value, key) { return value });
    this.toppingdata = prod_list;
    return prod_list;
  },
});

patch(Orderline, {
  props: {
    ...Orderline.props,
    line: {
      ...Orderline.props.line,
      shape: {
        ...Orderline.props.line.shape,
        toppingsData: { type: [Object, String], optional: true },
        // line_topping_ids: { type: Array, optional: true },
        // top_data: { type: [Array,String], optional: true },
      },
    },
  },
});
