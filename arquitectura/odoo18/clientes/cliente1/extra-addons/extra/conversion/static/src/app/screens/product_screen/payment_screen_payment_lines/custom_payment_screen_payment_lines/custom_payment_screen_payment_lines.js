/** @odoo-module **/
import { _t } from "@web/core/l10n/translation";
import { Component, useState, onRendered , onWillUpdateProps, onWillStart, useRef } from "@odoo/owl";
 
 
export class CustomPaymentScreenPaymentLines extends Component {
    static template = "conversion.CustomPaymentScreenPaymentLines";
     // Definir las propiedades que recibirá el componente
     static components = {
       
    };
   // Define las propiedades que el componente espera recibir
   static props = {
        paymentLines: Array, // Asegúrate de que el tipo sea correcto
    };

    setup() {
        
        super.setup();
         // Estado para almacenar el resultado
         this.state = useState({
            result: 0,hasData:false, // Resultado inicial
        });

        
        
          console.log("********Payment lines recibidas:", this.props.paymentLines);

        onRendered(() => {
            this.updateHasData(this.props.paymentLines);
        });
        
        onWillUpdateProps((nextProps) => {
            console.log("******************Props actualizadas:", nextProps);
            this.updateHasData(nextProps.paymentLines);
        });  
    }

    updateHasData(paymentLines = this.props.paymentLines) {
        this.state.hasData = paymentLines && paymentLines.length > 0;
        if (!this.state.hasData){
            this.state.result = 0;
        }
    }

      // Función para manejar el evento input
    onInputChange(event) {
        const inputValue = parseFloat(event.target.value) || 0; // Captura el valor del input
        this.state.result = inputValue * 62; // Multiplica el valor por 10 y actualiza el estado
        this.updateLastPaymentLine(this.state.result); // Manually trigger the update
    }
    calculateAmountSaymon(line) {
        // Lógica personalizada para calcular el campo en el frontend (si es necesario)
        return line.get_amount() * 62; // Ejemplo: multiplicar por 1.5
    }

    updateLastPaymentLine(newValue) {
        if (this.props.paymentLines && this.props.paymentLines.length > 0) {
            const lastLine = this.props.paymentLines[this.props.paymentLines.length - 1];
            lastLine.amount = newValue; // Update the value of the last element
            console.log("Última línea actualizada:", lastLine);
        } else {
            console.warn("No payment lines available to update.");
        }
    }
    // Sobrescribe el método addNewPaymentLine
    async onClick() {
        console.log("Lineas...Custom button paymentScreen.");
    }
}
