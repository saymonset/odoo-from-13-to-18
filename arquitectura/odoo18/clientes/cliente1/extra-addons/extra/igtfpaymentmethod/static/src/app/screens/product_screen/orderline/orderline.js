import {patch} from "@web/core/utils/patch";
import { Orderline } from "@point_of_sale/app/generic_components/orderline/orderline";
import { CustomOrderLine } from "./custom_orderline/custom_orderline";

// You can do this
// ControlButtons.components = {
//     ...ControlButtons.components,
//     CustomButton
// }
// Or this
patch(Orderline, {
    components: {
        ...Orderline.components,
        CustomOrderLine: CustomOrderLine,
    },
});
