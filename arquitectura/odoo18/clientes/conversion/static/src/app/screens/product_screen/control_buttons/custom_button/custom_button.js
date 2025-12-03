/** @odoo-module **/

import { _t } from "@web/core/l10n/translation";
import { Component, useState, onRendered , onWillUpdateProps, onWillStart, useRef, useService } from "@odoo/owl";
import { TagsList } from "@web/core/tags_list/tags_list";
//import { useService } from "@odoo/owl"; // Importar el servicio

export class CustomButton extends Component {
    static template = "conversion.CustomButton";
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

        this.loadLastConversion().then((ref)=>{
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



    async loadLastConversion() {
        var self = this;
        var resModel = 'conversion.conversion'; // Nombre del modelo
        var domain = []; // Sin filtros, para obtener todos los registros
        var fields = ['id', 'name', 'dateCurrency', 'currency_id', 'rent_amount']; // Campos que deseas recuperar
        var order = 'id desc'; // Ordenar por ID en orden descendente para obtener el último registro
        // Realizar la consulta al modelo
    const lastRecord = await self.env.services.orm.searchRead(
            resModel,
            domain,
            fields,
            { limit: 1, order: order } // Limitar a 1 registro y ordenar por ID descendente
        );
        // Verificar si se obtuvo un registro
        if (lastRecord.length > 0) {
            console.log('Último registro:', lastRecord[0]);
            return lastRecord[0].rent_amount; // Retornar el último registro
        } else {
            console.log('No se encontraron registros.');
            return null; // No hay registros
        }
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
