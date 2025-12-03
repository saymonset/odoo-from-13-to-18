/** @odoo-module **/
import { PaymentScreenPaymentLines } from "@point_of_sale/app/screens/payment_screen/payment_lines/payment_lines";
import { patch } from "@web/core/utils/patch"; 
import { onMounted } from "@odoo/owl";
import { PaymentLinesCustom } from "@igtfpaymentmethod/app/screens/payment_screen/payment_lines/payment_lines_custom/payment_lines_custom";
patch(PaymentScreenPaymentLines, {
    components: {
        ...PaymentScreenPaymentLines.components,
           PaymentLinesCustom,
    },
    setup() {
        const self = this; // Guarda el contexto de `this`
    
        console.log("El setup de PaymentScreenPaymentLines se está ejecutando");
    
        
    
        onMounted(() => {
            console.log("El componente se ha montado");
        });
    },
  
   
});
