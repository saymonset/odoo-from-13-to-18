/** @odoo-module */

import { PaymentScreen } from "@point_of_sale/app/screens/payment_screen/payment_screen";
import { patch } from "@web/core/utils/patch";
import { CustomPaymentScreenMethods } from "./custom_payment_screen_methods/custom_payment_screen__methods";
patch(PaymentScreen, {
    components: {
        ...PaymentScreen.components,
        CustomPaymentScreenMethods,
    },
    setup() {
        this._super(); // Call the original setup method
    },
    });
 
