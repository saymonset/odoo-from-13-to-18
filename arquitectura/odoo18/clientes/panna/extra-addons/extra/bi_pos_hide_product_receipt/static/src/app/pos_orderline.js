import { PosOrderline } from "@point_of_sale/app/models/pos_order_line";
import { Orderline } from "@point_of_sale/app/generic_components/orderline/orderline";

import { patch } from "@web/core/utils/patch";
import { _t } from "@web/core/l10n/translation";

patch(PosOrderline.prototype, {
  setup(vals) {
    super.setup(vals);
    this.hide_product = this.get_product().hide_in_receipt;
  },

  getDisplayData() {
    return {
      ...super.getDisplayData(),
      hide_product: this.hide_product,
    };
  },
});

patch(Orderline, {
  props: {
    ...Orderline.props,
    line: {
      ...Orderline.props.line,
      shape: {
        ...Orderline.props.line.shape,
        hide_product: { type: Boolean, optional: true },
      },
    },
  },
});
