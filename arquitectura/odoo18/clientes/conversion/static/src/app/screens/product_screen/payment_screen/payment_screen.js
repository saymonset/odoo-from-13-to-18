/** @odoo-module */

import { PaymentScreen } from "@point_of_sale/app/screens/payment_screen/payment_screen";
import { patch } from "@web/core/utils/patch";
import { CustomPaymentScreen } from "./custom_payment_screen/custom_payment_screen";
patch(PaymentScreen, {
    components: {
        ...PaymentScreen.components,
        CustomPaymentScreen,
    },
    setup() {
        this._super(); // Call the original setup method
    },
    });
 
