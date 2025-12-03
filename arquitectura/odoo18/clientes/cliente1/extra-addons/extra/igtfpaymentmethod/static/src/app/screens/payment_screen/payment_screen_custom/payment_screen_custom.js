/** @odoo-module **/
import { _t } from "@web/core/l10n/translation";
import { Component, useState } from "@odoo/owl";

export class PaymentScreenCustom extends Component {
    static template = "igtfpaymentmethod.custom_payment_screen";
    static components = {};
    
    static props = {
        currentOrder: {
            type: Object,
            optional: true,
        },
        paymentLines: {
            type: Array, // Cambia a Array si paymentLines es un array
            optional: true,
        },
       
    };

    setup() {
      //  
        super.setup();
        
     

        onWillStart(async () => {
            
        });
        
    }

   
 
}
