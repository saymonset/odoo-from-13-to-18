/** @odoo-module */
import { ControlButtons } from "@point_of_sale/app/screens/product_screen/control_buttons/control_buttons";
import { user } from "@web/core/user";
import { SelectPartnerButton } from "@point_of_sale/app/screens/product_screen/control_buttons/select_partner_button/select_partner_button";
import { OrderlineNoteButton } from "@point_of_sale/app/screens/product_screen/control_buttons/customer_note_button/customer_note_button";

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
        this.has_refund = !this.pos_hide_refund;
      } else {
        this.has_refund = true; // Set default value
      }
      const actionsUser = await this.env.services.orm.read(
        "res.users",
        [currentUser],
        ["pos_hide_actions"],
      );
      if (actionsUser && actionsUser.length > 0) {
        this.pos_hide_actions = actionsUser[0].pos_hide_actions;
        this.has_actions = !this.pos_hide_actions;
      } else {
        this.has_actions = true;
      }
      const user_general_note = await this.env.services.orm.read(
        "res.users",
        [currentUser],
        ["pos_hide_general_note"],
      );
      if (user_general_note && user_general_note.length > 0) {
        this.pos_hide_general_note = user_general_note[0].pos_hide_general_note;
        this.has_general_note = !this.pos_hide_general_note;
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
        this.has_customer_note = !this.pos_hide_customer_note;
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
        this.has_pricelist = !this.pos_hide_pricelist;
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
        this.has_cancel = !this.pos_hide_cancel_order;
      } else {
        this.has_cancel = true; // Set default value
      }
      const user_quote = await this.env.services.orm.read(
        "res.users",
        [currentUser],
        ["pos_hide_quot"],
      );
      if (user_quote && user_quote.length > 0) {
        this.pos_hide_quot = user_quote[0].pos_hide_quot;
        this.has_quote = !this.pos_hide_quot;
      } else {
        this.has_quote = true; // Set default value
      }
      const user_tax = await this.env.services.orm.read(
        "res.users",
        [currentUser],
        ["pos_hide_tax"],
      );
      if (user_tax && user_tax.length > 0) {
        this.pos_hide_tax = user_tax[0].pos_hide_tax;
        this.has_tax = !this.pos_hide_tax;
      } else {
        this.has_tax = true; // Set default value
      }
    });
  },
});

patch(SelectPartnerButton.prototype, {
  setup() {
    super.setup(...arguments);
    onWillStart(async () => {
      const currentUser = user.userId;
      const CustomerUser = await this.env.services.orm.read(
        "res.users",
        [currentUser],
        ["pos_hide_customer"],
      );
      if (CustomerUser && CustomerUser.length > 0) {
        this.pos_hide_customer = CustomerUser[0].pos_hide_customer;
        this.has_customer = !this.pos_hide_customer;
      } else {
        this.has_customer = true; // Set default value
      }
    });
  },
});
patch(OrderlineNoteButton.prototype, {
  setup() {
    super.setup(...arguments);
    onWillStart(async () => {
      const currentUser = user.userId;
      const OLNoteUser = await this.env.services.orm.read(
        "res.users",
        [currentUser],
        ["pos_hide_internal_note"],
      );
      if (OLNoteUser && OLNoteUser.length > 0) {
        this.pos_hide_internal_note = OLNoteUser[0].pos_hide_internal_note;
        this.has_note = !this.pos_hide_internal_note;
      } else {
        this.has_note = true; // Set default value
      }
    });
  },
});
