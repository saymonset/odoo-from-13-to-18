/** @odoo-module **/

import { registry } from "@web/core/registry";

export const igtfPaymentScreenService = {
    currentOrder: {}, // Almacena el pedido actual

    async start(env) {
        return {
            getCurrentOrder: () => this.currentOrder,
            setCurrentOrder: (order) => {
                this.currentOrder = order;
            },
        };
    }
};

registry.category("services").add("igtfPaymentScreenService", igtfPaymentScreenService);
