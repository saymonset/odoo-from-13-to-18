/** @odoo-module **/
import { _t } from "@web/core/l10n/translation";
import { Component, useState, onRendered , onWillUpdateProps, onWillStart, useRef, useService } from "@odoo/owl";
import { TagsList } from "@web/core/tags_list/tags_list";
import { formatMonetary } from "@web/views/fields/formatters";
export class CustomOrderWidget extends Component {
    static template = "conversion.CustomOrderWidget";
     // Definir las propiedades que recibirá el componente
     static props = {
        lines: { type: Array, element: Object, optional: true },
        taxTotals: { type: Object, optional: true },
    };
    static components = { TagsList };

    setup() {
        this.formatMonetary = formatMonetary;
        this.state = useState({ totalQuantity: 14, taxTotals:this.props.taxTotals, ref:0 });
        //   // Obtener el tipo de cambio
        this.getTotalQuantity(this.props.lines);

        onRendered(() => {
            this.getTotalQuantity(this.props.lines);
            this.state.taxTotals = this.props.taxTotals;
        }); 

        this.loadLastConversion().then((ref)=>{
            this.state.ref = ref;
        });;
    
        onWillUpdateProps((nextProps) => {
            console.log("Props actualizadas:", nextProps);

            // Si `lines` cambia, recalcular la cantidad total
            if (nextProps.lines !== this.props.lines) {
                this.getTotalQuantity(nextProps.lines);
            }

            // Si `taxTotals` cambia, actualizar el estado
            if (nextProps.taxTotals !== this.props.taxTotals) {
                this.state.taxTotals = nextProps.taxTotals;
            }
        });  

        super.setup();
    }
    
    // Método para calcular la cantidad total
    getTotalQuantity(lines) {
        let totalQuantity = 0;
        lines?.forEach((line) => {
            totalQuantity += line.price;
        });
        this.state.totalQuantity = totalQuantity;
        console.log("Cantidad total calculada:", totalQuantity);
    }
    updatePrice(lines) {
        var totalQuantity = 0;
        lines?.forEach(line => this.state.totalQuantity += line.price);
        return totalQuantity
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
