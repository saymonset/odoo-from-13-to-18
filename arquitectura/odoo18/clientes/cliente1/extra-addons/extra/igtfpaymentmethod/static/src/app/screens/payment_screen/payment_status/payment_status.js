/** @odoo-module **/

import { patch } from '@web/core/utils/patch';
import { PaymentScreenStatus } from "@point_of_sale/app/screens/payment_screen/payment_status/payment_status";
import { _t } from "@web/core/l10n/translation";
import { PaymentStatusCustom } from "@igtfpaymentmethod/app/screens/payment_screen/payment_status/payment_status_custom/payment_status_custom";
import { usePos } from "@point_of_sale/app/store/pos_hook";

patch(PaymentScreenStatus.prototype, {
    components: {
        ...PaymentScreenStatus.components,
        PaymentStatusCustom,
    },
    setup() {
 
        this.pos = usePos();
        // Call the original setup method
        super.setup(...arguments);

        // Ensure that props are available
        this.props = this.props || {}; // Initialize props if undefined
        this.payment_methods_from_config = this.pos.config.payment_method_ids
        .slice()
        .sort((a, b) => a.sequence - b.sequence);

        console.log('------1-----------');
    },
    async addNewPaymentLine() { // Cambiar a función normal
      if (!this.props || !this.props.order) {
          console.error("Props or order is not defined");
          return;
      }
      const result = this.props.order.add_paymentline( this.payment_methods_from_config[0]);
       
  }
});
