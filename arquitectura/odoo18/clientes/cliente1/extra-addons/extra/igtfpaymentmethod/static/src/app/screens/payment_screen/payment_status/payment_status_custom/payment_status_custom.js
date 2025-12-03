/** @odoo-module **/
import { _t } from "@web/core/l10n/translation";
import { Component, useState, onRendered, onWillUpdateProps, useRef } from "@odoo/owl";
import { usePos } from "@point_of_sale/app/store/pos_hook";



export class PaymentStatusCustom extends Component {
    static template = "igtfpaymentmethod.payment_status_custom";
    static components = {};
    
    static props = {
       
    };

    setup() {
      //  
      debugger
        super.setup();
        this.pos = usePos();
        
        
    } 

 
}
