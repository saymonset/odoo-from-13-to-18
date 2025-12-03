/** @odoo-module **/
import { PosOrder } from "@point_of_sale/app/models/pos_order";
import { registry } from '@web/core/registry';

export class CustomOrder extends PosOrder {

    getDefaultAmountDueToPayIn() {
        if (!super.getDefaultAmountDueToPayIn) {
            console.error("getDefaultAmountDueToPayIn is not defined in the parent class");
            return 0; // Default value if the method is not defined
        }
        const originalAmount = super.getDefaultAmountDueToPayIn();
        console.log("Cantidad original:", originalAmount);

        const customAmount = originalAmount * 2;
        console.log("Cantidad personalizada:", customAmount);

        return customAmount;
    }
}

// Register the CustomOrder class in the "models" category
registry.category("models").add("order", CustomOrder);
// Verifica si la clase está registrada
const registeredOrder = registry.category("models").get("order");

