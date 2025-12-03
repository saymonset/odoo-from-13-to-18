/** @odoo-module **/
import { _t } from "@web/core/l10n/translation";
import { Component, useState, onRendered , onWillUpdateProps, onWillStart, useRef } from "@odoo/owl";
import { TagsList } from "@web/core/tags_list/tags_list";
import { usePos } from "@point_of_sale/app/store/pos_hook";
import { TextInputPopup } from "@point_of_sale/app/utils/input_popups/text_input_popup";
import { useService } from "@web/core/utils/hooks";
import { makeAwaitable } from "@point_of_sale/app/store/make_awaitable_dialog";
export class CustomPaymentScreen extends Component {
    static template = "conversion.CustomPaymentScreen";
     // Definir las propiedades que recibirá el componente
     static props = {
    };
    static components = { TagsList };

    setup() {
        
        this.pos = usePos();
        this.dialog = useService("dialog");

        onRendered(() => {
           console.log('paymentScreen entrando.....')
        }); 
        onWillUpdateProps((nextProps) => {
            console.log("Props actualizadas:", nextProps);
        });  
        super.setup();
    }
    async onClick() {
        console.log("Custom button paymentScreen.");
        const payload = await this.openTextInput('saymon and saymon');
        console.log({payload})
    }


    async openTextInput(selectedNote) {
        let buttons = [];
        return await makeAwaitable(this.dialog, TextInputPopup, {
            title: _t("Add %s", "Bienvenido saymons"),
            buttons,
            rows: 4,
            startingValue: selectedNote,
        });
    }
}
