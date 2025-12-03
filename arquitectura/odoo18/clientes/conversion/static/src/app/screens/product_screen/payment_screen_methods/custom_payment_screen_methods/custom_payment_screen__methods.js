/** @odoo-module **/
import { _t } from "@web/core/l10n/translation";
import { Component, useState, onRendered , onWillUpdateProps, onWillStart, useRef } from "@odoo/owl";
 
 
export class CustomPaymentScreenMethods extends Component {
    static template = "conversion.CustomPaymentScreenMethods";
     // Definir las propiedades que recibirá el componente
     static components = {
       
    };
    static props = {
        //orderUuid: String,
    };

    setup() {
        super.setup();

         // Asegurarse de que cada línea de pago tenga el campo `amount_saymon`
        //  this.props.paymentLines.forEach((line) => {
        //     if (!line.amount_saymon) {
        //         line.amount_saymon = this.calculateAmountSaymon(line);
        //     }
        // });
       
        onRendered(() => {
       
        });
        

        
        onWillUpdateProps((nextProps) => {
            console.log("Props actualizadas:", nextProps);
        });  

    }
 

    calculateAmountSaymon(line) {
        // Lógica personalizada para calcular el campo en el frontend (si es necesario)
        return line.get_amount() / 60; // Ejemplo: multiplicar por 1.5
    }
    
    // Sobrescribe el método addNewPaymentLine
  
    async onClick() {
        console.log("Custom button paymentScreen.");
    
    }


}
