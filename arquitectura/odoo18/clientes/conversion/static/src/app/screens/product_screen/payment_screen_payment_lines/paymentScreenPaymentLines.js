/** @odoo-module */

import { PaymentScreenPaymentLines } from "@point_of_sale/app/screens/payment_screen/payment_lines/payment_lines";
import { patch } from "@web/core/utils/patch";
import { CustomPaymentScreenPaymentLines } from "./custom_payment_screen_payment_lines/custom_payment_screen_payment_lines";
patch(PaymentScreenPaymentLines, {
    components: {
        ...PaymentScreenPaymentLines.components,
        CustomPaymentScreenPaymentLines,
    },
    setup() {
        this._super(); // Call the original setup method
    },

    // Sobrescribe el renderizado para incluir el componente personalizado
    // render() {
    //     const originalRender = super.render();
    //     return {
    //         ...originalRender,
    //         CustomPaymentScreenPaymentLines: {
    //             component: CustomPaymentScreenPaymentLines,
    //             props: {
    //                 paymentLines: this.props.paymentLines, // Pasa las propiedades necesarias
    //             },
    //         },
    //     };
    // },

    });
 
