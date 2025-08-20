/** @odoo-module **/

import { _t } from "@web/core/l10n/translation";
import { ProductCard } from "@point_of_sale/app/generic_components/product_card/product_card";
import { usePos } from "@point_of_sale/app/store/pos_hook";
import { patch } from "@web/core/utils/patch";

patch(ProductCard.prototype, {
  setup() {
    super.setup(...arguments);
    this.pos = usePos();
  },
  getProductInfo(product) {
    if (
      this.pos.config.hide_unavailable_product &&
      !product.raw?.is_available
    ) {
      return false;
    }
    return true;
  },
});
