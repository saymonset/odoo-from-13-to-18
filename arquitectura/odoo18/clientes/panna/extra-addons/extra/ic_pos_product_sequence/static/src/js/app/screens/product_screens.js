/** @odoo-module */

import { ProductScreen } from "@point_of_sale/app/screens/product_screen/product_screen";
import { patch } from "@web/core/utils/patch";

patch(ProductScreen.prototype, {
  get productsToDisplay() {
    const list = super.productsToDisplay;
    return list.sort((a, b) => a.sequence - b.sequence);
  },
});
