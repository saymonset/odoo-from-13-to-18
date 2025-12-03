/** @odoo-module **/

import { _t } from "@web/core/l10n/translation";
import { Component, useState, onRendered , onWillUpdateProps, onWillStart, useRef, useService } from "@odoo/owl";
import { CONFIG } from "@igtfpaymentmethod/config";
import { convertCurrency } from "@igtfpaymentmethod/currencyConverter"; // Importa la función
import { TagsList } from "@web/core/tags_list/tags_list";
//import { useService } from "@odoo/owl"; // Importar el servicio

export class CustomOrderLine extends Component {
    static template = "igtfpaymentmethod.CustomOrderLine";
     // Definir las propiedades que recibirá el componente
     static props = {
        line: Object, // Asegúrate de que la propiedad 'line' sea un objeto
    };
    static components = { TagsList };

    setup() {
        
        
        this.state = useState({ value: 1, price: 0 , currencyRate: 1, rate :1, ref:0 });
        //   // Obtener el tipo de cambio
        this.getCurrencyRate(this.props.line.currency_id).then(rate => {
            this.state.rate = rate;
         //   console.log("Currency Rate:", this.state.currencyRate);
        });

        // Obtener el tipo de cambio
        convertCurrency(1,'USD').then((ref)=>{
              this.state.ref = ref;
            });;

        onWillStart(async () => {
           // console.log('CALLED:> willStart');
           
        });    

        onRendered(() => {
            this.updatePrice(this.props.line.price);
          //  console.log('CALLED:> Render');
        });    

        onWillUpdateProps((nextProps) => {
           // console.log('CALLED:> WillUpdateProps');
            if (nextProps.line.price !== this.props.line.price) {
               // console.log("Cantidad actualizada:", nextProps.line.price);
                this.updatePrice(nextProps.line.price); // Actualiza el precio
            }
        });  
        
       

        super.setup();
    }
    // Método para actualizar el precio basado en la cantidad
    updatePrice(newPrice) {
        // Usar una expresión regular para extraer el número
        let numericPart = this.onlyNumber(newPrice);
        // Multiplicar el número por 60
        let result = numericPart / this.state.ref ;
        this.state.price = result ; // Calcula el nuevo precio basado en la cantidad y el tipo de cambio

        console.log("Nuevo precio:", this.state.price);
    }

     // Método para actualizar el precio basado en la cantidad
     onlyNumber(mountWithCurrency) {
        // Usar una expresión regular para extraer el número
        let numericPart = parseFloat(mountWithCurrency.match(/[\d.]+/)[0]);
        // Multiplicar el número por 60
       return numericPart;
    }


 

    
 
    async getCurrencyRate(currencyId) {
      
        var self = this;
        // Usar el ORM para obtener el tipo de cambio
        const result = await self.env.services.orm.searchRead('res.currency.rate', [['currency_id', '=', 1]], ['rate'], { limit: 1 });
        return result.length > 0 ? result[0].rate : 7; // Retornar el tipo de cambio o 1 si no se encuentra
    }

    increment() {
        this.state.value++;
    }

    async onClick() {
        console.log("Custom button.");
        console.log("Current line:", this.props.line); // Aquí puedes acceder a la línea actual
        this.increment();
    }


    formatWithTwoDecimals(value) {
        console.log("Valor recibido en formatWithTwoDecimals:", value);
        try {

            const number = parseFloat(value);
            if (isNaN(number)) {
                console.error("El valor no es un número válido:", value);
                return "0.00"; // Valor predeterminado
            }
        // Usar Intl.NumberFormat para formatear con dos decimales
            const formatter = new Intl.NumberFormat('en-US', {
                minimumFractionDigits: 2,
                maximumFractionDigits: 2
            });

            return formatter.format(number);
                
        } catch (error) {
            return value;
        }
        
      //  
    
    }
}
