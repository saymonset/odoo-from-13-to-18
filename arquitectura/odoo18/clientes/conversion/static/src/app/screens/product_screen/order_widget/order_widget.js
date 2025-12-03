/** @odoo-module */
import { OrderWidget } from "@point_of_sale/app/generic_components/order_widget/order_widget";
import { patch } from "@web/core/utils/patch";
import { CustomOrderWidget } from "./custom_order_widget/custom_order_widget";
patch(OrderWidget, {
    components: {
        ...OrderWidget.components,
        CustomOrderWidget,
    },
    setup() {
        this._super(); // Call the original setup method
    },
    });
 
