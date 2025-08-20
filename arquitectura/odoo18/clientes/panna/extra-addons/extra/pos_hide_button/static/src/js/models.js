/** @odoo-module */
import { ControlButtons } from "@point_of_sale/app/screens/product_screen/control_buttons/control_buttons";
import { user } from "@web/core/user";

import { patch } from "@web/core/utils/patch";
import { onWillStart } from "@odoo/owl";

patch(ControlButtons.prototype, {
  setup() {
    super.setup(...arguments);
    onWillStart(async () => {
      const currentUser = user.userId;
      const fetchedUser = await this.env.services.orm.read(
        "res.users",
        [currentUser],
        ["pos_hide_refund"],
      );
      if (fetchedUser && fetchedUser.length > 0) {
        this.pos_hide_refund = fetchedUser[0].pos_hide_refund;
        this.has_refund = !this.pos_hide_refund; // true jika pos_hide_refund false
      } else {
        this.has_refund = true; // Set default value
      }
      const user_general_note = await this.env.services.orm.read(
        "res.users",
        [currentUser],
        ["pos_hide_general_note"],
      );
      if (user_general_note && user_general_note.length > 0) {
        this.pos_hide_general_note = user_general_note[0].pos_hide_general_note;
        this.has_general_note = !this.pos_hide_general_note; // true jika pos_hide_refund false
      } else {
        this.has_general_note = true; // Set default value
      }
      const user_customer_note = await this.env.services.orm.read(
        "res.users",
        [currentUser],
        ["pos_hide_customer_note"],
      );
      if (user_customer_note && user_customer_note.length > 0) {
        this.pos_hide_customer_note =
          user_customer_note[0].pos_hide_customer_note;
        this.has_customer_note = !this.pos_hide_customer_note; // true jika pos_hide_refund false
      } else {
        this.has_customer_note = true; // Set default value
      }
      const user_pricelist = await this.env.services.orm.read(
        "res.users",
        [currentUser],
        ["pos_hide_pricelist"],
      );
      if (user_pricelist && user_pricelist.length > 0) {
        this.pos_hide_pricelist = user_pricelist[0].pos_hide_pricelist;
        this.has_pricelist = !this.pos_hide_pricelist; // true jika pos_hide_refund false
      } else {
        this.has_pricelist = true; // Set default value
      }
      const user_cancel = await this.env.services.orm.read(
        "res.users",
        [currentUser],
        ["pos_hide_cancel_order"],
      );
      if (user_cancel && user_cancel.length > 0) {
        this.pos_hide_cancel_order = user_cancel[0].pos_hide_cancel_order;
        this.has_cancel = !this.pos_hide_cancel_order; // true jika pos_hide_refund false
      } else {
        this.has_cancel = true; // Set default value
      }
      const user_actions = await this.env.services.orm.read(
        "res.users",
        [currentUser],
        ["pos_hide_actions"],
      );
      if (user_actions && user_actions.length > 0) {
        this.pos_hide_actions = user_actions[0].pos_hide_actions;
        this.has_actions = !this.pos_hide_actions; // true jika pos_hide_refund false
      } else {
        this.has_actions = true; // Set default value
      }
      const user_quotations = await this.env.services.orm.read(
        "res.users",
        [currentUser],
        ["pos_hide_quotations_order"],
      );
      if (user_quotations && user_quotations.length > 0) {
        this.pos_hide_quotations_order =
          user_quotations[0].pos_hide_quotations_order;
        this.has_quotations = !this.pos_hide_quotations_order; // true jika pos_hide_refund false
      } else {
        this.has_quotations = true; // Set default value
      }
    });
  },
});
