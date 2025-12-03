import {patch} from "@web/core/utils/patch";
import { Orderline } from "@point_of_sale/app/generic_components/orderline/orderline";
import { CustomButton } from "./custom_button/custom_button";

// You can do this
// ControlButtons.components = {
//     ...ControlButtons.components,
//     CustomButton
// }
// Or this
patch(Orderline, {
    components: {
        ...Orderline.components,
        CustomButton,
    },
});
