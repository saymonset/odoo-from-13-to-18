/** @odoo-module **/
import { _t } from "@web/core/l10n/translation";
import { Component, useState, onRendered, onWillUpdateProps, useRef } from "@odoo/owl";
import { CONFIG } from "@igtfpaymentmethod/config";
import {  paymentMethodManager } from "@igtfpaymentmethod/app/screens/utils";
import { convertCurrency } from "@igtfpaymentmethod/currencyConverter"; 
import { usePos } from "@point_of_sale/app/store/pos_hook";
import { useService} from "@web/core/utils/hooks"


export class PaymentLinesCustom extends Component {
    static template = "igtfpaymentmethod.payment_lines_custom";
    static components = {};
    
    static props = {
        paymentLines: {
            type: Array,
            optional: true
        },
        deleteLine: {
            type: Function,
            optional: true,
        }
    };

    setup() {
      //  
        super.setup();
        this.igtfPaymentScreenService = useService("igtfPaymentScreenService");
        
        this.pos = usePos();
        
        console.log("Current props:", this.props);
        this.payment_methods_from_config = this.pos.config.payment_method_ids
        .slice()
        .sort((a, b) => a.sequence - b.sequence);
        this.numberInputRef = useRef("numberInput");
        const hasData = this.props.paymentLines && this.props.paymentLines.length > 0;
        this.state = useState({
            result: 0,
            hasData,
            inputValue: 0,
            ref_label: CONFIG.REF_LABEL,
            selectedCurrency: "USD",
            paymentMethodName: paymentMethodManager.getPaymentMethodName(),
            is_igtf: paymentMethodManager.is_igtf,
        });

        console.log("********Payment lines recibidas:", this.props.paymentLines || []);

  
        onRendered(() => {
            if (this.props.paymentLines && this.props.paymentLines.length > 0) {
                this.updateHasData(this.props.paymentLines);
            }
            this.state.paymentMethodName = paymentMethodManager.getPaymentMethodName();
            this.state.is_igtf = paymentMethodManager.is_igtf;
        });

        onWillUpdateProps((nextProps) => {
            if (nextProps.paymentLines) {
                this.updateHasData(nextProps.paymentLines);
            } else {
                console.warn("No se recibieron nuevas líneas de pago.");
            }

            // Escuchar cambios en el nombre del método de pago
        const newPaymentMethodName = paymentMethodManager.getPaymentMethodName();
        if (newPaymentMethodName !== this.state.paymentMethodName) {
            this.state.paymentMethodName = newPaymentMethodName; // Actualiza el estado
            this.state.is_igtf = paymentMethodManager.is_igtf; // Actualiza el estado
           // this.updateLastPaymentLine(this.state.result); // Llama a updateLastPaymentLine si ha cambiado
        }
        });
    }

// Método para manejar el cambio de moneda
async onCurrencyChange(event) {
    const newCurrency = event.target.value; // Captura la moneda seleccionada
    // Actualiza el estado
    this.state.selectedCurrency = newCurrency;
    let fromCurrency =  this.state.selectedCurrency ==="USD"? "USD" :"VEF"; // Moneda de origen
 

    
   // this.calculo(this.state.inputValue, fromCurrency);
 
   
    const ref = await convertCurrency(this.state.inputValue, fromCurrency);
     this.state.result = ref; // Actualiza el resultado
     this.updateLastPaymentLine(ref);
     
}
onBlur(event){
    const inputElement = this.numberInputRef.el; // Accede al elemento del DOM
    if (inputElement) {
        inputElement.value = 0; // Inicializa el valor en 0
        this.state.inputValue = 0; // Actualiza el estado
        this.state.result = 0; // Reinicia el resultado
        console.log("El campo se ha inicializado en 0.");
    }

    //acomodar manana 2025-05-23
        const currentOrder = this.igtfPaymentScreenService.getCurrentOrder();
        this.payment_methods_from_config[0].amount = this.state.result;
        currentOrder.add_paymentline(this.payment_methods_from_config[0]);
//acomodar manana fin
}

async onInputChange(event) {
    
    const inputValue = parseFloat(event.target.value) || 0; // Captura el valor del input
    this.state.inputValue=inputValue;
    let fromCurrency =  this.state.selectedCurrency ==="USD"? "USD" :"VEF"; // Moneda de origen
 
   // this.calculo( this.state.inputValue, fromCurrency);
     // Obtener el tipo de cambio
     
    const ref =  await convertCurrency(this.state.inputValue, fromCurrency) ;
    this.state.result = ref; // Actualiza el resultado
    this.updateLastPaymentLine(ref); // Llama a updateLastPaymentLine con el nuevo valor
}
 



updateLastPaymentLine(newValue) {

    if (this.props.paymentLines && this.props.paymentLines.length > 0) {
        const lastLine = this.props.paymentLines[this.props.paymentLines.length - 1];
        
        //Secaldula el igtf
     //   
        if (this.state.is_igtf) {
          //  lastLine.amount = ((igtf / 100) * lastLine.amount ) * -1 // Update the value of the last element
        }else{
            lastLine.amount = newValue; // Update the value of the last element
        }
  
        console.log("Última línea actualizada:", lastLine);
    } else {
        console.warn("No payment lines available to update.");
    }
}
   
  // Método sobrescrito para eliminar una línea y actualizar el estado
  deleteLineWithStateUpdate(uuid) {
    console.log('Llamando a deleteLine con UUID:', uuid);

    // Verifica si deleteLine está definido antes de llamarlo
   // if (typeof this.props.deleteLine === "function") {
     //   this.props.deleteLine(uuid); // Llama al método original

        // Actualiza el estado de hasData
        const hasData = this.props.paymentLines && this.props.paymentLines.length > 0;
        this.state.hasData = hasData;
    // } else {
    //     console.error("deleteLine no está definido en las propiedades del componente.");
    // }
}
    updateHasData(paymentLines = this.props.paymentLines || []) {
        this.state.hasData = paymentLines.length > 0;
        if (!this.state.hasData) {
            this.state.result = 0;
        }
    }

 
}
